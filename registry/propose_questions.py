#!/usr/bin/env python3
"""QUESTION-CREATION STRATEGY (the missing half of the loop). Three jobs:
  1. COVERAGE   — map existing questions onto the topic axes (tags); show gaps.
  2. DISCOVERY  — an LLM proposes NEW neutral questions in the gaps, each GROUNDED against the
                  author's library (bib semantic) so they are literature-driven, not invented.
  3. LIFECYCLE  — proposals get a TEMP id (SQ-LIP-D######); a curator promotes / rejects them.

Run from registry/:
  python3 propose_questions.py                 # coverage report + propose → proposed_questions.json
  python3 propose_questions.py list
  python3 propose_questions.py promote SQ-LIP-D000001   # → final SQ-LIP-###### in questions.json (claims:[])
  python3 propose_questions.py reject  SQ-LIP-D000001
Then run loop.py on the promoted question to populate its claims.
"""
import json, os, sys, datetime, re
import ingest
import phrasings
import db
HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
PF = os.path.join(HERE, "proposed_questions.json")
TODAY = datetime.date.today().isoformat()

AXES = ["Definition", "Epidemiology", "Diagnosis", "Screening", "Imaging", "Etiology", "Genetics",
        "Hormones", "Pathophysiology", "Metabolism", "Pain", "Comorbidities", "Mental health",
        "Treatment", "Surgery", "Diet", "Pharmacology", "Management", "Progression", "Complications",
        "Vascular", "History"]

def load_q(): return json.load(open(QF))
def load_p():
    return json.load(open(PF)) if os.path.exists(PF) else {"proposed": []}
def save_p(p): json.dump(p, open(PF, "w"), ensure_ascii=False, indent=2)

def coverage():
    qs = load_q()["questions"]
    tally = {a: 0 for a in AXES}
    for q in qs:
        for t in q.get("tags", []):
            tally[t] = tally.get(t, 0) + 1
    print("=== COVERAGE (existing questions per axis) ===")
    for a in AXES:
        bar = "█" * tally.get(a, 0)
        flag = "  ← GAP" if tally.get(a, 0) == 0 else ("  ← thin" if tally.get(a, 0) == 1 else "")
        print(f"  {a:16s} {tally.get(a,0):2d} {bar}{flag}")
    gaps = [a for a in AXES if tally.get(a, 0) == 0]
    print(f"\n  {len(qs)} questions · {len([a for a in AXES if tally.get(a,0)])}/{len(AXES)} axes covered · gaps: {gaps or 'none'}")
    return tally, gaps

SYS_PROPOSE = ("You design the QUESTION SPACE of a scientific claim registry for a disease. Propose NEW "
    "scientific questions that (a) are NOT already covered by the existing questions, (b) are NEUTRAL — no "
    "embedded conclusion, (c) are navigable questions a researcher/clinician/patient would actually ask, and "
    "(d) are answerable by the empirical literature (not philosophical).\n"
    "CRITICAL — R-Q-6, specificity is mandatory: each question must be NARROW, SPECIFIC, DIRECTED and OBJECTIVE — "
    "exactly ONE relationship (one exposure/intervention vs one outcome) with a DELIMITED population/context, such "
    "that a single focused literature search answers it. REJECT and DO NOT propose broad, open, umbrella, or "
    "subjective questions. If a gap is broad, DECOMPOSE it into several narrow questions instead of one wide one.\n"
    "  BAD (too broad): 'What causes lipedema?' · 'How is lipedema treated?' · 'What is the best therapy?'\n"
    "  GOOD (narrow): 'Is lipedema associated with thyroid disease?' · 'Does complete decongestive therapy reduce "
    "pain in lipedema?' · 'Does a ketogenic diet reduce limb volume in lipedema?'\n"
    "One distinct, testable relationship per question. Output strict JSON.")

def discover(gaps, k=10):
    if not ingest.provider():
        sys.exit("No LLM key — discovery needs one.")
    qdata = load_q(); qs = qdata["questions"]
    existing = "\n".join(f'- {q["text"]} [tags: {", ".join(q.get("tags", []))}]' for q in qs)
    user = (f'DOMAIN: lipedema.\nTOPIC AXES: {", ".join(AXES)}.\nUNDER-COVERED AXES (prioritize): {", ".join(gaps) or "none obvious"}.\n\n'
            f'EXISTING QUESTIONS ({len(qs)}):\n{existing}\n\n'
            f'Propose up to {k} NEW questions. Return JSON {{"questions": [{{"text": "...", "text_pt": "...", '
            '"tags": ["AxisFromTheList", ...], "keywords": ["...", "..."], "rationale": "why this is a distinct, '
            'literature-answerable gap"}}]}}. Avoid any overlap with the existing questions.')
    out = ingest._chat_json(SYS_PROPOSE, user).get("questions", [])
    print(f"\n=== DISCOVERY: {len(out)} candidate(s) from {ingest.model_name()} — grounding against the library ===")
    p = load_p()
    seq = max([int(x["temp_id"].split("D")[-1]) for x in p["proposed"]] + [0]) + 1
    added = merged = 0
    for cand in out:
        text = cand.get("text", "").strip()
        if not text:
            continue
        # R-Q-5 canonicalization gate: is this the SAME question as an existing one (just reworded)?
        verdict = phrasings.judge_same(text, qs)
        if phrasings.is_auto_merge(verdict):
            target = next((q for q in qs if q["id"] == verdict["sq_id"]), None)
            if target:
                phrasings.add_phrasing_to_question(target, text, cand.get("text_pt", ""))
                merged += 1
                print(f"  ↩ merged into {target['id']} as PHRASING (conf {verdict['confidence']:.2f}): {text[:66]}")
                continue  # no new SQ — the duplicate becomes an alternative way to ask the canonical one
        hits = ingest.bib_search(text, 6) if ingest.bib_available() else []
        refs = [f"DOI:{h['doi'].lower()}" for h in hits if h.get("doi")][:5]
        grounded = len(hits)
        tmp = f"SQ-LIP-D{seq:06d}"; seq += 1
        entry = {
            "temp_id": tmp, "text": text, "text_pt": cand.get("text_pt", ""),
            "tags": [t for t in cand.get("tags", []) if t in AXES], "keywords": cand.get("keywords", []),
            "rationale": cand.get("rationale", ""), "library_hits": grounded, "example_refs": refs,
            "status": "proposed", "created": TODAY, "engine": ingest.model_name()}
        # related-but-distinct → keep a see-also link so promote() can wire `related`
        if verdict.get("verdict") == "related" and verdict.get("sq_id"):
            entry["related_to"] = verdict["sq_id"]
        p["proposed"].append(entry)
        added += 1
        rel = f" ~related:{verdict['sq_id']}" if entry.get("related_to") else ""
        flag = "✓grounded" if grounded >= 2 else ("·weak" if grounded == 1 else "⚠ungrounded")
        print(f"  {tmp}  [{flag}, {grounded} lib hits]{rel}  {text[:74]}")
    save_p(p)
    if merged:
        json.dump(qdata, open(QF, "w"), ensure_ascii=False, indent=2)  # persist merged phrasings
        db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
    print(f"\nStaged {added} proposal(s); {merged} merged as phrasings into existing questions (R-Q-5).")

def next_final_seq():
    seqs = [int(q["id"].split("-")[-1]) for q in load_q()["questions"] if re.match(r"SQ-LIP-\d+$", q["id"])]
    return (max(seqs) + 1) if seqs else 1

def promote(temp_id):
    p = load_p(); cand = next((x for x in p["proposed"] if x["temp_id"] == temp_id), None)
    if not cand:
        sys.exit(f"{temp_id} not found.")
    qd = load_q()
    fid = f"SQ-LIP-{next_final_seq():06d}"
    newq = {
        "id": fid, "text": cand["text"], "text_pt": cand.get("text_pt", ""),
        "phrasings": [], "phrasings_pt": [],
        "knowledge_state": "speculative", "tags": cand.get("tags", []), "keywords": cand.get("keywords", []),
        "current_answer": "No evidence has been indexed for this question yet.",
        "current_answer_pt": "Nenhuma evidência foi indexada para esta pergunta ainda.",
        "major_uncertainty": "Newly created question; the surveillance loop has not yet populated it.",
        "major_uncertainty_pt": "Pergunta recém-criada; o laço de vigilância ainda não a populou.",
        "version": "1.0", "created": TODAY, "updated": TODAY,
        "history": [{"version": "1.0", "date": TODAY, "change": f"Question created (promoted from {temp_id}).",
                     "change_pt": f"Pergunta criada (promovida de {temp_id})."}],
        "claims": []}
    if cand.get("related_to"):
        newq["related"] = [cand["related_to"]]  # see-also: distinct but adjacent question (R-Q-5)
    qd["questions"].append(newq)
    json.dump(qd, open(QF, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
    cand["status"] = "promoted"; cand["final_id"] = fid; save_p(p)
    print(f"Promoted {temp_id} → {fid}. Next: python3 loop.py {fid} --source library --commit  (to populate).")

def reject(temp_id):
    p = load_p()
    for x in p["proposed"]:
        if x["temp_id"] == temp_id: x["status"] = "rejected"
    save_p(p); print(f"Rejected {temp_id}.")

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        _, gaps = coverage(); discover(gaps)
    elif a[0] == "list":
        for x in load_p()["proposed"]:
            print(f"  {x['temp_id']} [{x['status']}, {x.get('library_hits',0)} hits] {x['text'][:80]}")
    elif a[0] == "promote" and len(a) > 1: promote(a[1])
    elif a[0] == "reject" and len(a) > 1: reject(a[1])
    elif a[0] == "coverage": coverage()
    else: print(__doc__)
