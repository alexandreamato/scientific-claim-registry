#!/usr/bin/env python3
"""Backfill real PECO context on claims that have placeholder context (R-CLM-15 / audit 2026-06).
86% of claims had population/exposure/comparator/outcome = '—'. For each, derive PECO from the
statement + evidence (structured extraction — uses Sonnet, cheaper/faster than Opus). Idempotent.
Does NOT change the answer (PECO is claim metadata) — no recompile needed.
  python3 backfill_peco.py [--force] [SCR-LIP-000123 ...]"""
import os, sys, json
os.environ.setdefault("SCR_LLM_MODEL", "anthropic/claude-sonnet-4.6")  # extraction; cheap/fast
import ingest, db

HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.join(HERE, "claims.json")
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if a.startswith("SCR-")]

SYS = ("You extract structured PECO context for a scientific CLAIM in a lipedema registry. "
       "Given the claim statement and its evidence, return STRICT JSON with keys population, exposure, "
       "comparator, outcome — each a SHORT noun phrase (≤8 words) grounded in the claim; use '—' only if "
       "genuinely not applicable. population = who (e.g. 'women with lipedema, stage I–III'); exposure = the "
       "intervention/factor studied (e.g. 'tumescent liposuction'); comparator = vs what (e.g. 'pre-operative "
       "baseline' or '—'); outcome = the measured endpoint (e.g. 'limb pain (VAS)'). No prose.")


def empty(ctx):
    return all((not ctx.get(k) or ctx.get(k) == "—") for k in ("population", "exposure", "comparator", "outcome"))


def main():
    data = json.load(open(CF)); n = 0; fail = 0
    for c in data["claims"]:
        if ONLY and c["id"] not in ONLY:
            continue
        ctx = c.setdefault("context", {})
        if not empty(ctx) and not FORCE:
            continue
        ev = "; ".join(f"{e.get('study_design','?')} ({e.get('grade','?')})" for e in c.get("evidence", [])[:6])
        user = f"CLAIM: {c.get('statement','')}\nTYPE: {c.get('claim_type')}\nEVIDENCE: {ev}"
        try:
            out = ingest._chat_json(SYS, user)
        except Exception as e:
            fail += 1; print(f"  [{c['id']} error: {e}]"); continue
        for k in ("population", "exposure", "comparator", "outcome"):
            v = (out.get(k) or "").strip()
            if v:
                ctx[k] = v
        ctx.setdefault("condition", ingest.DOMAIN_TERM.get("LIP", "lipedema"))
        n += 1
        if n % 25 == 0:
            json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)  # checkpoint
            print(f"  …{n} PECO filled")
    json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)
    print(f"Done. PECO filled on {n} claim(s); {fail} failures. DB synced.")


if __name__ == "__main__":
    main()
