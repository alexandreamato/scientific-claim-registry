# Scientific Claim Registry (SCR)
### A public, versioned, expert-curated registry of biomedical scientific claims

> **Texto público do projeto no OSF.** (Descrição institucional, SCR à frente.)

---

**Papers have DOIs. Researchers have ORCIDs. Trials have registration numbers.
Sequences have accession numbers. Scientific claims have nothing.**

The **Scientific Claim Registry (SCR)** is a research initiative to give the scientific
*claim* — the actual assertion that science exists to establish, revise, and sometimes
overturn — a persistent identity of its own.

Today, claims remain trapped inside the prose of publications: un-addressable,
un-versionable, and impossible to track as evidence accumulates. As a result, no
existing system can answer simple questions such as *"when did the field begin to
believe this?"*, *"how strongly is it believed now?"*, or *"what changed since last
year?"*. SCR proposes that each claim receive a permanent identifier, a canonical
statement with explicit context, links to supporting and contradicting evidence, an
evidence-certainty rating (reusing GRADE), and a complete, auditable version history.

SCR is operated by the **BIO (Biological Intelligence Observatory)** method — the
methodology and governance layer that maintains the registry, much as CrossRef operates
DOIs or ClinicalTrials.gov operates trial registration.

**SCR is a hypothesis, not a finished platform.** Its central, testable question:

> *Can a claim-centric, versioned, expert-curated registry maintain current biomedical
> knowledge better than today's publication-centric synthesis?*

**Lipedema** is the first proof-of-concept domain — chosen because it is hard: a rapidly
expanding, fragmented literature with active controversies, multidisciplinary stakes,
and an engaged international community. The framework is disease-agnostic by design.

This OSF project is the public, timestamped record of SCR's conceptual foundation,
methodology, prior-art analysis, and pilot. It establishes the priority date of the
framework and grows as the work develops.

**v0.3 (current) — from proposal to a live system.** v0.2 proposed the framework; v0.3 is the
implemented, running registry at https://scientificclaims.org. The object model pivoted to be
**question-centric**: the scientific *question* (e.g. `SQ-LIP-000007`) is the primary navigable
object, with *claims* (`SCR-LIP-000001`) as versioned evidence linked underneath by role. A closed
**Layer-1 surveillance loop** (semantic retrieval → LLM classification → conservative merge →
AI-compiled, evidence-bounded answers → immutable versioned snapshots) keeps each answer current,
with Knowledge Freshness, quality weighting, retraction detection, full temporal provenance, and a
machine-first bilingual (EN + PT) interface. **Lipedema pilot:** 25 versioned questions, 240 claims.

---

**Founder & Principal Investigator:** Alexandre Campos Moraes Amato (Amato Duo;
Associação Brasileira de Lipedema), ORCID 0000-0003-4008-4029

**License:** CC BY 4.0 (open access by principle). **Status:** v0.3 — implemented framework + live
lipedema pilot. **Version of record:** Zenodo DOI 10.5281/zenodo.20476673 (concept DOI 10.5281/zenodo.20466195).

**Prior art acknowledged:** nanopublications, micropublications, Wikidata, CIViC,
ClinGen, PharmGKB/CPIC, Open Targets, Cochrane Living Systematic Reviews, GRADE,
MAGICapp, and related claim-centric proposals. SCR's contribution is *adoption,
governance, and execution in a specific domain*, not the concept of a claim object.
