#!/usr/bin/env python3
"""Backfill a 2-sentence plain-language `bottom_line` (+ `bottom_line_pt`) onto each question
(R-SITE-14), derived from the already-compiled answer + outcomes + major uncertainty — cheap, no
re-litigation of the full compilation. Going forward the loop's compiler emits it directly. Idempotent
(skips questions that already have a bottom_line unless --force). Run from registry/:
  python3 bottom_line.py [--force] [SQ-LIP-000003 ...]
Use a cheap model via env, e.g.  SCR_LLM_MODEL=anthropic/claude-sonnet-4.6 python3 bottom_line.py
"""
import json, os, sys
import ingest, db

HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if a.startswith("SQ-")]

SYS = ("You write the BOTTOM LINE for a scientific question in an evidence registry that REGISTERS, does "
       "not arbitrate. Given the question, its current evidence-bounded answer, its per-outcome breakdown, "
       "and its major uncertainty, produce a 2-sentence plain-language takeaway: sentence 1 = what the "
       "evidence DOES support; sentence 2 = what it does NOT support or what remains uncertain. No jargon, "
       "no 'Based on currently indexed evidence' preamble, readable in 10 seconds, never overstate, never "
       "give a clinical recommendation. `bottom_line` MUST be English; `bottom_line_pt` MUST be Brazilian "
       "Portuguese (português do Brasil) — NEVER Spanish (e.g. 'evidência' not 'evidencia', 'o lipedema' not "
       "'la lipedema', 'e' not 'y', 'mulheres' not 'mujeres'). "
       "Return STRICT JSON {\"bottom_line\": \"...\", \"bottom_line_pt\": \"...\"}.")

def make(q):
    user = (f'QUESTION: {q["text"]}\n\n'
            f'CURRENT ANSWER: {q.get("current_answer","")}\n\n'
            f'OUTCOMES: {json.dumps(q.get("outcomes") or [], ensure_ascii=False)}\n\n'
            f'MAJOR UNCERTAINTY: {q.get("major_uncertainty","")}')
    r = ingest._chat_json(SYS, user)
    return (r.get("bottom_line") or "").strip(), (r.get("bottom_line_pt") or "").strip()

def main():
    if not ingest.provider():
        sys.exit("no LLM provider configured")
    data = json.load(open(QF))
    done = 0
    for q in data["questions"]:
        if ONLY and q["id"] not in ONLY:
            continue
        if q.get("bottom_line") and not FORCE:
            continue
        try:
            bl, bl_pt = make(q)
        except Exception as e:
            print(f"  ✗ {q['id']}: {e}"); continue
        if bl:
            q["bottom_line"] = bl
            if bl_pt:
                q["bottom_line_pt"] = bl_pt
            done += 1
            print(f"  ✓ {q['id']}: {bl[:90]}")
            if done % 10 == 0:
                json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
    json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)  # R-DATA-1
    print(f"Done. {done} bottom_line(s) written + DB synced.")

if __name__ == "__main__":
    main()
