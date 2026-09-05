#!/usr/bin/env python3
"""Language-leak guard (R-SITE-16). Heuristic detector that flags text fields written in the WRONG
language — a `*_pt` field that is actually English or Spanish, or an English base field that is
actually Portuguese/Spanish. Pure stdlib, no LLM. Catches AI-generation drift (a backfill that came
out in Spanish, a `what_changed_pt` that escaped to English) before it ships.

Run from registry/:
  python3 lang_check.py            # report leaks; exit 1 if any (use in cron/CI)
  python3 lang_check.py --verbose  # also print a one-line excerpt per leak

Scans questions.json + claims.json: every base (EN) and `*_pt` field, including phrasings,
outcomes, version history, and evidence notes.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERBOSE = "--verbose" in sys.argv

PT_CHARS = re.compile(r"[ãõçâêô]")
PT_W = set("não são também já há está estão evidências com dos das uma é às após porém contudo "
           "qualidade reduzir aumentar mulheres doença gordura tratamento segundo sobre forma".split())
ES_W = set("la los las el y evidencia muestra muestran mujeres enfermedad grasa tratamiento según "
           "también aunque hacia sólo ningún investigación reducción aún reportó aproximadamente personas".split())
EN_W = set("the and of is are was with that for this not evidence shows show suggest remains while "
           "between disease women fat treatment quality reduce increase added several including".split())

def words(t):
    return re.findall(r"[a-záéíóúâêôãõçñü]+", (t or "").lower())

def leak(t, expected):
    """Return a short reason string if `t` is NOT in the expected language ('en'|'pt'), else None."""
    ws = words(t)
    if len(ws) < 5:           # too short to judge reliably
        return None
    pt = len(PT_CHARS.findall(t or "")) + sum(1 for w in ws if w in PT_W)
    es = sum(1 for w in ws if w in ES_W)
    en = sum(1 for w in ws if w in EN_W)
    if expected == "pt":
        if es >= 3 and es > pt:        return f"Spanish (es{es}/pt{pt})"
        if en >= 3 and pt == 0 and es < 2: return f"English (en{en}/pt{pt})"
    else:  # expected English
        if pt >= 3 and pt > en:        return f"Portuguese (pt{pt}/en{en})"
        if es >= 4 and es > en:        return f"Spanish (es{es}/en{en})"
    return None

def scan():
    flags = []
    def chk(oid, field, text, expected):
        r = leak(text, expected)
        if r:
            flags.append((oid, field, r, (text or "")[:90]))

    qs = json.load(open(os.path.join(HERE, "questions.json")))["questions"]
    for q in qs:
        for b in ("text", "current_answer", "major_uncertainty", "bottom_line"):
            chk(q["id"], b, q.get(b), "en")
            chk(q["id"], b + "_pt", q.get(b + "_pt"), "pt")
        for p in (q.get("phrasings") or []):    chk(q["id"], "phrasing", p, "en")
        for p in (q.get("phrasings_pt") or []): chk(q["id"], "phrasing_pt", p, "pt")
        for o in (q.get("outcomes") or []):
            chk(q["id"], "outcome", o.get("outcome"), "en")
            chk(q["id"], "outcome_pt", o.get("outcome_pt"), "pt")
            chk(q["id"], "outcome.note", o.get("note"), "en")
            chk(q["id"], "outcome.note_pt", o.get("note_pt"), "pt")
        for h in (q.get("history") or []):
            chk(q["id"], "history.change", h.get("change"), "en")
            chk(q["id"], "history.change_pt", h.get("change_pt"), "pt")

    cs = json.load(open(os.path.join(HERE, "claims.json")))["claims"]
    for c in cs:
        chk(c["id"], "statement", c.get("statement"), "en")
        chk(c["id"], "statement_pt", c.get("statement_pt"), "pt")
        chk(c["id"], "gaps", c.get("gaps"), "en")
        for e in c.get("evidence", []):
            chk(c["id"], "evidence.note", e.get("note"), "en")
    return flags

def main():
    flags = scan()
    if flags:
        print(f"✗ LANG GUARD: {len(flags)} field(s) in the wrong language (R-SITE-16):")
        for oid, field, reason, excerpt in flags[:40]:
            print(f"    {oid} · {field} → {reason}")
            if VERBOSE:
                print(f"        {excerpt}")
        print("  → fix the field(s) above (regenerate or translate), then rebuild.")
        sys.exit(1)
    print("✓ LANG GUARD: every text field is in its expected language (R-SITE-16).")

if __name__ == "__main__":
    main()
