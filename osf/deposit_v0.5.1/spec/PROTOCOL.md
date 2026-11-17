# SCR Protocol v1 — The Open Specification for a Versioned Memory of Scientific Answers

**Status:** Draft (v1.0-draft) · **Date:** 2026-06-02 · **DOI:** [10.5281/zenodo.20517114](https://doi.org/10.5281/zenodo.20517114)
**Editor:** Dr. Alexandre Campos Moraes Amato (Amato Duo) · ORCID `0000-0003-4008-4029`
**Canonical rulebook (reference implementation):** `docs/spec/RULES.md`
**Home of the reference implementation:** https://scientificclaims.org

> This document is the **disease-agnostic, citable specification** of the Scientific Claim Registry (SCR).
> It defines the **rigid minimal core** that any implementation must honour to interoperate — *not* the
> content, the domains, the AI, or the funding model, which are deliberately **open and plural**.
> `RULES.md` remains the canonical operational rulebook of the **reference implementation**; this PROTOCOL
> is the **interoperability standard** distilled from it. Where this document says MUST/SHOULD/MAY, it uses
> them as in RFC 2119.

---

## 0. The one idea

> *"PubMed stores scientific papers. SCR stores the evolving answers to scientific questions."*

SCR is the **operating system of scientific memory** — not of truth, not of consensus, of **memory**: it
records scientific **questions**, the **claims** that answer them, and **how those answers change over time**.
It **registers; it does not arbitrate** (R-MIS-2).

The protocol's job is to make that memory **stable, traceable, versioned, and machine-readable** in a way
that is **identical across every field of science** — so that anyone, anywhere, can create an entry and have
it fit into the same fabric.

---

## 1. Design principle — a small rigid core, a large open periphery

Every standard that achieved global adoption (git, HTTP, DOI, ORCID) shares one shape: a **tiny inflexible
core** wrapped in a **huge open periphery**. SCR is built the same way.

**The rigid core (this document — MUST be identical for every domain and every contributor):**
1. The **object model** (question · claim · evidence; the graph; the layers; answer-as-rendering).
2. The **identifiers** (format, domain dictionary, no reuse, version separated from code).
3. The **identifier lifecycle** (request → temporary → identity-validation → final).
4. The **claim contract** (the minimal fields and disciplines a claim must carry).
5. The **versioning** (immutable, citable snapshots).
6. **Knowledge Freshness** (the evidence-decay signal).
7. The **machine-first surface** (JSON per object).
8. **Provenance & neutrality** (compiler-not-author, public AI provenance, mandatory contradiction-seeking).

**The open periphery (NOT part of the protocol — varies freely, see §11):**
which domains exist · who creates entries · which AI compiles them · which sources are searched ·
how deep curation goes · who pays for compute · which natural language.

A correct mental model: **this protocol is the "git" of scientific answers; a host like
scientificclaims.org is the "GitHub".** The protocol is open; hosts and services compete on top of it.

---

## 2. The four non-negotiable principles (R-MIS-2, R-HON-1/2)

1. **Registers, not arbitrates.** The registry records questions, claims and their evolution. Truth,
   consensus and clinical recommendation are *optional layers above it* (§3), never baked into L1.
2. **Consensus ≠ truth.** Divergence is exposed, never hidden inside a single number.
3. **No false novelty.** SCR does not reinvent persistent identity for claims; it **builds on** existing
   infrastructure (nanopublications/Trusty URIs, DOI/DataCite, PROV-O, ClaimReview, GRADE, ORCID). Its
   contribution is **adoption + organisation by domain + versioned accumulation + freshness + machine-first**.
4. **The compiler does not opine.** Answers are cautious and *evidence-bounded* ("Based on currently
   indexed evidence…"). Human curation is **optional**, not a requirement for the record to exist.

---

## 3. Object model (R-OBJ-1…7)

| Layer | Object | Role |
|---|---|---|
| **Question** | `SQ-<DOMAIN>-<seq>` | The **central navigable object** — stable, neutral. Users enter here. |
| **Claim** | `SCR-<DOMAIN>-<seq>` | **Structured, versioned evidence** linked to one or more questions. |
| **Article** | DOI / PMID | The **source of evidence** under a claim. |

- A claim relates to a question with a **role**: `supporting` · `contradicting` · `refines` · `context`.
- **Claim ↔ question is a graph** (R-OBJ-4/7): one finding is **one claim linked to many questions** —
  never duplicated as parallel twins. Deduplication/canonicalisation across questions is mandatory.
- **Layers — only Layer 1 must exist:**
  - **L1 Registry** (the product, automatable): records questions+claims, accumulates
    supports/contradicts/refines + history. **Does not judge.**
  - **L2 Consensus** (optional): experts endorse / dissent / qualify.
  - **L3 Recommendation** (optional): societies map evidence to clinical conduct.
- **The answer is a rendering, not a stored truth** (R-OBJ-6): the durable assets are the **question**,
  the **claims**, and the **version history**. The prose "current answer" is a derived, versioned view.

---

## 4. Identifiers (R-ID-1…8)

- **Format:** `<PREFIX>-<DOMAIN>-<SEQ>`.
- **PREFIX:** `SQ` = question · `SCR` = claim (intentionally distinct).
- **DOMAIN:** 2–4 uppercase letters, drawn from a **canonical domain dictionary** whose real identity is a
  cross-reference to **MONDO / ICD-11 / MeSH** (or the field's equivalent ontology) — never invented ad hoc.
  Codes are unique, stable, and **never reused**. The dictionary is **extensible**: new domains are added,
  old ones are never repurposed.
- **SEQ:** integer ≥ 1, **zero-padded to a minimum of 6 digits, no ceiling** (overflow simply lengthens).
- **No reuse:** a retracted code becomes a **tombstone**, never re-issued (R-ID-5).
- **Case-insensitive** on read, **uppercase** canonical (R-ID-6).
- **Version (`vX.Y`) is separate from the identifier** — the base code never changes across versions (R-ID-7).

**Federated identity (hybrid model, R-ID-9/10/11).** So that independent hosts can run the protocol without ID
collisions and without a central minting bottleneck — yet without fragmenting the "one evolving answer" thesis:
- **Emission is host-qualified (no central mint).** The bare `SQ-LIP-000001` is *instance-local*; the **global
  physical identifier is `<host>/q/<code>`** (e.g. `scientificclaims.org/q/SQ-LIP-000001`). Each host mints
  locally. (Model: git's global hash + local branch; Trusty URIs.)
- **Domain anchoring is the cross-host authority.** A domain code (`LIP`) is globally comparable ONLY through its
  cross-reference (MONDO / ICD-11 / MeSH, §4 above): two hosts using `LIP` denote the same disease **iff** they map
  to the same `MONDO:…`. SCR is **not** the authority of the disease namespace — it **delegates to MONDO**.
- **The single tissue is reconstructed by `sameAs` resolution, not central minting.** Questions on different hosts
  with the same domain anchor and an equivalent canonical phrasing (the §7 canonicalisation judge extended from
  intra-host to inter-host) are linked `sameAs` and resolved together. Federation does not fragment the canonical
  answer; the global tissue emerges from resolution (cf. Web/Wikidata `sameAs`, DOI, nanopub/Trusty URIs).

---

## 5. Identifier lifecycle — open creation, identity gate (R-ALLOC-1…5)

This is the mechanism that lets **anyone create an entry** while keeping the fabric coherent.

1. **Create = request.** Submitting a question or claim first yields a **TEMP handle**, not a final code.
2. **Validate = identity, not truth** (R-ALLOC-4). Validation checks only that the entry is **well-formed**
   and **deduplicated/canonicalised** against what already exists. It does **not** check whether the claim is
   *correct* — that is never the registry's job.
3. **Match-or-mint.** The system attempts to **fit the request into an existing object** (semantic candidate
   retrieval → adjudication: *same / related / novel*). If it matches, the request **links** to the existing
   object; if not, it **mints a new final code** (TEMP→FINAL alias, the TEMP redirecting forever, R-ALLOC-3).
4. **Counters are monotonic** per `(prefix, domain)` scope (R-ALLOC-5).

> Failure mode is graceful: if matching misses, a duplicate is minted and later **dedup** merges it
> (the graph is repaired, evidence is never lost). Correctness of identity degrades softly; it never blocks.

---

## 6. Claim contract (R-CLM-*) — the minimal evidence discipline

A conforming claim MUST carry:

- **`statement`** — a single, focused, restrictive assertion (R-Q-6). One finding per claim.
- **Explicit context — PECO** (population, condition/exposure, comparator, outcome), filled **at ingestion**,
  never a placeholder (R-CLM-1, R-CLM-15).
- **`grade`** — evidence certainty on the **GRADE** scale (`high/moderate/low/very_low`). Never invented;
  capped by study design and, where a human grade exists, the **human grade is the ceiling** (R-CLM-2/13).
- **`gaps`** — bias, reverse causation, sample limits, etc. (R-CLM-4).
- **`knowledge_state`** — evidence maturity: `Speculative → Emerging → Probable → Established → Foundational`
  (R-CLM-5). A distinct state `no_evidence` marks a **gap** ("absence of evidence ≠ evidence of absence",
  R-CLM-7).
- **Evidence with a verifiable, resolvable reference** — `DOI:` / `PMID:` / citation. A local filename MUST
  NEVER be exposed as a reference (R-CLM-8). Unverifiable references MUST NOT be ingested (R-AI-4).
- **The three dimensions kept separate, always:** *Evidence Confidence · Consensus · Knowledge State*
  (R-CLM-3). They are never collapsed into one score.

**Evidence is permanent; revision is evidence-complete** (R-CLM-9): an article that ever supported a claim is
never silently dropped; every revision re-injects the full evidence set. **Stronger evidence outweighs weaker**
within a claim (R-CLM-11).

---

## 7. Question & answer (R-Q-1…7)

- The **question is neutral** — it embeds no conclusion (R-Q-1).
- The **answer is cautious and evidence-bounded** ("Based on currently indexed evidence…", R-Q-2).
- Questions and claims are **deliberately focused and restrictive** (R-Q-6). Broad "umbrella" questions
  SHOULD be decomposed into outcome/mechanism/modality sub-questions, linked back as a graph.
- **The outcome is mandatory** (R-Q-7): a claim or answer MUST NOT say "effective/safe" without naming the
  outcome it refers to, and MUST distinguish **symptomatic** effect from **disease-modifying** effect.
  Normative judgements ("should be used") belong to L3, never to L1.
- Canonical question + **alternative phrasings**, with **semantic dedup at creation** to avoid near-duplicate
  questions (R-Q-5).

---

## 8. Versioning (R-VER-1…5)

- Any material change to an answer = a **new version (commit)**; no change = no version bump (R-VER-1).
- Every version has a **frozen, immutable, citable snapshot** (R-VER-2); from it you can reach the current
  version and the full history.
- **Versioning is per question** (`version` / `updated` / `history[]`), R-VER-4.
- **Every claim and question carries dates:** `created` · `updated` · `history[]` (R-VER-5).
- Citation cites the **version** (it captures the evidence state at that date), with corporate author
  `Scientific Claim Registry` (R-CIT-1/3).

---

## 9. Knowledge Freshness — the evidence-decay signal (R-FRESH-1…4)

- **Freshness** of a question = the share of its evidence sources from the **last 5 years** (+ newest/oldest
  year, source count).
- **Low freshness ≠ wrong answer** — it flags an **ageing evidence base** (R-FRESH-2).
- **High freshness ≠ robustness** — when `freshness ≥ 90%` **and** `sources < 6`, the object MUST be flagged
  ("small evidence base") so recency is not misread as strength (R-FRESH-4).
- Freshness MUST be exposed both on the human page and in the machine JSON (R-FRESH-3).

---

## 10. Machine-first & provenance (R-MR-1/2/4, R-AI-1/4/5/9/11/12)

- **Every object exposes JSON** (`/q/<id>.json`, `/c/<id>.json`) for LLMs and agents (R-MR-1). The intended
  consumption chain is **PubMed → SCR → AI → User**.
- **Build on, do not reinvent** (R-MR-2): persistent identity via nanopub/Trusty URI + DOI/DataCite; provenance
  via PROV-O; claim review via ClaimReview.
- **The AI is a compiler, not an author** (R-AI-1): it proposes (extracts claims, links evidence, drafts the
  answer); it never decides truth.
- **AI provenance is public** (R-AI-9): the **model** that compiled each answer is shown on the page and in
  the JSON. (Which *means* it was reached — provider/router — is implementation detail and need not appear.)
- **Contradiction-seeking is mandatory** (R-AI-12) and the classifier is **anti-confirmation-bias** (R-AI-11):
  every compilation also actively searches for null/negative/contradicting evidence, so the body of evidence
  is not silently biased toward support.

---

## 11. The open periphery — explicitly NOT part of the protocol

To keep adoption unbounded, the following are **out of scope** and free to vary per domain, host or contributor:

- **Which domains exist** — the domain dictionary is extensible; no central gatekeeper of subject matter.
- **Which AI model compiles** — provider-agnostic (R-AI-6). Any capable LLM is acceptable.
- **Which sources are retrieved** — local libraries, Europe PMC, publisher APIs, curated reading lists, etc.
  (the reference implementation's author-library retrieval, R-AI-7/CLM-12, is **domain-specific, not protocol**).
- **How deep curation goes** — L2/L3 are optional.
- **Who funds compute** — see §12.
- **Natural language** — content language and translations are a presentation concern.

> Rules in `RULES.md` tagged to the lipedema pilot (e.g. author-library preference) are **reference-implementation
> choices**, not protocol requirements. An implementation can be fully SCR-conformant in another field without them.

---

## 12. Contribution & sustainability model (Proposed — R-CONTRIB-*)

The protocol is designed so the **founder need not compile all of science**. Contribution is open; the
*surface* of contribution is deliberately **narrow and safe**.

- **Open creation (R-CONTRIB-1).** Anyone may **create a question or a claim** (request → TEMP → identity
  validation, §5). Creation is open; the **identity gate** (dedup/canonicalisation), not truth, is the filter.
- **Evidence contribution is suggestion-only (R-CONTRIB-2).** A contributor MAY only **suggest articles**
  (DOI/PMID) "to be considered". They MUST NOT write or edit a claim or an answer directly. The suggestion is
  an **input**; the result is produced by the neutral compiler (evidence-bounded + GRADE + contradiction-seeking).
  **The worst case of abuse is wasted compute, not a corrupted claim.** This is the *pull-request* model:
  you propose inputs; the transparent process decides the output. (Operationally: the reference implementation's
  DOI reading-list ingestion `--doi-file` turned outward; extends the minimal inbox R-MR-5.)
- **Attribution (R-CONTRIB-3).** Creation and suggestion are **attributable** — ORCID or another verifiable
  identity — and provenance is recorded.
- **Bring-your-own compute (R-CONTRIB-4).** Compilation MAY run on the **contributor's or institution's** AI
  key; the host stores the result and provides the protocol. This **decouples cost from the founder**.
- **Federated stewardship (R-CONTRIB-5).** A domain MAY be **stewarded** by a group (e.g. a medical society)
  that funds and curates (L2) its domain, while the host keeps the rails and the neutrality (L1 still
  *registers, not arbitrates*). This generalises the founder-steward model (R-GOV-3) to **multi-steward federation**.
- **Open standard, services around it (R-CONTRIB-6).** Sustainability comes from **services around an open
  standard**, not from owning the standard. The protocol and the **public read MUST stay open** — closing them
  would destroy the neutrality that is the entire moat. Monetisation may target enterprise consumption
  (API/analytics/evidence-surveillance, the machine-first angle); aligns with the protected-commons licence
  (Posture B, R-LIC-1).

---

## 13. Conformance

An implementation is **SCR-conformant (Level 1, Registry)** if it satisfies, for every object it publishes:

- **MUST** use the identifier format and the no-reuse, version-separated rules of §4.
- **MUST** implement the create→temp→identity-validate→final lifecycle of §5, with match-or-mint dedup.
- **MUST** honour the claim contract of §6 (PECO context, GRADE, gaps, knowledge state, verifiable reference,
  three dimensions separate, evidence permanence).
- **MUST** keep questions neutral and answers evidence-bounded, with the outcome discipline of §7.
- **MUST** produce immutable, citable, dated version snapshots (§8).
- **MUST** expose machine-readable JSON per object (§10) and keep the AI as compiler-not-author with public
  model provenance and mandatory contradiction-seeking.
- **MUST** compute and expose Knowledge Freshness with the small-base caveat (§9).
- **MUST NOT** arbitrate truth/consensus/recommendation inside L1 (the four principles, §2).

**Level 2 (Consensus)** and **Level 3 (Recommendation)** are **optional** conformance extensions layered above
a conformant L1; they MUST NOT alter or overwrite L1 records, only annotate them.

---

## 14. Relationship to existing standards (build-on, §2.3)

| Concern | SCR builds on |
|---|---|
| Persistent claim identity | nanopublications, Trusty URIs |
| Object DOIs / deposit | DataCite, Zenodo |
| Provenance | PROV-O |
| Machine-readable claim review | schema.org ClaimReview |
| Evidence certainty | GRADE |
| Contributor identity | ORCID |
| Domain identity | MONDO / ICD-11 / MeSH (and field equivalents) |

SCR adds the **layer none of them own**: the **question-centric, versioned, freshness-aware, machine-first
accumulation** of how the answer changes — the "change layer of science" (R-MIS-6).

---

## 15. Versioning & governance of the protocol itself

- This protocol is itself **versioned and citable** (its own DOI), independent of any domain's content. It is
  the **constitution** that must survive any single steward or funder (R-PROTO-2).
- The canonical, operational source of rules remains `RULES.md` (R-DOC-1). This PROTOCOL is the **public,
  disease-agnostic distillation**; where it is silent, RULES governs the reference implementation. Where the
  two ever conflict on an **interoperability** requirement, this PROTOCOL is normative for **conformance**;
  RULES remains normative for the **reference implementation's behaviour**.
- Changes to the rigid core are protocol-version bumps (`v1 → v1.1 → v2`) with a public changelog. The open
  periphery (§11) is **out of scope** and may change without a protocol bump.

---

## 16. Citation

> Scientific Claim Registry. *SCR Protocol v1 — The Open Specification for a Versioned Memory of Scientific
> Answers.* Amato ACM (ed.), ORCID 0000-0003-4008-4029. Zenodo, 2026. DOI: 10.5281/zenodo.20517114.

*Status: Draft. This specification is offered for adoption and comment; it builds on prior art and does not
claim to reinvent persistent claim identity (§2.3, §14).*
