# Scientific Claim Registry — v0.5 (unattended Layer 1 surveillance at library scale)

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Previous version (v0.4):** 10.5281/zenodo.20665788
**Live:** https://scientificclaims.org · **OSF:** https://osf.io/n97ez/
**Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

## What changed from v0.4 → v0.5

v0.4 made every evidence link independently verified. v0.5 is the first version in which the registry has been
**kept current by its own surveillance loop**, and it reports what that took, including where it failed.

### The headline: the corpus grew through the loop, not through manual curation

| | v0.4 (2026-06-12) | v0.5 (2026-11-17) |
|---|---|---|
| Scientific questions | 42 | 42 |
| Evidence claims | 347 | **526** |
| Evidence records | 423 | **626** |
| Question↔claim links | 624 | **895** |
| Distinct DOIs cited | — | **383** |
| Verified (R-AI-14) | 416 | **614** |
| Disputed (kept, flagged) | 0 | **5** |
| Unverified (no source text) | 7 | 7 |
| Contradicting evidence | — | **19** (3.0%) |

Growth came from two passes of the same Layer 1 loop (retrieve → classify → verify → promote/corroborate →
recompile → version), with no manual claim writing:

1. **Weekly rotating contradiction sweep (R-AI-12)**, unattended, June–September 2026: two questions per week,
   each run combining the topical pass with a dedicated null/negative/opposing-evidence pass.
2. **Library-scale backfill (2026-11-17)**: all 42 questions re-run against the author's curated lipedema library,
   which had grown to 4,563 structured records (≈1,450 in lipedema folders), plus Europe PMC. 135 new claims;
   every new evidence record went through dual-model verification before entering (of the 140 records under new
   claims, 136 verified and 4 disputed at ingestion; one of the 4 was then corrected, see below).

Every question whose answer changed received a new **immutable version** with a "what changed" note, so the
growth is auditable question by question, and the weekly runs are recorded as dated commits in the public repository.

### Operational honesty: what broke, and the guarantees added (R-AI-7, R-AI-12)

Running unattended exposed failures that a demo never shows. They are recorded here because a memory system that
hides its own gaps contradicts its premise.

- **Eight silent weeks (2026-09-27 → 2026-11-15).** The LLM credential was absent on the machine running the
  weekly job. The loop exited with an error each week, but the rotation pointer advanced
  and the log reported the questions as "swept": 18 questions were marked as surveyed with nothing done.
  *Guarantee added:* the rotation now advances only over questions whose run completed successfully; a missing
  credential is a loud warning and the pointer stays put. "Sweeping" without running no longer counts as sweeping.
- **Semantic retrieval silently degraded.** The library's semantic endpoint returned an error to every query,
  so runs fell back to a stale keyword index (or to no library evidence at all). *Guarantees added:* keyword
  fallback whenever the semantic pass returns nothing; the weekly job starts the library service itself.
- **A malformed model response (trailing comma in JSON) discarded a whole question's run.** Writes were atomic,
  so nothing partial entered the registry; parsing now retries leniently once.

### Verification at the claim level, continued

One new claim stated that a source did *not* report quality-of-life data when it did. It was re-anchored to the
source's own wording and re-verified (recorded in its change log). The remaining disputed records are stance-nuance
disagreements between the two models (e.g. *refines* vs *supporting*) and one stance question on a prospective
cohort; they are published with their flag, not removed (*registers, does not arbitrate*).

### Honesty / prior art (unchanged stance)

SCR does not invent the claim primitive or persistent claim identity (nanopublications/Trusty URIs,
micropublications, Wikidata, CIViC, ClinGen, Epistemonikos/PICO, SciFact, GRADE/MAGICapp already exist). The v0.5
contribution is evidence that a question-centric, verified, versioned registry can be **maintained by its own
loop**, with the failure modes of unattended operation documented and guarded.

## Files

- `pilot-dataset/` — `claims.json`, `questions.json` (with immutable version snapshots), `domains.json`
- `spec/` — `PROTOCOL.md` (SCR Protocol v1), `RULES.md` (rulebook, with changelog), claim schema, ID allocation,
  surveillance, creation strategy, governance model
