# SCR / BIO — Glossário

> Vocabulário do projeto. Ideias se espalham por vocabulário — usar estes termos de forma consistente.

## Núcleo

- **SCR — Scientific Claim Registry.** A instituição/infraestrutura pública: o registro
  de claims com identificadores persistentes. Análogo a ClinicalTrials.gov, CrossRef, GenBank.
- **BIO — Biological Intelligence Observatory.** O motor/método que *opera* o SCR:
  governança, versionamento, consenso vivo, vigilância da literatura.
- **Claim (afirmação científica).** Unidade fundamental do conhecimento no SCR: uma
  afirmação significativa com contexto explícito (população, condição, exposição,
  comparador, desfecho, escopo). Possui ID persistente (`SCR-LIP-000001`).
- **Claim-centric science.** Organizar o conhecimento em torno de *claims*, não de
  *artigos* (publication-centric). Os artigos passam a ser fontes de evidência.

## Dimensões (sempre separadas)

- **Evidence Confidence (Força da evidência).** Qualidade da evidência de suporte.
  **Reusa GRADE:** High / Moderate / Low / Very low.
- **Consensus Agreement (Concordância).** Grau de concordância entre especialistas
  verificados. Ponderado por expertise e COI.
- **Knowledge State (Estado do conhecimento).** Síntese interpretativa do status da claim:
  🔴 Speculative → 🟠 Emerging → 🟡 Probable → 🟢 Established → 🔵 Foundational. **Nunca é "verdade absoluta".**

## Métricas (do framework BIO)

- **ECS — Evidence Confidence Score.** Operacionalização da força da evidência.
- **CAS — Consensus Agreement Score.** % ponderado de concordância.
- **KSI — Knowledge Stability Index.** Quão estável vs em rápida mudança está a claim.
- **Controversy Index.** Divergência + evidências conflitantes + heterogeneidade.
- **Clinical Actionability Score.** Quanto a claim muda diagnóstico/conduta.
- **KCS — Knowledge Contribution Score.** "Impact Factor 2.0": reputação por curadoria
  de claims; meta de virar métrica complementar ao H-index.

## Conceitos

- **Living Consensus (Consenso vivo).** Consenso como processo contínuo, não evento/PDF.
- **Evidence-Versioned Medicine.** Além de baseada em evidência: com histórico completo
  (quando a crença surgiu, quando mudou, quem mudou, por qual evidência).
- **Versionamento da crença científica.** Transformar a evolução do conhecimento num
  objeto consultável — o ativo mais defensável do projeto.
- **Conflito Ativo.** Marcação explícita de uma claim onde as evidências/especialistas
  divergem — sinaliza onde a ciência precisa de novos estudos.
- **Founder-steward (fundador-guardião).** Modelo de governança em que o fundador
  permanece central e legítimo (origem + ativo + convener) enquanto o conhecimento é aberto.
- **Knowledge State vs Truth.** O sistema rastreia o *estado* do conhecimento, nunca
  declara *verdade*. Consenso ≠ verdade.

## Predecessores (prior art — sempre citar)

- **Nanopublications / Micropublications.** Claim+proveniência como objeto RDF (2010/2014).
- **Wikidata.** Statements versionados com referência e rank.
- **CIViC / ClinGen / PharmGKB / Open Targets / Monarch.** Bases curadas de claims com governança.
- **Cochrane Living Systematic Reviews / Living Guidelines / MAGICapp.** Síntese viva.
- **GRADE.** Padrão de certeza da evidência (reusado pelo SCR).
- **ClaimRxiv (Kejriwal, 2026).** Proposta quase idêntica — reforça que o diferencial é execução.

---

## Atualização — modelo pergunta-cêntrico (2026-05-30)

- **Scientific Question (SQ).** O **objeto central navegável** do SCR — uma pergunta
  científica neutra (ex. `SQ-LIP-0005` "Does lipedema increase the prevalence of joint
  hypermobility?"). Estável; os claims (evidência) ficam ligados a ela.
- **Claim como evidência.** No modelo atual, o claim (`SCR-LIP-…`) é **evidência estruturada e
  versionada** ligada a uma pergunta, com papel **supporting / contradicting / refines / context**.
  É um **grafo** (um claim pode responder a várias perguntas).
- **Knowledge Freshness.** % das fontes de evidência de uma pergunta publicadas nos últimos 5
  anos. Mede o **Evidence Decay** (envelhecimento). Freshness baixa ≠ resposta errada.
- **Evidence Decay.** O envelhecimento do conhecimento; "quando uma resposta ficou desatualizada?".
  Prior art: Shojania 2007. O SCR o expõe como métrica viva por pergunta.
- **Layers (L1/L2/L3).** L1 Registry (automatizável, o produto) · L2 Consensus (opcional) ·
  L3 Recommendation (opcional). Ver `docs/09`.
- **OS da memória científica.** Reposicionamento: o SCR guarda **perguntas, claims e a evolução
  das respostas** — não a verdade, não o consenso, a **memória**.
- **Machine-first.** Cada pergunta tem JSON (`/q/<id>.json`) para LLMs/agentes: `PubMed → SCR → IA → Usuário`.
- **Registra, não arbitra.** Princípio: o SCR registra evidência e histórico; não decide a verdade.
