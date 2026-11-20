#!/usr/bin/env python3
"""Agent-mode twin of `loop.py --recompile-only` (no API spend): the same compiler prompt is written to a file,
a Claude Code subagent writes the JSON answer, and this script applies it exactly as loop.py would.
  python3 recompile_agent.py prep QID [QID...]       → consolidation/work/QID.answer_prompt.md
  python3 recompile_agent.py apply QID FILE.json [model_label]   (writes questions.json + db.sync)"""
import json, os, sys
import loop, db

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "consolidation", "work")
NEED = ("current_answer", "current_answer_pt", "bottom_line", "bottom_line_pt", "major_uncertainty",
        "major_uncertainty_pt", "outcomes")


def load():
    qd, cd = json.load(open(loop.QJSON)), json.load(open(loop.CJSON))
    return qd, {c["id"]: c for c in cd["claims"]}


def prep(qid):
    qd, by_id = load()
    q = next(x for x in qd["questions"] if x["id"] == qid)
    base = [loop.claim_brief(by_id.get(l["id"], {}), l["role"]) for l in q["claims"]]
    n = sum(len(c["evidence"]) for c in base)
    user = (f'QUESTION ({q["id"]}): {q["text"]}\n\nPRIOR ANSWER: {q.get("current_answer", "")}\n\n'
            'NEWLY ADDED this update:\n- (context) The claim set was restructured: single-paper claims were '
            'consolidated into general propositions, each backed by several study-level findings (R-CLM-19). '
            'No new papers were added; recompile the answer from the propositions and their findings.\n\n'
            f'FULL ACCUMULATED EVIDENCE BASE ({len(base)} claims, {n} articles — compile from ALL of it):\n'
            + json.dumps(base, ensure_ascii=False) + "\n\n"
            'Return JSON with keys: current_answer, current_answer_pt, bottom_line (2 plain sentences: '
            'what the evidence supports + what it does not / remains uncertain), bottom_line_pt, '
            'major_uncertainty, major_uncertainty_pt, what_changed (one sentence describing what THIS update '
            'changed relative to the prior answer), what_changed_pt, AND outcomes — an array (may be empty for '
            'non-efficacy questions) of {outcome (short label EN), outcome_pt, direction (one of: improved | '
            'reduced | increased | no_effect | not_demonstrated | mixed), confidence (GRADE: high|moderate|low|'
            'very_low), disease_modifying (boolean), note (≤120 chars, EN), note_pt}. Every *_pt field MUST be '
            'Brazilian Portuguese, never Spanish.')
    os.makedirs(WORK, exist_ok=True)
    p = os.path.join(WORK, f"{qid}.answer_prompt.md")
    open(p, "w").write(f"# SYSTEM\n\n{loop.SYS_COMPILE}\n\n# INPUT\n\n{user}\n")
    print(p)


def apply(qid, path, model="claude-code-subagent"):
    rc = json.load(open(path))
    miss = [k for k in NEED if k not in rc]
    if miss:
        sys.exit(f"{qid}: missing keys {miss}")
    qd, _ = load()
    q = next(x for x in qd["questions"] if x["id"] == qid)
    for k in NEED:
        q[k] = rc[k]
    q["version"] = loop.bump(q.get("version", "1.0")); q["updated"] = loop.TODAY
    q["compiled_by"] = {"model": model, "mode": "agent", "date": loop.TODAY}
    q.setdefault("history", []).insert(0, {"version": q["version"], "date": loop.TODAY,
        "change": rc.get("what_changed") or "Answer recompiled after claim consolidation (R-CLM-19).",
        "change_pt": rc.get("what_changed_pt") or "Resposta recompilada após a consolidação dos claims (R-CLM-19).",
        "engine": model})
    json.dump(qd, open(loop.QJSON, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)
    print(f"{qid} → v{q['version']}: {q['current_answer'][:160]}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        for x in sys.argv[2:]:
            prep(x)
    elif cmd == "apply":
        apply(*sys.argv[2:])
