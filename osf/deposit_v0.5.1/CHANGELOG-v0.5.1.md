# Scientific Claim Registry — v0.5.1 (corrective release)

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Supersedes:** v0.5, 10.5281/zenodo.24324283
**Live:** https://scientificclaims.org · **Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

v0.5.1 corrects the v0.5 dataset, published the same day. **Use v0.5.1 instead of v0.5.**

## Why a corrective release

The v0.5 dataset contained references that the curator's rules exclude from citation. They had entered through
semantic retrieval over the curator's library, which catalogues those records (marked as not citable) but whose
mark the surveillance loop did not read. They were found and removed after v0.5 was published. A published Zenodo
version cannot be edited, so the correction is this new version.

## Changes from v0.5

- **Curation (R-CLM-10, new category `author_ban`):** 11 references removed (11 claims), and the loop now refuses
  them on ingest. One preprint was removed as `superseded` by its peer-reviewed version (1 claim). Archived question
  versions that cited removed claims keep their number and date, with their content withdrawn and a notice.
- **Risk of bias from full-text appraisal (R-CLM-18, new):** four studies central to contested questions (lipedema
  progression, weight loss and bariatric surgery, a sensory test for diagnosis, pain after bariatric surgery) were
  re-rated as high risk of bias, each point justified with the verbatim passage from the full text and shown on the
  claim page; GRADE downgraded one level. Points of position or interpretation were excluded. The appraisal was done
  by an AI model and checked against the PDFs; it is labelled as such, not as expert (Layer 2) review.
- **Answers recompiled** for the affected questions. The answer on progression to lymphedema (SQ-LIP-000039) no
  longer rests on a single cohort's "stable in two-thirds" framing.
- **Two operational guarantees:** a provider refusal (no credit, invalid key) now aborts a run without writing,
  instead of falling back to a heuristic that would have recorded title-only claims; and banned authorship is
  checked at the loop's final filter.

## Dataset

| | v0.5 | v0.5.1 |
|---|---|---|
| Scientific questions | 42 | 42 |
| Evidence claims | 526 | **514** |
| Evidence records | 626 | **612** |
| Question↔claim links | 895 | **876** |
| Distinct DOIs | 383 | **371** |
| Verified / disputed / unverified (R-AI-14) | 614 / 5 / 7 | **601 / 4 / 7** |

## Files

- `pilot-dataset/` — `claims.json`, `questions.json`, `domains.json`
- `spec/` — `PROTOCOL.md`, `RULES.md` (with changelog), claim schema, ID allocation, surveillance, creation strategy, governance model
