#!/usr/bin/env python3
"""Quality audit — guarantees the SCR-LIP-000221 (Viana) pathology does not recur.

It cross-checks every claim's evidence grade against the AUTHORITATIVE human-curated grade
in the author's library (`bib`, field `grau`, Oxford CEBM level N1..N6). When the registry
grade is HIGHER than the curated grade allows, the evidence is OVER-GRADED — a weak paper
masquerading as strong, which inflates the compiled answer (violating R-CLM-11). It also
flags evidence with NO grade at all (the quality weighting can't act on it).

  python3 audit_quality.py            # report only (read-only)
  python3 audit_quality.py --fix      # cap each grade at the bib-curated ceiling; fill missing
  python3 audit_quality.py --fix --commit   # (alias; --fix already writes)

`--fix` only ever LOWERS a grade to the curated ceiling or FILLS a missing one — it never
raises a grade. Edited evidence is marked provenance.grade_source='bib_curated'. After --fix:
rebuild + redeploy + recompile the touched questions.
Heuristic fallback (no bib match): a weak study type (narrative review / opinion / case /
animal / in vitro / preprint) marked high|moderate is flagged but NOT auto-changed."""
import json, os, sys, collections
import ingest
import db

HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.join(HERE, "claims.json")
FIX = "--fix" in sys.argv

# Oxford CEBM level (bib `grau`, N1=best .. N6=mechanism/opinion) -> GRADE ceiling.
GRADE_RANK = {"very_low": 0, "low": 1, "moderate": 2, "high": 3}
N_TO_GRADE = {"N1": "high", "N2": "high", "N3": "moderate",
              "N4": "low", "N5": "low", "N6": "very_low"}
WEAK_TYPE = ("narrative", "opinion", "editorial", "expert", "preprint",
             "animal", "in vitro", "in_vitro", "ex vivo", "case report", "case_report")


def ceiling_from_grau(grau):
    if not grau:
        return None
    g = str(grau).strip().upper().replace(" ", "")
    return N_TO_GRADE.get(g)


def main():
    data = json.load(open(CF))
    over, missing, heuristic = [], [], []
    fixed = 0
    touched_claims = set()
    bib_ok = ingest.bib_available()
    if not bib_ok:
        print("⚠ bib API DOWN — só auditoria heurística (sem o grau curado). Suba `bib serve`.\n")

    for c in data["claims"]:
        for ev in c.get("evidence", []):
            raw = (ev.get("doi") or ev.get("ref") or "")
            doi = raw.split("DOI:")[-1].strip() if "DOI:" in raw.upper() or "10." in raw else ""
            if "PMID:" in raw.upper() and "10." not in raw:
                doi = ""  # PMID-only ref; bib_by_doi won't help
            reg = (ev.get("grade") or "").strip().lower() or None
            dl = (ev.get("study_design") or "").lower()
            ceil = None
            grau = tipo = None
            if bib_ok and doi:
                f = ingest.bib_by_doi(doi) or {}
                grau = f.get("grau")
                tipo = f.get("tipo_estudo")
                ceil = ceiling_from_grau(grau)

            # 1) OVER-GRADED vs curated ceiling
            if ceil and reg and GRADE_RANK.get(reg, 9) > GRADE_RANK[ceil]:
                over.append((c["id"], doi, reg, ceil, grau, (tipo or "")[:50]))
                if FIX:
                    ev["grade"] = ceil
                    ev.setdefault("note", "")
                    ev["note"] = (ev["note"] + f" [grade capped {reg}->{ceil} per curated Oxford {grau}]").strip()
                    ev.setdefault("_prov", {})["grade_source"] = "bib_curated"
                    fixed += 1
                    touched_claims.add(c["id"])
            # 2) MISSING grade but bib knows it -> fill
            elif ceil and not reg:
                missing.append((c["id"], doi, ceil, grau))
                if FIX:
                    ev["grade"] = ceil
                    ev.setdefault("_prov", {})["grade_source"] = "bib_curated"
                    fixed += 1
                    touched_claims.add(c["id"])
            # 3) heuristic flag (no bib match): weak type marked strong
            elif not ceil and reg in ("high", "moderate") and any(k in dl for k in WEAK_TYPE):
                heuristic.append((c["id"], doi or ev.get("ref", ""), reg, dl))

    print(f"=== OVER-GRADED vs grau curado do bib ===  ({len(over)})")
    for o in over:
        print(f"  {o[0]}  {o[1]:30} reg={o[2]:9}-> teto={o[3]:9} (grau {o[4]}) {o[5]}")
    print(f"\n=== SEM grade, mas bib sabe ===  ({len(missing)})")
    for m in missing:
        print(f"  {m[0]}  {m[1]:30} fill={m[2]} (grau {m[3]})")
    print(f"\n=== heurístico (fora da biblioteca): tipo fraco marcado high/moderate ===  ({len(heuristic)})")
    for h in heuristic:
        print(f"  {h[0]}  {h[1]:30} {h[2]:9} {h[3]}")

    if FIX and fixed:
        json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)
        db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
        print(f"\n✓ {fixed} grade(s) corrigido(s) + DB sincronizado. Perguntas a recompilar:")
        # map claims -> questions
        qd = json.load(open(os.path.join(HERE, "questions.json")))
        for q in qd["questions"]:
            ids = {(cl["id"] if isinstance(cl, dict) else cl) for cl in q.get("claims", [])}
            if ids & touched_claims:
                print(f"    {q['id']}  (loop.py {q['id']} --recompile-only --commit)")
    elif FIX:
        print("\n(nada a corrigir)")
    else:
        print("\n(read-only — rode com --fix para aplicar o teto curado)")


if __name__ == "__main__":
    main()
