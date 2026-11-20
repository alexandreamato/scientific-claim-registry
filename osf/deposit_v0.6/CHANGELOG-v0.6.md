# Scientific Claim Registry — v0.6: General propositions backed by study-level findings

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Previous version:** v0.5.2, 10.5281/zenodo.24325901
**Live:** https://scientificclaims.org · **Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

## What changed: a claim is now a general proposition (R-CLM-19)

Up to v0.5.2, 87% of claims had a single source and read like a paper's abstract (median 43 words, with sample
sizes, percentages and p-values). Such a claim holds for one paper only, and several papers cannot support or
contradict it. v0.6 restructures the registry so that:

- **a claim is a general proposition**: at most 25 words, one idea, no numbers, never a description of a study, and
  worded no more strongly than its evidence licenses (median 18 words);
- **each study's own result is its `finding`**, stored on the evidence row under the proposition, with the quote,
  verification and risk-of-bias data carried over intact;
- a review that only re-reports another included study is marked `secondary_of` and does not count;
- a proposition's GRADE is computed by a fixed rule from its findings: the best supporting certainty, one level
  lower if a finding of equal or higher certainty contradicts it (R-CLM-11).

## Dataset

- 42 versioned questions; **215 active claims** (general propositions) under 288 question–claim links.
- 168 of the 215 rest on more than one primary study, and 40 are shared by several questions (claim graph, no twins:
  46 duplicate propositions created independently for different questions were merged, R-OBJ-7).
- 837 study-level findings (823 verified, 6 disputed, 8 unverified) citing 356 distinct DOIs.
- The 514 single-paper claims of v0.5.2 are **kept, never deleted** (R-CLM-9): 490 are `superseded` and point to the
  propositions that received their evidence (`superseded_by`); 24 are `retired`, because their only evidence was
  judged not to be a finding on any question (a trial protocol, a truncated abstract, an off-topic paper). The reason
  is in each claim's history.
- All 42 answers were recompiled from the propositions and their findings.

## How it was done (folder `consolidation/`)

For each question, a consolidator model grouped the evidence into propositions. Deterministic code checked every
proposal: each item placed exactly once, no invented keys, length, no numbers, no study-descriptive wording, valid
labels. An independent verifier, a different model with a fresh context that never saw the consolidator's reasoning,
then checked each proposition and the set as a whole for over-generalisation, contradictions, caveats already
overturned by stronger evidence, and double counting. Questions with major problems got one repair round. All 42
ended with no major problem left: 25 at the first verification, 14 after repair, and 3 by adopting the verifier's
more cautious wording (recorded as arbitration, not re-verified).

The consolidator was Claude Opus 5.5 and the verifier Claude Sonnet, both run as Claude Code subagents. Both models
come from the same vendor, so verification here is less independent than the cross-vendor check of R-AI-14. Each
result file records the models used, the verifier's report and any remaining minor issues.

Files: one result per question (`SQ-LIP-*.json`: items, propositions, dropped items with reasons, verification,
status), the shared proposition store (`propositions.json`), the twin merges with their reasons (`twins.json`,
`twins_reasons.md`), the proposition-to-claim mapping (`applied.json`) and the tools (`consolidate.py`,
`apply_consolidation.py`, `recompile_agent.py`).

## Correction

SCR-LIP-000121 cited DOI 10.1111/iwj.13071, which resolves to a paper on the cost of pressure injuries. Its quote is
verbatim from Shavit E, Wollina U, Alavi A. "Lipoedema is not lymphoedema: A review of current literature." Int Wound
J 2018, 10.1111/iwj.12949 (checked against the Europe PMC abstract). The reference was corrected in all four
evidence rows, with the old value kept in `correction`.

## Known limitations

- The verifiers flagged leftover metadata problems in some older evidence rows: titles that do not match their
  quote, duplicated records of one study, and preprints used as evidence. They are listed as minor issues in the
  result files and were not corrected in this release.
- Some evidence-level GRADE ratings inherited from earlier versions are generous, such as before-after
  meta-analyses rated "high". A proposition's grade inherits them.
- The surveillance loop now attaches new papers to the general propositions (with their result as `finding`). A
  paper that fits no proposition still creates a claim in the old, single-paper format.

The registry registers; it does not arbitrate.
