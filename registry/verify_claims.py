#!/usr/bin/env python3
"""SCR — retroactive evidence verifier (R-AI-13/14 audit).

The closed loop verifies evidence as it enters. This tool audits evidence that is ALREADY in the
registry — the legacy items ingested before dual-model verification existed — and backfills, per
evidence record:
  • a sentence-level provenance QUOTE (R-AI-13): a verbatim span of the source that grounds the stance;
  • an EXTRACTION confidence (R-CLM-17): how well the source was read (≠ GRADE, the study's quality);
  • a VERIFICATION verdict (R-AI-14): an INDEPENDENT model re-derives the stance and judges faithfulness;
    `verified` iff the quote is grounded AND the verifier agrees on stance AND finds the statement faithful;
    else `disputed` (recorded, never deleted — registra, não arbitra).

It NEVER rewrites the stored statement or stance; it only ADDS the audit fields. A `disputed` verdict
flags the item needs_review and surfaces a ⚠ badge on the site — turning a silent error into a visible,
honest dispute. Reproducible from public sources (Europe PMC); the author's library only enriches.

Run LOCALLY (needs an LLM key, same as loop.py). Pipeline after a commit: db.sync (automatic) →
build_questions.py + build_site.py → rsync.

Usage:
  python3 verify_claims.py                       # dry-run audit of ALL not-yet-verified evidence
  python3 verify_claims.py SQ-LIP-000005         # audit only evidence under one question
  python3 verify_claims.py SCR-LIP-000017        # audit one claim
  python3 verify_claims.py --limit 5             # cap to 5 evidence items (cheap smoke test)
  python3 verify_claims.py --reverify            # re-audit even already-verified items
  python3 verify_claims.py --commit              # write claims.json + sync the DB
"""
import json, os, sys, datetime
import ingest
import db

DIR = os.path.dirname(os.path.abspath(__file__))
QJSON = os.path.join(DIR, "questions.json")
CJSON = os.path.join(DIR, "claims.json")
TODAY = datetime.date.today().isoformat()


def claim_questions_map(qdata):
    """claim_id -> the question dict that links it (first link wins — enough to anchor stance)."""
    out = {}
    for q in qdata["questions"]:
        for l in q.get("claims", []):
            out.setdefault(l["id"], q)
    return out


def fetch_article(ref):
    """Resolve a stored 'DOI:..'/'PMID:..' ref to an article with abstractText. Library ficha first
    (richer), else Europe PMC. Returns None when no source text can be recovered."""
    if not ref:
        return None
    r = ref.strip()
    if r.upper().startswith("DOI:"):
        doi = r[4:]
        art = ingest.bib_by_doi(doi) or ingest.europepmc_by_doi(doi)
        return art if (art and art.get("abstractText")) else art
    if r.upper().startswith("PMID:"):
        # Europe PMC search by PMID
        try:
            res = ingest.europepmc(f'EXT_ID:{r[5:]} AND SRC:MED', 1900, 1)
            if res:
                a = res[0]; a["source"] = "europepmc"; return a
        except Exception:
            return None
    return None


def audit_one(q, claim, ev):
    """Verify one evidence item against its STORED stance/statement. Returns (verification, quote,
    extraction_confidence, source_text) — source_text is the combined text the verifier saw, returned so
    the caller can accumulate it for the per-claim integrity check (R-AI-14, per-claim altitude)."""
    ref = ev.get("ref")
    art = fetch_article(ref)
    if not art or not art.get("abstractText"):
        return {"method": "dual-model", "verdict": "unverified", "quote_grounded": False,
                "stance_agreed": None, "faithful": None, "reason": "source text unavailable for re-verification",
                "date": TODAY}, None, None, ""
    stored_stance = ev.get("stance", "context")
    stored_stmt = claim.get("statement", "")
    # Primary model reads the source independently to propose a grounding quote for the STORED finding.
    try:
        cl0 = ingest.llm_classify(q, art)
    except Exception as ex:
        return {"method": "dual-model", "verdict": "unverified", "reason": f"classify error: {ex}",
                "quote_grounded": False, "date": TODAY}, None, None, ""
    # cl0 (primary re-read) is used ONLY to extract a grounding quote for the STORED finding; its stance
    # is NOT used to override the verdict — the audit uses the SAME rule as the forward loop (grounding +
    # the independent verifier's stance + per-source faithfulness), so a flag means the same thing everywhere.
    cl_v = {"stance": stored_stance, "statement": stored_stmt,
            "quote": cl0.get("quote", ""), "extraction_confidence": cl0.get("extraction_confidence", "moderate"),
            "engine": ingest.model_name()}
    ver = ingest.verify_extraction(q, art, cl_v)
    return ver, cl_v["quote"], cl_v["extraction_confidence"], ingest.combined_source_text(art)


def main():
    args = sys.argv[1:]
    commit = "--commit" in args
    reverify = "--reverify" in args
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 10**9
    qfilter = next((a for a in args if a.startswith("SQ-")), None)
    cfilter = next((a for a in args if a.startswith("SCR-")), None)

    if not ingest.provider():
        sys.exit("No LLM key — set an Anthropic/OpenAI/OpenRouter key (see loop.py). This audit needs one.")

    qdata = json.load(open(QJSON)); cdata = json.load(open(CJSON))
    cq = claim_questions_map(qdata)
    q_by_id = {q["id"]: q for q in qdata["questions"]}
    claims = cdata["claims"]

    print(f"primary: {ingest.model_label(ingest.model_name())}  ·  verifier: {ingest.model_label(ingest.verify_model_name())}")
    targets = []
    for c in claims:
        if cfilter and c["id"] != cfilter:
            continue
        q = q_by_id.get(qfilter) if qfilter else cq.get(c["id"])
        if qfilter and (not q or not any(l["id"] == c["id"] for l in q.get("claims", []))):
            continue
        if not q:
            continue  # cannot judge stance without a question anchor
        for ev in c.get("evidence", []):
            if not reverify and (ev.get("verification") or {}).get("verdict"):
                continue
            targets.append((q, c, ev))

    print(f"{len(targets)} evidence item(s) to audit" + (f" (capped to {limit})" if limit < len(targets) else "") + "\n")
    counts = {"verified": 0, "disputed": 0, "unverified": 0}
    disputed = []
    # Per-source pass: verify each evidence item; accumulate the source text seen, per claim, for the
    # per-claim integrity (fabrication) pass that follows.
    claim_sources = {}   # cid -> list of source texts
    claim_qc = {}        # cid -> (q, claim)
    for i, (q, c, ev) in enumerate(targets):
        if i >= limit:
            break
        ver, quote, ec, src = audit_one(q, c, ev)
        vd = ver.get("verdict", "unverified")
        counts[vd] = counts.get(vd, 0) + 1
        ev["verification"] = ver
        if quote is not None:
            ev["quote"] = (quote or "")[:300]
        if ec:
            ev["extraction_confidence"] = ec
        if vd == "disputed":
            ev["needs_review"] = True
            disputed.append((c["id"], ev.get("ref"), ver.get("reason", "")))
        elif "needs_review" in ev and vd == "verified":
            ev.pop("needs_review", None)
        if src:
            claim_sources.setdefault(c["id"], []).append(src)
            claim_qc[c["id"]] = (q, c)
        mark = {"verified": "✓", "disputed": "⚠", "unverified": "?"}.get(vd, "?")
        print(f"  {mark} {c['id']}  {ev.get('ref'):28s}  {vd:11s}  {ver.get('reason','')[:60]}")

    # Per-claim integrity pass (R-AI-14, per-claim altitude): does the STATEMENT assert specifics absent
    # from the UNION of the claim's sources? Catches fabrication that per-source checking cannot.
    fabricated = []
    if claim_qc:
        print("\n— per-claim statement integrity (fabrication vs. union of sources) —")
    for cid, (q, c) in claim_qc.items():
        union = "\n\n".join(dict.fromkeys(claim_sources.get(cid, [])))  # dedupe, preserve order
        integ = ingest.verify_statement_integrity(q, c.get("statement", ""), union)
        c["statement_integrity"] = integ
        if integ.get("fabricated"):
            fabricated.append((cid, integ.get("invented", []), integ.get("reason", "")))
            print(f"  ⚠ {cid}  FABRICATION  invented={integ.get('invented')}  — {integ.get('reason','')[:60]}")
        else:
            print(f"  ✓ {cid}  statement consistent with its sources")

    print(f"\nverified: {counts['verified']}  ·  disputed: {counts['disputed']}  ·  unverified: {counts['unverified']}"
          f"  ·  claims w/ fabrication: {len(fabricated)}")
    if disputed:
        print("\nPER-SOURCE DISPUTED (contradiction or misattribution — needs human review):")
        for cid, ref, reason in disputed:
            print(f"  • {cid}  {ref}  — {reason[:90]}")
    if fabricated:
        print("\nSTATEMENT FABRICATION (specifics in no source — needs human review):")
        for cid, inv, reason in fabricated:
            print(f"  • {cid}  invented={inv}  — {reason[:80]}")
    if not commit:
        print("\n(dry-run — re-run with --commit to write claims.json + sync the DB)")
        return
    json.dump(cdata, open(CJSON, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)
    print("\n✓ claims.json written + DB synced. Next: build_questions.py + build_site.py → rsync.")


if __name__ == "__main__":
    main()
