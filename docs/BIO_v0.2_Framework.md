# BIO v0.2

## Biological Intelligence Observatory

### A Claim-Centric Framework for Versioned Biomedical Knowledge

### Position Paper and Research Agenda

Version 0.2 — May 2026

---

# Abstract

Biomedical knowledge is currently organized around publications.

Journal articles, systematic reviews, guidelines, and consensus documents serve as the primary mechanisms for storing and communicating scientific knowledge. While highly successful, these structures are fundamentally publication-centric and largely static.

This paper proposes BIO (Biological Intelligence Observatory), a research framework for claim-centric biomedical knowledge management.

In BIO, scientific claims rather than publications become the primary knowledge objects. Claims are linked to supporting and contradictory evidence, expert commentary, revision history, uncertainty assessments, and semantic relationships to other claims.

BIO does not propose replacing the existing scientific ecosystem. Instead, it proposes investigating whether claim-centric knowledge structures can complement publication-centric systems and improve evidence navigation, transparency, update speed, and knowledge maintenance.

The framework draws inspiration from existing developments including nanopublications, living systematic reviews, biomedical knowledge graphs, structured evidence assessment systems, and version-control methodologies.

Lipedema is proposed as the initial proof-of-concept domain.

The central hypothesis is testable:

Can a claim-centric, versioned, expert-curated knowledge system outperform traditional publication-centric knowledge synthesis in maintaining current biomedical knowledge?

---

# 1. Introduction

Modern biomedical science produces knowledge at a rate that exceeds the ability of individuals and institutions to continuously synthesize it.

Although articles remain the fundamental mechanism of scientific communication, clinicians, researchers, and patients increasingly require answers to questions that transcend individual publications:

- What is currently known?
- What remains uncertain?
- What has changed recently?
- Which claims are controversial?
- Which claims are becoming more stable?

Existing infrastructures answer these questions only indirectly.

BIO is motivated by the possibility that scientific claims may represent a more appropriate unit of continuous knowledge maintenance than publications themselves.

---

# 2. Prior Art

BIO is not proposed as a completely novel invention.

Instead, it is proposed as a potential integration and extension of multiple existing approaches.

Relevant predecessors include:

- Nanopublications
- Wikidata
- Living Systematic Reviews
- Living Guidelines
- GRADE
- Biomedical Knowledge Graphs
- scite.ai
- ClinGen
- CIViC
- PharmGKB
- Open Targets
- Monarch Initiative

BIO builds upon these efforts rather than replacing them.

The primary distinction proposed by BIO is the integration of these concepts into a unified claim-centric framework with explicit versioning, provenance tracking, and continuous expert review.

---

# 3. Core Hypothesis

BIO is founded on a single research hypothesis:

Claim-centric knowledge systems may provide superior maintenance of evolving biomedical knowledge compared with publication-centric systems.

This hypothesis remains unproven.

The purpose of BIO is to test it.

---

# 4. Claims as Knowledge Objects

A claim is defined as:

A scientifically meaningful assertion expressed within a clearly defined context.

Claims are not considered context-free statements.

Every claim must explicitly specify:

- Population
- Condition
- Exposure or intervention
- Comparator
- Outcome
- Methodological scope

For example:

"Among adult women meeting Consensus Definition X for lipedema, joint hypermobility prevalence appears higher than in age-matched female controls."

This structure acknowledges that claims derive meaning from context.

---

# 5. Separation of Evidence, Consensus, and Truth

BIO explicitly rejects the assumption that consensus equals truth.

Three separate dimensions are tracked:

### Evidence Confidence
Assessment of supporting evidence quality.

### Consensus Agreement
Degree of agreement among participating experts.

### Knowledge State
Current interpretation of the claim's status.

Examples:
- Speculative
- Emerging
- Probable
- Established
- Foundational

These dimensions must never be conflated.

A claim may have high consensus and weak evidence, or strong evidence and low consensus.

The system should expose such discrepancies rather than hide them.

---

# 6. Versioned Knowledge

BIO treats scientific knowledge as a continuously evolving process.

Every modification generates a permanent revision record.

Version history includes:
- Author
- Reviewer
- Timestamp
- Rationale
- Evidence added
- Evidence removed

The objective is not to determine final truth. The objective is to preserve the evolution of scientific understanding.

---

# 7. Governance Before Automation

The primary challenges facing BIO are social rather than technical.

Therefore governance precedes automation.

Any implementation must define:
- Contributor eligibility
- Conflict-of-interest disclosure
- Dispute resolution procedures
- Editorial authority
- Appeal mechanisms
- Transparency requirements

Artificial intelligence cannot replace these structures.

---

# 8. Artificial Intelligence as Assistant

BIO does not assume that current AI systems can reliably curate scientific knowledge.

AI is initially restricted to:
- Literature surveillance
- Candidate claim detection
- Duplicate detection
- Semantic linking

Human experts remain responsible for all claim approval and modification.

Future expansion depends on empirical validation.

---

# 9. Pilot Study

The first implementation should remain intentionally limited.

Recommended scope:
- Disease: Lipedema
- Claims: 50–100
- Curators: 10–20 experts
- Duration: 12 months
- Evidence assessment: existing GRADE methodology
- Updating cycle: scheduled rather than real-time

The objective is evaluation rather than scale.

---

# 10. Success Criteria

BIO should be evaluated against measurable outcomes:
- Update latency
- Expert participation
- Inter-rater agreement
- Knowledge retrieval efficiency
- User satisfaction
- Evidence traceability
- Cost of maintenance

Most importantly: Can claim-centric knowledge management produce demonstrably better outcomes than existing alternatives?

---

# 11. Research Agenda

BIO should be viewed as an experiment in scientific infrastructure.

Key questions:
- Can claims be reliably represented?
- Can experts sustainably maintain them?
- Can versioning improve transparency?
- Can governance scale?
- Can claim-centric systems coexist with traditional publishing?

These questions remain open.

---

# Conclusion

BIO is not proposed as a replacement for journals, systematic reviews, or scientific publishing.

It is proposed as a testable framework for investigating whether claim-centric, versioned, expert-curated biomedical knowledge systems can improve the maintenance and accessibility of scientific knowledge.

The ultimate goal is not to replace science as currently practiced. The goal is to determine whether scientific knowledge itself can become more transparent, more traceable, and more adaptable to continuous change.
