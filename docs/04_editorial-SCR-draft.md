# Why Scientific Claims Deserve Persistent Identifiers

### A proposal for a Scientific Claim Registry (SCR)

**Author:** Alexandre Campos Moraes Amato (Amato Duo; Associação Brasileira de Lipedema)
**Type:** Editorial / Perspective — **Draft v0.1**, 2026-05-30

> **Alvos de submissão sugeridos** (conceitual, sem dados): *JMIR*, *PLOS Digital
> Health*, *BMJ Health & Care Informatics*, *Learned Publishing*, *Patterns* (Cell
> Press), *npj Digital Medicine* (perspective). Comprimento-alvo: 1.500–2.500 palavras.
>
> Nota: este é o entregável "fácil de comunicar" — ataca a raiz do problema com uma
> única pergunta provocativa, sem exigir que toda a arquitetura do BIO esteja pronta.

---

## Abstract

Modern science assigns persistent identifiers to nearly every artifact it produces.
Papers have DOIs. Researchers have ORCIDs. Clinical trials have registration numbers.
Genetic sequences have accession numbers. Yet the **scientific claim** — the actual
assertion that science exists to establish, revise, and occasionally overturn — has
no identity of its own. It remains trapped inside the prose of publications, un-addressable,
un-versionable, and impossible to track as evidence accumulates. This editorial argues
that the absence of persistent claim identifiers is a structural gap in scientific
infrastructure, and proposes a **Scientific Claim Registry (SCR)**: a minimal, public,
human-curated registry that assigns each claim a permanent identifier, a canonical
statement with explicit context, links to supporting and contradicting evidence, and a
complete revision history. We argue this is feasible today, can begin in a single
disease domain, and would become more valuable — not less — as scientific AI matures.

---

## 1. An asymmetry hiding in plain sight

Consider what science already identifies persistently. A paper published today receives
a Digital Object Identifier the moment it appears. Its authors are disambiguated through
ORCID. If it reports a trial, that trial was registered on ClinicalTrials.gov before the
first patient was enrolled. If it deposits a sequence, that sequence enters GenBank with
an accession number. Each of these identifiers solved a real problem: papers move and
break links (DOI), author names collide (ORCID), trials were selectively reported
(registration), sequences needed to be findable and citable (accession numbers).

Now consider the one thing all of these artifacts exist to communicate — a claim:

> *"Among adult women meeting a given consensus definition of lipedema, the prevalence
> of joint hypermobility is higher than in age-matched female controls."*

This assertion has no identifier. It cannot be cited as itself; only the papers around
it can. It cannot be versioned as the evidence shifts. When a supporting study is
retracted, nothing propagates to the claim. When you ask *"when did the field begin to
believe this, and how strongly does it believe it now?"*, no system answers, because the
claim was never an object in the first place.

This is the asymmetry: **science identifies its containers, but not its contents.**

## 2. The cost of claim anonymity

Because claims have no identity, four things that should be routine are currently
impossible at scale:

1. **No tracking.** A claim cannot accumulate evidence over time, because there is
   nowhere for evidence to accumulate. Each new study is filed against a journal, not
   against the assertion it tests.
2. **No versioning.** Scientific belief evolves, but that evolution is invisible. We can
   read what an author thought in 2021 and what another thought in 2026, but we cannot
   query the trajectory of the claim itself.
3. **No propagation.** When evidence is retracted or overturned, the correction does not
   flow to the claims that depended on it. Retracted papers continue to be cited
   approvingly for years.
4. **No measurable consensus.** We speak of "the evidence suggests" and "experts agree,"
   but agreement is never attached to a stable object that could carry a confidence
   rating, a controversy index, or a record of who dissents and why.

These are not philosophical inconveniences. They are the reason clinical knowledge lags
years behind the evidence, and the reason a clinician, a researcher, and a patient
asking *"what is currently true?"* receive three different, undatable answers.

## 3. Why now

Two developments make claim identifiers timely rather than merely desirable.

First, **scale**: the biomedical literature now grows faster than any human or committee
can synthesize. Static artifacts — reviews, guidelines, consensus statements — are
obsolete on publication.

Second, and more importantly, **scientific AI**. Tools such as Consensus, Elicit,
OpenEvidence and their successors increasingly answer scientific questions by reading
across the literature. But they operate at the level of the *publication*: they re-read
the papers each time, hold no persistent memory of a claim, and cannot tell you when or
why belief changed. As these systems become primary interfaces to scientific knowledge,
the absence of a stable, curated, machine-readable substrate of claims becomes a liability.
A registry of identified claims is precisely the layer such systems could consult and
cite — *"according to SCR-LIP-000234…"* — rather than re-deriving an answer from scratch
every time. The registry does not compete with scientific AI; it is the infrastructure
that makes scientific AI accountable.

## 4. What already exists — and why it is not yet enough

Honesty about prior art is essential, because most of the building blocks exist.

- **Nanopublications** (since 2010) already model a single assertion plus its provenance
  as a citable, immutable RDF object — conceptually, the claim-as-identified-object.
- **Wikidata** stores versioned statements with references and a reliability rank, with
  full edit history and persistent identifiers.
- **CIViC** and **ClinGen** demonstrate that expert-curated, evidence-graded, governed
  claim-level knowledge works in production — ClinGen is the first publicly accessible
  variant database recognized by the FDA.
- **Cochrane Living Systematic Reviews** and living guidelines show that continuous,
  versioned synthesis is achievable.
- **GRADE** provides a mature, internationally adopted way to rate certainty of evidence.

What is missing is not another data model. It is an **adopted institution** — a registry
whose identifiers the community recognizes and uses, the way it adopted DOIs and trial
registration. Nanopublications gave us the object but never the institution; Wikidata is
general-purpose and not evidence-graded; CIViC and ClinGen are powerful but bounded to
genomics. The gap is **execution, adoption, and governance**, not concept. That is a
harder problem than technology, and a more durable one.

## 5. The proposal: a Scientific Claim Registry

We propose beginning with the smallest defensible version of the idea.

A registered claim would carry only:

- a **persistent identifier** (e.g., `SCR-LIP-000001`);
- a **canonical statement** with explicit context — population, condition, exposure,
  comparator, outcome, and methodological scope (a claim is meaningless stripped of context);
- **links to supporting and contradicting evidence**, at the level of individual studies;
- a **version history** with curator attribution, timestamp, and rationale;
- and a **certainty rating reusing GRADE** — not a novel score invented for the purpose.

Deliberately, the first version needs no artificial intelligence, no knowledge graph, and
no real-time updating. It can begin as a curated, human-maintained register. Three design
commitments matter from the start:

1. **Governance before automation.** Who may register and revise claims, how conflicts of
   interest are declared, and how disputes are resolved must be defined before any tooling
   is built. The hard problems here are social, not technical.
2. **Separate evidence, consensus, and knowledge state.** Strong evidence with low
   consensus, and high consensus with weak evidence, must remain visibly distinct. The
   registry should expose disagreement, not launder it into a single number.
3. **Human authority, AI assistance.** Automated literature surveillance may *propose*
   candidate claims and flag new evidence; experts decide. AI dependence should grow only
   as its accuracy is independently validated.

## 6. Starting where the gap is widest

Infrastructure does not begin everywhere at once; it begins where the need is acute and a
committed community exists. We propose **lipedema** as the first domain — not because it is
representative, but because it is hard: a field with a rapidly expanding and fragmented
literature, active and well-defined controversies, multidisciplinary stakes, a diagnostic
delay measured in years, and an engaged international patient community. A registry that
brings order to lipedema's contested knowledge would demonstrate the model where it is
most needed. If claim identifiers prove their worth there, the same registry — disease-
agnostic by design — can extend to lymphedema, the Ehlers–Danlos spectrum, mast cell
activation, and beyond.

## 7. A modest call

The question is deliberately narrow, and that is its strength:

> *If papers, authors, trials, and sequences all deserve persistent identifiers, why not
> the claims themselves?*

We are not proposing to replace journals, systematic reviews, or peer review. We are
proposing to give the assertion — the true unit of scientific knowledge — the same basic
dignity of identity that we long ago granted to everything that surrounds it. A Scientific
Claim Registry is a small, concrete, and overdue first step toward science that is not
only published, but kept alive.

---

*Conflicts of interest: the author founded and directs clinical and scientific
initiatives in lipedema, the proposed pilot domain. Disclosure to be completed on
submission.*
