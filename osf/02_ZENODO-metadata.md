# Metadados para depósito no Zenodo (DOI)

> Campos prontos para criar o depósito em https://zenodo.org (ou via integração
> OSF↔Zenodo). Estabelece o DOI e a prioridade intelectual. **SCR à frente.**

## Registro-âncora (flagship)

- **Title:**
  `Scientific Claim Registry (SCR): A Framework for Persistent, Versioned, Expert-Curated Biomedical Claims`
- **Subtitle / version line:** Framework v0.2 (operated by the BIO method)
- **Authors (Creators):**
  - Amato, Alexandre Campos Moraes — *Amato Duo; Associação Brasileira de Lipedema* — ORCID: `0000-0003-4008-4029`
  - *(adicionar coautores fundadores se houver)*
- **Resource type:** Publication → *Working paper* (ou *Preprint*)
- **Version:** `0.2`
- **Publication date:** `⟨data do depósito⟩`
- **License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**)
- **Access:** Open Access
- **Language:** English

### Description (cole no campo "Description")

> Modern science assigns persistent identifiers to nearly every artifact it produces —
> papers (DOI), researchers (ORCID), clinical trials (registration numbers), genetic
> sequences (accession numbers) — yet the scientific *claim* itself has no identity.
> Claims remain trapped inside publications: un-addressable, un-versionable, and
> impossible to track as evidence accumulates.
>
> This work proposes the **Scientific Claim Registry (SCR)**: a public, versioned,
> expert-curated registry that assigns each biomedical claim a persistent identifier, a
> canonical statement with explicit context (population, condition, exposure, comparator,
> outcome, methodological scope), links to supporting and contradicting evidence, an
> evidence-certainty rating reusing GRADE, and a complete revision history. The registry
> is operated by the **BIO (Biological Intelligence Observatory)** method — its
> governance and maintenance layer.
>
> SCR is presented as a testable hypothesis: whether a claim-centric, versioned,
> expert-curated registry can maintain current biomedical knowledge better than
> publication-centric synthesis. Lipedema is proposed as the first proof-of-concept
> domain; the framework is disease-agnostic. The work explicitly builds on and
> acknowledges prior art including nanopublications, micropublications, Wikidata, CIViC,
> ClinGen, PharmGKB/CPIC, Open Targets, Cochrane Living Systematic Reviews, GRADE and
> MAGICapp; its proposed contribution is adoption, governance, and domain execution,
> not the claim primitive itself.
>
> This document establishes the conceptual foundation and priority date of the SCR/BIO
> framework. Future technical specifications, implementations, and disease-specific
> deployments will build upon the principles described herein.

### Keywords

`scientific claims` · `persistent identifiers` · `claim-centric science` ·
`biomedical knowledge` · `knowledge graph` · `living evidence` · `living consensus` ·
`evidence synthesis` · `version control` · `biomedical informatics` ·
`scientific infrastructure` · `GRADE` · `lipedema` · `nanopublications`

### Related identifiers (preencher após criar)

- *is operated by / is part of* → URL do projeto OSF
- *is supplemented by* → DOI do Editorial (se depositado à parte)

---

## Registro secundário (opcional) — o Editorial

- **Title:** `Why Scientific Claims Deserve Persistent Identifiers: A Proposal for a Scientific Claim Registry (SCR)`
- **Resource type:** Publication → *Preprint* (ou *Article* se for submetido)
- **License:** CC BY 4.0 · **Authors:** Amato, A. C. M.
- **Description:** usar o Abstract de `docs/04_editorial-SCR-draft.md`.

---

## Observações

- **ORCID:** `0000-0003-4008-4029` (Dr. Amato) — usar em todos os depósitos (ancora a autoria/prioridade).
- **Integração OSF↔Zenodo:** ao conectar, o Zenodo gera DOI automaticamente para o
  componente; alternativamente, depositar o PDF diretamente no Zenodo.
- **Versionamento:** Zenodo mantém DOI versionado — o "v0.2" pode evoluir para v0.3 com
  DOI próprio + DOI-conceito que sempre aponta para a última versão.
