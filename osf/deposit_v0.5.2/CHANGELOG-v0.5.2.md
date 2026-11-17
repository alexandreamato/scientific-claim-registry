# Scientific Claim Registry — v0.5.2 (corrective release)

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Supersedes:** v0.5.1, 10.5281/zenodo.24325390 (and v0.5, 10.5281/zenodo.24324283)
**Live:** https://scientificclaims.org · **Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

**Use v0.5.2 instead of v0.5.1 or v0.5.**

## Change from v0.5.1

- The `first_mention` anchor of SQ-LIP-000004 pointed to a reference that the curator's rules exclude from citation
  (`author_ban`, R-CLM-10). It was removed, and the tool that sets this anchor now skips excluded references. This was
  the only such reference left in v0.5.1.
- The rulebook (`spec/RULES.md`) records the cleanup of the project's public repository history.

The dataset content is otherwise identical to v0.5.1: 42 questions, 514 evidence claims, 612 evidence records
(601 verified, 4 disputed, 7 unverified), 876 question↔claim links, 371 distinct DOIs.

Known limitation, unchanged: the `first_mention` anchor of several questions is a recent preprint rather than the
oldest article on the topic; it is a timeline anchor, not evidence, and will be corrected in a later version.
