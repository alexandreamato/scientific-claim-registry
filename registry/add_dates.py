#!/usr/bin/env python3
"""Backfill date provenance so every claim and question has: created · updated (last) · history (a
dated log of each change). Idempotent. Run from registry/: python3 add_dates.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
QF, CF = os.path.join(HERE, "questions.json"), os.path.join(HERE, "claims.json")
REG = json.load(open(QF)).get("date", "2026-05-30")

# ---- claims: created / updated / history (a dated update log) ----
cd = json.load(open(CF))
for c in cd["claims"]:
    c.setdefault("created", REG)
    c.setdefault("updated", c["created"])
    if not c.get("history"):
        hist = [{"date": c["created"], "event": "created"}]
        for p in c.get("provenance_log", []):          # migrate legacy corroboration log
            hist.append({"date": p.get("date", c["updated"]), "event": p.get("action", "updated"),
                         "detail": p.get("ref")})
        if c["updated"] != c["created"] and not any(h["date"] == c["updated"] for h in hist):
            hist.append({"date": c["updated"], "event": "updated"})
        c["history"] = hist
    c.pop("provenance_log", None)
    c["updated"] = c["history"][-1]["date"]            # keep last-updated in sync with the log
json.dump(cd, open(CF, "w"), ensure_ascii=False, indent=2)

# ---- questions: created (earliest version) / updated (latest) ----
qd = json.load(open(QF))
for q in qd["questions"]:
    dates = [h["date"] for h in (q.get("history") or []) if h.get("date")]
    q.setdefault("created", min(dates) if dates else REG)
    q["updated"] = q.get("updated") or (max(dates) if dates else REG)
json.dump(qd, open(QF, "w"), ensure_ascii=False, indent=2)

print(f"Dates backfilled: {len(cd['claims'])} claims, {len(qd['questions'])} questions "
      "(created · updated · history on each).")
