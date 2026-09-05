# Scientific Claim Registry — v0.3 (working framework + lipedema pilot)

**Concept DOI** (always latest): 10.5281/zenodo.20466195 · **Previous version (v0.2):** 10.5281/zenodo.20466196
**Live:** https://scientificclaims.org · **OSF:** https://osf.io/n97ez/
**Author:** Dr. Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029 · CC BY 4.0

## What changed from v0.2 → v0.3

v0.2 **proposed** the framework. v0.3 is the **implemented, live system** — the "future implementation" v0.2 anticipated.

### Conceptual
- **Question-centric pivot.** The scientific **question** (`SQ-LIP-…`) is the primary navigable object; **claims**
  (`SCR-LIP-…`) are versioned evidence linked underneath with a role (supporting/contradicting/refines/context). Graph, not tree.
- **Registers, not arbitrates.** Layered architecture: L1 Registry (the product, automatable) · L2 Consensus (optional) · L3 Recommendation (optional).
- **Positioning:** *"PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to scientific questions."* — a **versioned memory of how scientific answers evolve**.

### Implemented (live)
- **Layer-1 surveillance loop:** semantic retrieval over a curated corpus + Europe PMC + reading lists → LLM classify
  (relevance/stance/design/quality) → conservative merge (distinct = new claim; restatement = corroboration) →
  AI-compiled, evidence-bounded answers → **versioned** with immutable citable snapshots.
- **Knowledge Freshness / Evidence Decay** per question; **evidence timeline** anchored at the topic's first literature mention.
- **Quality weighting** (strong evidence overshadows weak); reference verification; **article ban system** with automated
  **retraction detection** (Crossref); full **temporal provenance** (created/updated/change-log) on every claim and question.
- **Question-creation strategy:** coverage analysis (axes) + literature-grounded LLM discovery + temp→final lifecycle.
- **Machine-first:** JSON per question/claim and a static read API. **Bilingual** (EN + PT). Persistent IDs with a temp→validated→final lifecycle and a domain dictionary cross-referenced to MONDO/ICD-11/MeSH.

### Honesty / prior art (unchanged stance)
SCR does not invent the claim primitive or persistent claim identity (nanopublications/Trusty URIs, micropublications,
Wikidata, CIViC, ClinGen, Epistemonikos/PICO, SciFact, GRADE/MAGICapp already exist). Contribution = adoption + domain
organization + versioned accumulation + freshness + machine-first, **built on** that prior art.

## Contents of this deposit
- `spec/` — canonical specification: **RULES.md** (the rulebook), surveillance.md (the loop), creation-strategy.md
  (how questions & claims are created), claim-schema.md, id-allocation.md, governance-model.md (Layer-2, optional).
- `pilot-dataset/` — snapshot of the live **lipedema pilot**: `questions.json` (25), `claims.json` (240), `domains.json`.
  *(Framework & docs: CC BY 4.0. The registry data is also available live and machine-readable at scientificclaims.org/api.)*
