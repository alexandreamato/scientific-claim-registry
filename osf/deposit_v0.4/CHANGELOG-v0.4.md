# Scientific Claim Registry — v0.4 (adversarially AI-verified registry + expanded lipedema pilot)

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Previous version (v0.3):** 10.5281/zenodo.20476673
**Live:** https://scientificclaims.org · **OSF:** https://osf.io/n97ez/
**Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

## What changed from v0.3 → v0.4

v0.3 delivered the **implemented, live system**. v0.4 makes every piece of evidence in it **independently
verifiable and verified** — the registry now ships with a per-evidence trust layer that, to our knowledge, no
other claim/evidence registry has.

### The headline: a verification layer (R-AI-13, R-AI-14, R-CLM-17)

Verifying that a DOI *resolves* proves the source exists — not that the claim is *faithful* to it. v0.4 closes
that gap with two altitudes of checking, both built into the surveillance loop and applied retroactively to the
whole pilot:

- **Sentence-level provenance (R-AI-13).** Every evidence record carries a **verbatim `quote`** copied from the
  source that grounds its stance, with **deterministic grounding** (the quote must be an exact span of the source
  text) — catching a hallucinated or paraphrased quote with no model in the loop. Each claim is now *falsifiable
  by inspection*.
- **Adversarial dual-model verification (R-AI-14).** A **second, independent model** (distinct from the primary
  classifier) re-derives the stance and judges faithfulness against the source. Fidelity is checked at **two
  altitudes**: per-source (does this source *contradict* or *misattribute*?) and per-claim (does the statement
  assert a specific present in *no* source — i.e. fabrication, checked against the union of the claim's sources).
  A record is `verified` only when stance and provenance are independently confirmed; otherwise it is recorded as
  `disputed` (never deleted — *registers, does not arbitrate*) and flagged for review.
- **Two distinct confidences, never fused (R-CLM-17):** `grade` (GRADE — the *study's* quality) is kept separate
  from `extraction_confidence` (how well the *source was read*).

### What the full audit found (and fixed)

The entire pilot — **all 423 evidence sources across 42 questions** — was audited and reviewed:

- **416 verified · 0 disputed · 7 unverified** (the 7 have no recoverable source text). 98% verified.
- **13 statement fabrications caught and corrected** — concrete specifics (sample sizes, statistics, mechanisms,
  named methods) that appeared in *no* source, including one statement with 7 invented clinimetric figures.
- **Cross-paper contamination caught** — statements assembled from findings belonging to *other* studies (e.g. an
  epidemiology claim describing a different study's surgical cohort), plus stance mislabels (a source arguing the
  opposite of its assigned role) and review-design errors (scoping vs. systematic).
- These are silent errors that DOI-resolution and single-model extraction cannot surface; the verification layer
  makes them visible, then the corpus was cleaned. Every fix is recorded in each claim's change log.

### Made public and machine-first (R-SITE-17)

Verification is surfaced, not hidden: a **per-question rollup** ("N of M sources independently verified") on every
question page and in its JSON (`evidence_verification`), a **registry-wide seal** on the homepage and questions
index, and a global figure in the static read API. Verified / disputed / unverified are shown honestly side by side.

### Dataset growth

The lipedema pilot expanded from the v0.3 snapshot (25 questions / 240 claims) to **42 versioned scientific
questions and 347 evidence claims** (624 question↔claim links), each claim now carrying verification metadata.

### Honesty / prior art (unchanged stance)

SCR does not invent the claim primitive or persistent claim identity (nanopublications/Trusty URIs,
micropublications, Wikidata, CIViC, ClinGen, Epistemonikos/PICO, SciFact, GRADE/MAGICapp already exist). The v0.4
contribution is **adversarial, sentence-grounded verification of each evidence link, exposed machine-first** — built
on top of that prior art, question-centric, registering-not-arbitrating.

## Contents of this deposit

- `spec/` — canonical specification: **RULES.md** (the rulebook, now including R-AI-13/14, R-CLM-17, R-SITE-17),
  **PROTOCOL.md** (the disease-agnostic protocol core), surveillance.md (the loop), creation-strategy.md,
  claim-schema.md, id-allocation.md, governance-model.md (Layer-2, optional).
- `pilot-dataset/` — snapshot of the live **lipedema pilot**: `questions.json` (42), `claims.json` (347, each
  evidence record carrying `quote` / `extraction_confidence` / `verification`), `domains.json`.
  *(Framework & docs: CC BY 4.0. The registry data is also live and machine-readable at scientificclaims.org/api.)*
