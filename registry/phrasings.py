#!/usr/bin/env python3
"""R-Q-5 — canonical question + alternative phrasings.

A scientific question (SQ) is the central, stable, neutral object. Humans and agents ask it
in many ways. Instead of duplicating near-identical questions, we keep ONE canonical `text`
(+`text_pt`) and a list of `phrasings` (+`phrasings_pt`): alternative natural-language ways to
ask the SAME question (the same answer satisfies all of them). This:
  • prevents semantic duplicates (a paraphrase becomes a phrasing, not a new SQ),
  • widens site search recall (search matches phrasings) with no new pages,
  • powers machine-first routing (resolve any phrasing → the canonical SQ).

Two reusable pieces, both LLM-backed (conservative, mirroring the claim-merge philosophy):
  gen_phrasings(text, text_pt, n) -> {"phrasings":[...], "phrasings_pt":[...]}
  judge_same(proposed_text, existing) -> {"verdict": same|related|novel, "sq_id", "confidence", "reason"}
"""
import json
import ingest

# Auto-merge only on HIGH confidence that it is the same question (else create a new SQ).
SAME_THRESHOLD = 0.85

SYS_GEN = (
    "You generate alternative PHRASINGS of a single scientific question for a question-centric "
    "evidence registry. A phrasing is a different natural-language way to ask the SAME question — "
    "such that ONE answer would satisfy all of them. Keep the exact same scope, population, and "
    "intent: do NOT broaden, narrow, or shift the question. Mix registers: a lay/patient way, a "
    "clinical way, a short search-style query. No yes/no leading bias beyond the original.\n"
    "Return STRICT JSON: {\"phrasings\":[3-4 English strings], \"phrasings_pt\":[the same count, "
    "Brazilian Portuguese]}. Phrasings must differ in wording from the canonical text and from each "
    "other. No numbering, no quotes inside strings."
)

SYS_JUDGE = (
    "You are a CONSERVATIVE deduplicator for a scientific question registry. Given a PROPOSED "
    "question and a list of EXISTING questions (each with its canonical text and known phrasings), "
    "decide the relationship to the closest existing question:\n"
    "  • \"same\"   — it is the SAME question, just phrased differently (one answer satisfies both; "
    "identical scope/population/intent). This is a PARAPHRASE.\n"
    "  • \"related\" — clearly about the same topic but a DISTINCT question (different scope, outcome, "
    "or sub-aspect → would need its own answer).\n"
    "  • \"novel\"  — not matching any existing question.\n"
    "Be strict: choose \"same\" ONLY when you are highly confident the answers are interchangeable. "
    "When unsure between same and related, choose \"related\". Never collapse distinct questions.\n"
    "Return STRICT JSON: {\"verdict\":\"same|related|novel\", \"sq_id\":\"SQ-… or null\", "
    "\"confidence\":0.0-1.0, \"reason\":\"one sentence\"}."
)


def gen_phrasings(text, text_pt="", n=4):
    user = (f"Canonical question (EN): {text}\n"
            f"Canonical question (PT): {text_pt or '(translate from EN)'}\n"
            f"Generate {n} alternative phrasings in EN and the same {n} in PT-BR.")
    try:
        out = ingest._chat_json(SYS_GEN, user)
    except Exception as ex:
        print(f"  [gen_phrasings error: {ex}]"); return {"phrasings": [], "phrasings_pt": []}
    ph = [s.strip() for s in (out.get("phrasings") or []) if isinstance(s, str) and s.strip()]
    pp = [s.strip() for s in (out.get("phrasings_pt") or []) if isinstance(s, str) and s.strip()]
    # never echo the canonical text back as a phrasing
    low = {text.strip().lower(), (text_pt or "").strip().lower()}
    ph = [s for s in ph if s.lower() not in low]
    pp = [s for s in pp if s.lower() not in low]
    return {"phrasings": ph, "phrasings_pt": pp}


def judge_same(proposed_text, existing):
    """existing = [{"id","text","phrasings":[...]}]. Returns the verdict dict (conservative)."""
    catalog = [{"sq_id": q["id"], "text": q.get("text", ""),
                "phrasings": (q.get("phrasings") or [])} for q in existing]
    user = ("PROPOSED question:\n  " + proposed_text + "\n\nEXISTING questions (canonical + phrasings):\n"
            + json.dumps(catalog, ensure_ascii=False, indent=1))
    try:
        v = ingest._chat_json(SYS_JUDGE, user)
    except Exception as ex:
        print(f"  [judge_same error: {ex}]"); return {"verdict": "novel", "sq_id": None, "confidence": 0.0}
    v["verdict"] = (v.get("verdict") or "novel").lower()
    try:
        v["confidence"] = float(v.get("confidence") or 0.0)
    except (TypeError, ValueError):
        v["confidence"] = 0.0
    return v


def is_auto_merge(verdict):
    return verdict.get("verdict") == "same" and verdict.get("confidence", 0) >= SAME_THRESHOLD \
        and verdict.get("sq_id")


def add_phrasing_to_question(q, text, text_pt=""):
    """Append a phrasing to a question dict (dedup-safe, case-insensitive)."""
    ph = q.setdefault("phrasings", []); pp = q.setdefault("phrasings_pt", [])
    seen = {s.lower() for s in ph} | {q.get("text", "").lower()}
    if text and text.lower() not in seen:
        ph.append(text)
    seenp = {s.lower() for s in pp} | {q.get("text_pt", "").lower()}
    if text_pt and text_pt.lower() not in seenp:
        pp.append(text_pt)
