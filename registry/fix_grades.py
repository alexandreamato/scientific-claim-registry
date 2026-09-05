#!/usr/bin/env python3
"""Cap each evidence grade by its STUDY DESIGN (audit 2026-06; extends R-CLM-13 to design).
A weak design can't carry a high grade: case_report→very_low, case_series→low, basic_science→low,
review→low, narrative_review→very_low, expert_opinion→very_low, cohort→moderate. Only LOWERS.
Writes claims.json + db.sync, and prints the questions to recompile.
  python3 fix_grades.py            # report
  python3 fix_grades.py --fix      # apply"""
import json, os, sys
import db

HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.join(HERE, "claims.json")
QF = os.path.join(HERE, "questions.json")
FIX = "--fix" in sys.argv

RANK = {"very_low": 0, "low": 1, "moderate": 2, "high": 3}
DESIGN_MAX = {"case_report": "very_low", "case_series": "low", "basic_science": "low",
              "review": "moderate", "narrative_review": "very_low", "expert_opinion": "very_low",
              "cohort": "moderate"}


def main():
    data = json.load(open(CF))
    touched = set(); n = 0
    for c in data["claims"]:
        worst = 0
        for ev in c.get("evidence", []):
            d = (ev.get("study_design") or "").lower(); g = ev.get("grade")
            ceil = DESIGN_MAX.get(d)
            if ceil and g in RANK and RANK[g] > RANK[ceil]:
                if FIX:
                    ev["grade"] = ceil
                    ev.setdefault("_prov", {})["grade_source"] = "design_cap"
                n += 1; touched.add(c["id"])
            worst = max(worst, RANK.get(ev.get("grade"), 0))
        # keep claim-level confidence no higher than its best (now-capped) evidence
        ec = c.get("evidence_confidence")
        if ec in RANK and RANK[ec] > worst and c.get("evidence"):
            if FIX:
                c["evidence_confidence"] = [k for k, v in RANK.items() if v == worst][0]
            touched.add(c["id"])
    print(f"{'capped' if FIX else 'would cap'} {n} evidence grade(s) across {len(touched)} claim(s)")
    if FIX and touched:
        json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)
        db.sync(verbose=False)
        qd = json.load(open(QF))
        qs = sorted({q["id"] for q in qd["questions"]
                     for cl in q.get("claims", []) if (cl["id"] if isinstance(cl, dict) else cl) in touched})
        print("recompile:", " ".join(qs))


if __name__ == "__main__":
    main()
