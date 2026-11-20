#!/usr/bin/env python3
"""Attach one paper's study-level findings to general propositions (R-CLM-19), with no API spend.

The staged file (written in a session; checked by an independent verifier subagent) holds the paper's metadata,
optionally new propositions, and one row per placement:
  {"paper": {ref, title, authors, year, study_design, n, risk_of_bias, grade, translation_ref?, journal?},
   "new_propositions": [{"key": "NEW", "qid", "role", "statement", "statement_pt", "claim_type"?}],
   "rows": [{"target": "SCR-LIP-…|NEW", "qid", "stance", "quote", "quote_location"?, "finding", "note"?,
             "verification": {...}}]}
Guards: the DOI must resolve (loop.verify_ref); the grade is capped by the library grade (R-CLM-13); a proposition
≤25 words without numbers (consolidate.NUMBER); a paper already under a target is not added twice; only rows whose
verification verdict is "verified" are written. A new proposition is linked to its question. The proposition's
grade follows R-CLM-11 (best supporting grade, one level down if contradicted by equal or higher certainty).
  python3 attach_findings.py STAGED.json [--commit]        (without --commit: dry run)"""
import json, os, sys, datetime, collections
import loop, db
from consolidate import NUMBER

TODAY = datetime.date.today().isoformat()
GR = ["very_low", "low", "moderate", "high"]


def norm(r):
    return (r or "").strip().lower()


def prop_grade(ev):
    sup = [GR.index(e["grade"]) for e in ev if e.get("stance") == "supporting" and e.get("grade") in GR
           and not e.get("secondary_of")]
    con = [GR.index(e["grade"]) for e in ev if e.get("stance") == "contradicting" and e.get("grade") in GR]
    if not sup:
        return None
    g = max(sup)
    if con and max(con) >= g:
        g = max(g - 1, 0)
    return GR[g]


def main():
    path = sys.argv[1]; commit = "--commit" in sys.argv
    st = json.load(open(path)); P = st["paper"]
    cd, qd = json.load(open(loop.CJSON)), json.load(open(loop.QJSON))
    C = {c["id"]: c for c in cd["claims"]}; Q = {q["id"]: q for q in qd["questions"]}
    doi = P["ref"].split(":", 1)[1] if P["ref"].upper().startswith("DOI:") else None
    if doi and not loop.verify_ref(doi, None):
        sys.exit(f"{P['ref']} does not resolve")
    seq = max(int(c["id"].split("-")[-1]) for c in cd["claims"])
    newmap = {}
    for np_ in st.get("new_propositions", []):
        s = np_["statement"]
        if len(s.split()) > 25 or NUMBER.search(s):
            sys.exit(f"proposition fails R-CLM-19 format: {s}")
        seq += 1; cid = f"SCR-LIP-{seq:06d}"
        C[cid] = {"id": cid, "statement": s, "statement_pt": np_.get("statement_pt", ""),
                  "claim_type": np_.get("claim_type", "epidemiological"), "context": np_.get("context", {}),
                  "knowledge_state": "emerging", "evidence_confidence": P.get("grade", "very_low"),
                  "evidence": [], "relations": [], "gaps": "", "curators": [], "created": TODAY, "updated": TODAY,
                  "license": "CC-BY-4.0", "consolidated_from": [], "questions_consolidated": [np_["qid"]],
                  "provenance": {"method": "attach_findings (R-CLM-19)", "source": P["ref"]},
                  "history": [{"date": TODAY, "event": "created",
                               "detail": f"general proposition created for {P['ref']} under {np_['qid']}"}]}
        cd["claims"].append(C[cid]); newmap[np_["key"]] = cid
        Q[np_["qid"]]["claims"].append({"id": cid, "role": np_["role"]})
        print(f"new {cid} ({np_['qid']}, {np_['role']}): {s}")
    touched = collections.defaultdict(set)
    for r in st["rows"]:
        cid = newmap.get(r["target"], r["target"]); c = C[cid]
        v = r.get("verification") or {}
        if v.get("verdict") != "verified":
            print(f"skip {cid}: verification {v.get('verdict')}"); continue
        if norm(P["ref"]) in {norm(e.get("ref")) for e in c["evidence"]}:
            print(f"skip {cid}: {P['ref']} already there"); continue
        art = {"doi": doi, "year": P.get("year"), "title": P.get("title")}
        g = loop.design_cap(loop.cap_grade(P.get("grade", "low"), art), P.get("study_design"))
        ev = {"ref": P["ref"], "stance": r["stance"], "study_design": P.get("study_design"), "n": P.get("n"),
              "risk_of_bias": P.get("risk_of_bias"), "year": P.get("year"), "title": P.get("title"),
              "authors": P.get("authors"), "grade": g, "_prov": {"grade_source": "bib_curated"},
              "quote": r["quote"], "finding": r["finding"], "extraction_confidence": "high",
              "verification": v, "added": TODAY}
        for k in ("quote_location", "note"):
            if r.get(k):
                ev[k] = r[k]
        if P.get("translation_ref"):
            ev["translation_ref"] = P["translation_ref"]
        if P.get("amato_authored") or "amato" in norm(P.get("authors")).split(",")[0]:
            ev["amato_authored"] = True
        c["evidence"].append(ev)
        ng = prop_grade(c["evidence"])
        if ng and ng != c.get("evidence_confidence"):
            print(f"  {cid} grade {c.get('evidence_confidence')} → {ng}"); c["evidence_confidence"] = ng
        c["updated"] = TODAY
        c.setdefault("history", []).append({"date": TODAY, "event": "evidence added",
                                            "detail": f"finding from {P['ref']} ({r['stance']})"})
        touched[r["qid"]].add(cid)
        print(f"+ {cid} ← {P['ref']} [{r['stance']}] {r['finding'][:110]}")
    for qid in touched:
        Q[qid]["updated"] = TODAY
    if not commit:
        print("(dry run — add --commit to write)"); return
    cd["count"] = len(cd["claims"]); cd["date"] = TODAY
    json.dump(cd, open(loop.CJSON, "w"), ensure_ascii=False, indent=2)
    json.dump(qd, open(loop.QJSON, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)
    print(f"✓ written + DB synced; recompile: {', '.join(sorted(touched))}")


if __name__ == "__main__":
    main()
