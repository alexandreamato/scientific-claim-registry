# SCR — O ecossistema de "scientific claims" (revisão profunda)

> Revisão profunda da literatura/infra de *scientific claims* (NLP, nanopublications,
> proveniência, KGs, registros), pedida após a observação de que "claims" já é objeto
> aceito em várias comunidades. Compilado 2026-05-30 (3 frentes de pesquisa). Complementa `02_prior-art-review.md`.

## ⚠️ Os dois achados que mudam o posicionamento

1. **Já existe identidade persistente para claims — chama-se nanopublication.** ~**10M+
   nanopublications** publicadas, em **16 servidores distribuídos**, cada uma com ID
   persistente verificável (**Trusty URI**, content-addressed/criptográfico), proveniência
   (PROV), atribuição por ORCID, versionamento (`npx:supersedes`) e retração assinada.
   Comercializada pela **Knowledge Pixels** (Tobias Kuhn). → **A frase "scientific claims
   have no persistent identity" é tecnicamente falsa.**
2. **A tese exata já foi publicada** (de novo): **ClaimRxiv** (Kejriwal, abr/2026) propõe
   claims como objetos de 1ª classe com proveniência, contraevidência, confiança, status de
   replicação e *revision history* — quase palavra por palavra do SCR. É um ensaio (não
   construído), mas **antecede o SCR e compartilha o pitch**.

**Conclusão honesta:** o SCR **não é novo** como "registro de claims com IDs persistentes" —
isso existe (nanopublications) e foi proposto (ClaimRxiv). A **novidade defensável** do SCR é a
**camada que ninguém combinou e mantém**: *curadoria + governança por especialistas + consenso
versionado + adjudicação de evidência contraditória, num domínio*, **construída sobre** o
substrato de identidade que já existe — não reinventando-o.

## Cluster A — NLP / verificação de claims (a comunidade que já trata "claim" como objeto)

Estabelecido: claim é objeto científico legítimo, anotável, verificável. Mas são
**benchmarks e modelos estáticos**, não um registro mantido.

| Sistema | O que é | Cita o quê do SCR |
|---|---|---|
| **SciFact** (Wadden 2020, EMNLP, arXiv:2004.14974) | 1,4k claims biomédicos + evidência SUPPORT/REFUTE/NEI. **O paper que o SCR DEVE citar e diferenciar.** | claim-as-object, evidência for/against |
| SciFact-Open (2022), SciVer (2021), HealthVer, HealthFC, COVID-Fact, PUBHEALTH, AVeriTeC, FEVER/FEVEROUS | datasets de verificação (alguns biomédicos) | idem — todos **estáticos** |
| MultiVerS/LongChecker, ARSJoint, ParagraphJoint, VeriSci | **modelos** de verificação | nada persistente |
| **SciClaim** (Magnusson 2021, EMNLP) | **esquema de grafo** para estrutura de claim (causal/comparativo/estatístico) | machine-readable structure |
| CLAIMGEN-BART (Wright 2022, ACL) | **geração** de claims atômicos verificáveis (+ negações) | como o SCR pode *extrair/gerar* claims |
| CiteWorth (Wright 2021) | detecta frases que precisam de citação | identificar claims a registrar |
| ClaimBuster (2017) | detector de claims "check-worthy" (API viva) | detecção |
| SemRep/SemMedDB | 130M+ predicações S-P-O do PubMed | **⚠️ descontinuado dez/2024** (alerta: escala sem curadoria morre) |
| Surveys: Vladika & Matthes 2023 (ACL); Dmonte 2025 | mapeiam o campo | citar para enquadrar "o que NLP fez/não fez" |

**Síntese A:** a comunidade NLP **valida a premissa** (claims são objetos). **Não** fornece:
registro persistente, governança humana, consenso vivo versionado. Risco de duplicação: o SCR
deve **consumir** essas ferramentas (gerar/extrair/estruturar claims), não reconstruí-las.

## Cluster B — Identidade, proveniência e modelos de asserção (o substrato já construído)

| Sistema | Implementa | Falta (para o SCR) |
|---|---|---|
| **Nanopublications** (Groth 2010; Kuhn) | claim-obj, **ID persistente (Trusty URI)**, proveniência, versionamento, API; ~10M, 16 servidores | **curadoria, governança, consenso** (mint é descentralizado/sem curadoria) |
| **Micropublications** (Clark/Ciccarese/Goble 2014) | claim+evidência+**argumento; relações suporte/desafio** (as mais ricas do cluster) | não virou serviço/registro em escala |
| **AIDA statements** (Kuhn 2018) | normaliza o *texto* do claim (atômico, declarativo) | usa nanopub para o resto |
| **PROV-O** (W3C 2013), **Web Annotation** (W3C 2017), **RO-Crate** (2022) | proveniência + ancoragem em fonte + empacotamento | não são registro de claims |
| **FAIR Digital Objects** + DOI/Handle/ARK | PID resolvível para unidades de conhecimento | sem governança/consenso |
| **ORKG** (TIB) | **DOIs DataCite** para contribuições/comparações, versão, curadoria | o *paper/comparação* é a unidade, não o *claim*; sem consenso/contradição |
| **Wikidata + Scholia** | statement (claim)+referências+**histórico completo**+**rank**+governança comunitária, 100M+ | consenso por *rank* editorial, não por evidência; genérico, não científico-curado |
| **scite.ai** | **supporting/contrasting/mentioning** em 1,6B citações | no nível artigo↔artigo, não do claim registrado |

**Síntese B:** o "claim como objeto identificado e versionado" **já está construído e em escala**
(nanopublications). O SCR **deve construir sobre** isso (Trusty URI para ID; opcionalmente DOI
DataCite como ponte citável, como o ORKG faz; PROV-O para proveniência; RO-Crate para empacotar).
Reinventar identificadores seria desperdício — e a Knowledge Pixels/Nanodash já oferece a pilha.

## Cluster C — KGs de claims, registros e a pergunta decisiva

**Já existe um "registro de claims científicos com IDs + versão + consenso"?**
*Proposto: sim (ClaimRxiv). Construído como sistema único integrado: não.*

- **ClaimRxiv** (Kejriwal, abr/2026) — o precedente mais próximo (ensaio). Deixa vago
  justamente o que o SCR detalha: **PID real, mecanismo de consenso, governança**.
- **Nanopublications** — substrato técnico mais próximo (IDs+proveniência+versão), **construído**.
- **ClaimsKG** (Tchechmedjiev 2019) — KG de claims *fact-checked* (28k+), mas político/geral,
  semiautomático, sem consenso científico nem PID global.
- **ClaimReview (schema.org) + Google Fact Check** — ecossistema "claim+review+referência"
  legível por máquina (geral, não-ciência; Google descontinuando no Search). **O SCR deveria
  emitir saída compatível com ClaimReview** para interoperar.
- **OpenAlex / Semantic Scholar / SciGraph** — IDs para *papers/autores/conceitos*, **nunca para
  claims** → confirma a lacuna que o SCR aponta.
- **HypER / De Waard** (2009) — ancestral intelectual: paper como rede de hipóteses+evidência com
  "knowledge states". **Living Systematic Reviews** (Elliott 2014) — consenso vivo no nível da *revisão*, não do claim.

## ✅ Reposicionamento recomendado (o que fazer com isto)

1. **Corrigir a mensagem-âncora.** Largar "*claims have no persistent identity*" (falso —
   nanopubs/Trusty URIs) e "*persistent identifiers*" como o gancho central. Liderar pela
   **lacuna real**: não existe **registro público, curado por especialistas, com consenso vivo
   e adjudicação de evidência contraditória, num domínio**. Sugestão de gancho honesto:
   > *"A maquinaria para identificar um claim já existe (nanopublications). O que não existe é um
   > registro público e curado que rastreie a evidência, as contradições e o consenso de um claim
   > ao longo do tempo. O SCR é essa camada."*
2. **Construir sobre, não reinventar.** Trusty URI (ID) + DOI DataCite (ponte citável, modelo
   ORKG) + PROV-O + Web Annotation + RO-Crate + `npx:supersedes`. Considerar parceria/uso da
   **Knowledge Pixels/Nanodash**. Emitir **ClaimReview** + nanopub para interop.
3. **Consumir o NLP, não recriá-lo.** CLAIMGEN (gerar claims atômicos), SciClaim (esquema),
   CiteWorth (detecção), SemRep (predicações) como ferramentas de *bootstrap* — a novidade do
   SCR é a camada de **curadoria/governança/consenso**.
4. **Citar e diferenciar explicitamente:** SciFact (Wadden 2020), ClaimRxiv (Kejriwal 2026),
   nanopublications (Groth 2010/Kuhn), Wikidata+Scholia, ORKG, scite, ClaimsKG, Vladika&Matthes 2023.
5. **Frase de posicionamento honesta (adotar):**
   > *"O SCR operacionaliza a visão recém-proposta mas não construída de claims como objetos de
   > 1ª classe (cf. ClaimRxiv, 2026), adicionando o que falta à infraestrutura existente — um
   > registro curado e governado que liga identificadores persistentes de claim (viáveis via
   > nanopublications) a consenso versionado e rastreio de evidência contraditória — em vez de
   > inventar a identidade persistente, que já existe."*

> **Por que isso é boa notícia (sua intuição estava certa):** quando várias áreas independentes
> (NLP, web semântica, cientometria, evidência viva) convergem para o mesmo objeto — *claims* —
> há um problema legítimo esperando infraestrutura melhor. O SCR não precisa inventar o objeto;
> precisa ser a **instituição curada** que falta sobre ele.

## Fontes-chave
[SciFact (Wadden 2020) arXiv:2004.14974](https://arxiv.org/abs/2004.14974) ·
[Vladika & Matthes 2023 (survey)](https://aclanthology.org/2023.findings-acl.387/) ·
[SciClaim (Magnusson 2021)](https://aclanthology.org/2021.emnlp-main.381/) ·
[CLAIMGEN (Wright 2022)](https://aclanthology.org/2022.acl-long.175/) ·
[Nanopublications (Groth 2010) DOI:10.3233/ISU-2010-0613](https://doi.org/10.3233/ISU-2010-0613) ·
[Trusty URIs (Kuhn 2014)](https://doi.org/10.1007/978-3-319-07443-6_27) ·
[Nanopub scale 10M+ (Giachelle 2021)](https://doi.org/10.7717/peerj-cs.335) ·
[Micropublications (Clark 2014) DOI:10.1186/2041-1480-5-28](https://doi.org/10.1186/2041-1480-5-28) ·
[ORKG PIDs arXiv:2209.08789](https://arxiv.org/abs/2209.08789) ·
[Scholia (Nielsen 2017)](https://doi.org/10.1007/978-3-319-70407-4_36) ·
[scite (Nicholson 2021) DOI:10.1162/qss_a_00146](https://doi.org/10.1162/qss_a_00146) ·
[ClaimsKG (Tchechmedjiev 2019) DOI:10.1007/978-3-030-30796-7_20](https://doi.org/10.1007/978-3-030-30796-7_20) ·
[ClaimRxiv (Kejriwal 2026)](https://aiscientist.substack.com/p/claimrxiv-making-scientific-claims) ·
[Knowledge Pixels](https://knowledgepixels.com/) ·
[SemMedDB (Kilicoglu 2012, descontinuado 2024) DOI:10.1093/bioinformatics/bts591](https://doi.org/10.1093/bioinformatics/bts591)
