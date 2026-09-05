#!/usr/bin/env python3
"""Backfill R-Q-5 phrasings on every existing question (bilingual, via Opus).
Idempotent: skips questions that already have phrasings unless --force.
  python3 add_phrasings.py [--force] [SQ-LIP-000007 ...]"""
import json, os, sys
import phrasings
import db

HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if a.startswith("SQ-")]


def main():
    data = json.load(open(QF)); n = 0
    for q in data["questions"]:
        if ONLY and q["id"] not in ONLY:
            continue
        if q.get("phrasings") and not FORCE:
            continue
        g = phrasings.gen_phrasings(q.get("text", ""), q.get("text_pt", ""))
        if not g["phrasings"]:
            print(f"  {q['id']}  (no phrasings generated)"); continue
        q["phrasings"] = g["phrasings"]
        q["phrasings_pt"] = g["phrasings_pt"]
        n += 1
        print(f"  {q['id']}  +{len(g['phrasings'])} EN / +{len(g['phrasings_pt'])} PT")
        for p in g["phrasings"]:
            print(f"        · {p}")
    json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
    if n:
        db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
    print(f"Done. {n} question(s) got phrasings. DB synced.")


if __name__ == "__main__":
    main()
