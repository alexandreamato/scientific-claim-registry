# BIO — Revisão de Prior Art (Mapeamento do Terreno Intelectual)

> Resposta à **ação prioritária nº 1** do conselho de IAs: *"Conduct a serious
> literature review and reposition the contribution relative to nanopublications,
> living systematic reviews, Wikidata, and GRADE."*
> Compilado em 2026-05-30 a partir de 4 frentes de pesquisa (PubMed + web).

---

## ⚠️ Veredito honesto (leia primeiro)

**Nenhum dos pilares conceituais do BIO é novo. Vários já existem em produção. E
a tese central do BIO — "claims, não artigos, como unidade; versionados; com
proveniência, consenso vivo e accountability" — já foi publicada mais de uma vez,
inclusive em abril de 2026, quase palavra por palavra.**

Isso *não* mata o BIO. Mas obriga a reposicioná-lo: **a contribuição do BIO não é
o conceito — é a execução, a integração e o domínio (lipedema).** O conselho de
IAs previu exatamente isto. A revisão confirmou.

Três achados que mudam a estratégia:

1. **O modelo de dados literal do BIO já existe e roda:** *nanopublications* (2010),
   *micropublications* (2014), *Wikidata* (statement + referência + rank + histórico),
   *CIViC* (claim com ID permanente + nível de evidência + histórico de versões +
   moderação transparente). **CIViC é praticamente o BIO, só que para variantes em câncer.**
2. **O modelo de governança que o BIO propõe já tem reconhecimento regulatório:**
   *ClinGen* é a **primeira base pública de variantes reconhecida pela FDA**, com
   painéis de especialistas, sign-off de consenso e política pública de conflito de interesse.
3. **A tese exata já está no ar:** o ensaio **"ClaimRxiv: Making Scientific Claims
   First-Class Objects"** (Mayank Kejriwal, abr/2026) propõe quase tudo que o BIO
   propõe. É um Substack não revisado por pares — ou seja, a *ideia* está publicada,
   mas ainda **não foi construída nem validada**. Essa é a brecha do BIO.

---

## Cluster 1 — Primitivos de "claim" e statements versionados

A unidade "claim como objeto endereçável, com proveniência, em grafo" é **prior art consolidado.**

| Sistema | Quem mantém | O que já implementa | Maturidade |
|---|---|---|---|
| **Nanopublications** | Tobias Kuhn / Knowledge Pixels (descentralizado) | Claim+proveniência+metadados em RDF, ID imutável (trusty URI), grafo, API/SPARQL. ~10M nanopubs. **É a ideia-núcleo do BIO, publicada em 2010.** | Ativo (2010–) |
| **Micropublications** | Clark, Ciccarese, Goble | Ontologia de claim+evidência+argumento, com relações **suporte/desafio entre asserções** (= o primitivo de evidência for/against do BIO). | Modelo (2014), nunca escalou como serviço |
| **Wikidata** | Wikimedia + WikiProject Medicine / Gene Wiki | Statement+referência+**rank** (preferido/normal/deprecated)+**histórico de versões completo**+ID persistente+SPARQL. **O match mais próximo de "statement versionado + curadoria" em produção.** | Ativo, gigante (>1.5B statements) |
| **SemMedDB / SemRep** | NLM/NIH | Extração automática de triplas claim-like do PubMed (>130M predicações). | ⚠️ **Descontinuado em dez/2024** |
| **scite.ai** | Comercial (Research Solutions) | Citações classificadas **supporting / contrasting / mentioning** (1.6B citações). O for/against em escala — mas no nível do *artigo*, não da *claim*. | Ativo (2018–) |
| **ORKG** | TIB Hannover (biblioteca nacional) | *Contribuições* estruturadas + *Comparisons* (tabelas/leaderboards), grafo RDF, versionamento, curadoria + LLM. | Ativo (2019–), institucionalmente durável |
| **SciFact / SciVer** | Allen AI (AI2) | NLP de verificação de claim: SUPPORTED/REFUTED/NEI. Benchmark, não serviço. | Dataset (2020) |
| **Hypothesis.is / W3C Web Annotation** | Hypothesis (nonprofit) / W3C | Substrato padronizado para ancorar uma asserção a um trecho de fonte. | Ativo; padrão W3C 2017 |

**Síntese:** claim-as-object, proveniência, grafo, versionamento e curadoria já são
*table stakes*. O ponto fino — onde o BIO pode contribuir — é um **score de
confiança/consenso quantitativo, por claim, que evolui com novas evidências e é
versionado**, unificando extração automática (estilo SemMedDB, hoje abandonado) com
curadoria humana (estilo Wikidata/ORKG) sobre o **mesmo objeto-claim**. Sinal de
alerta: SemMedDB foi descontinuado e Micropublications nunca virou serviço →
**o difícil não é o modelo, é manter a operação curada e viva em escala.**

---

## Cluster 2 — Bases curadas por especialistas (claim + evidência + governança)

A ideia "claim curado por especialista, com nível de evidência e governança" **já
está resolvida em domínios estreitos** — e um sistema tem aval da FDA.

| Sistema | Governança | Relação com o BIO |
|---|---|---|
| **ClinGen** | Painéis de especialistas (GCEP/VCEP), sign-off de consenso, **política pública de COI**, **1º banco reconhecido pela FDA** | É o **modelo de governança** que o BIO propõe — já com legitimidade regulatória. Escopo: genética mendeliana. |
| **CIViC** | Crowdsourcing moderado (≥2 curadores, 1 editor; editor não aprova o próprio) | **O match mais próximo do modelo de dados literal do BIO:** evidence items + assertions como entidades de 1ª classe, ID permanente, nível de evidência, **histórico de versões completo**, API GraphQL. Escopo: variantes em câncer. |
| **PharmGKB / ClinPGx + CPIC** | Consórcio de especialistas, níveis de evidência 1A–4, guidelines graduadas | Precedente maduro (20+ anos) de **asserções graduadas e governadas** + camada evidência→recomendação. |
| **Open Targets** | **Algorítmico**, não consenso humano (harmonic-sum de ~20 fontes) | Melhor da categoria em **agregação de evidência + grafo + escala**, mas deliberadamente **sem** sign-off de especialista. O BIO ≈ governança do ClinGen + grafo/escala do Open Targets (que nenhum sistema combina). |
| **Monarch Initiative** | Padrões de ontologia (HPO, Mondo) | Backbone de **grafo semântico + ID persistente + proveniência**. |
| **GO annotations + evidence codes** | Consórcio + curadores | **O blueprint histórico** de "asserção + evidência tipada + proveniência persistente". |
| **GWAS Catalog** | Curadoria manual (NHGRI-EBI) | Precedente de asserções curadas manualmente, FAIR, em escala. |
| **DisGeNET / Hetionet** | Agregação/NLP | KGs de associação gene-doença. **Alerta: DisGeNET virou freemium/comercial em 2020** (problema de sustentabilidade). |

**Síntese:** os 8 primitivos do BIO existem *em algum lugar* desta lista. O modelo
de dados está mais próximo do **CIViC**; a governança, do **ClinGen**. A governança
se divide em dois paradigmas — **consenso humano** (ClinGen/CIViC/CPIC: crível, mas
caro, lento, estreito) vs **agregação algorítmica** (Open Targets/DisGeNET: escalável,
mas sem sign-off). **Ninguém entrega governança nível-ClinGen na largura/escala do
Open Targets** — essa é a maior área branca defensável. O **modelo de crédito/incentivo
é a lacuna quase universal**: todos rastreiam contribuidores para *accountability*,
nenhum oferece **crédito acadêmico durável e citável** que recompense o curador como
uma publicação faz.

---

## Cluster 3 — Evidência viva, guidelines contínuas, grading e vigilância por IA

Campo **maduro e lotado**. "Living evidence" é metodologia nomeada desde 2014.

| Sistema | O que já faz | Lição para o BIO |
|---|---|---|
| **Cochrane Living Systematic Reviews** | Síntese contínua, re-versionada; pico de 25 LSRs de COVID | **Reusar o conceito.** Modo de falha documentado = colapso por carga de trabalho do autor e perda de financiamento (a maioria caducou). **Esse é exatamente o pitch do BIO.** |
| **Australian Living Guidelines** (NHMRC/Monash) | Guideline de AVC vivo desde 2018; Taskforce COVID: 9→176 recomendações, updates **semanais** | A implementação real mais completa de "consenso contínuo por painel". **Mas foi desfinanciada em jun/2023** apesar de funcionar → durabilidade é o problema central. |
| **MAGICapp** | Plataforma de recomendações **estruturadas, versionadas, legíveis por máquina**, GRADE nativo. Hospeda WHO, BMJ RapidRecs | **Reusar, não rebuildar.** É a camada de "recomendação viva estruturada" do BIO, já pronta. |
| **GRADE** | Padrão de certeza da evidência (Alta/Moderada/Baixa/Muito baixa) | **Adotar integralmente** em vez de inventar score de confiança. + **GRADE-ADOLOPMENT** para adaptar guidance existente. |
| **Epistemonikos / L·OVE** | ~300k revisões; matriz PICO viva com IA; repositório COVID >430k artigos | O mais próximo de "grafo vivo de evidência organizado por pergunta". |
| **Trialstreamer / RobotReviewer / ASReview / Cochrane Pipeline** | Vigilância viva de RCTs (673k indexados), extração de PICO+risco de viés, screening por active-learning, classificador (recall 0.99) + crowd | **Toda a vigilância/extração automática do BIO já existe como ferramenta open-source.** É problema de integração, não de invenção. |
| **UpToDate / DynaMed** | Conhecimento clínico mantido editorialmente há 20+ anos, GRADE (DynaMed) | **A prova comercial** de que manutenção contínua é sustentável. Mas são *caixas-pretas em prosa*, proprietárias, sem histórico público estruturado. |

**Síntese:** o pipeline inteiro já existe em pedaços. **O BIO deveria reusar GRADE,
adotar registros estruturados estilo MAGICapp e conectar as ferramentas de vigilância
existentes** — não reconstruir nada disso. O problema **não resolvido** é a
**sustentabilidade** e o **loop vigilância→consenso** (decidir *qual* recomendação
ficou obsoleta e *quem* re-julga, barato e em escala). E há área branca real em
**transparência**: consenso aberto, legível por máquina e com histórico de versões
público (os líderes comerciais são prosa fechada).

---

## Cluster 4 — "Git para ciência" e publicação alternativa

| Sistema | Relação com o BIO |
|---|---|
| **Octopus.ac** (UKRI/Jisc, A. Freeman) | O match *operacional* mais próximo de "claims, não artigos": 8 tipos de publicação encadeados (Problema→Hipótese→Método→Resultados→…). Mas são documentos narrativos, **não versionados nem legíveis por máquina**, sem consenso vivo nem métrica. |
| **ResearchEquals** (C. Hartgerink) | "Módulos de pesquisa" com DOI por etapa. Module-centric (processo), não claim-centric (asserção). |
| **Manubot** (Greene Lab) | "Workflow do GitHub para ciência": manuscrito em Markdown+Git, versionado, contínuo. Versiona *documentos*, não *claims*. |
| **OpenAlex / Semantic Scholar** | Grafos de citação/conceito (200M+ obras), substrato pronto — mas param no nível do documento/citação, não da asserção. |
| **Scholia / WikiCite** | Mostra um KG acadêmico versionado e estruturado em claims sobre Wikidata. |
| **CRediT / ORCID / Altmetric / micro-attribution** | Blocos de construção para crédito. Mas **não existe métrica de contribuição em nível de claim** implantada como padrão. |

### ⭐ A tese do BIO já foi publicada?

**Sim, repetidamente — e uma vez em abril de 2026, quase idêntica.**

1. **ClaimRxiv** — Kejriwal, "Making Scientific Claims First-Class Objects" (abr/2026).
   Propõe que *"a unidade primária não seria o artigo, mas claims individuais"*, cada
   um com *boundary conditions, evidentiary burden, provenance, confidence/uncertainty,
   counterevidence, replication status, revision history* sobre modelo estilo Wikidata,
   com métricas não-citacionais. **É a tese do BIO quase linha a linha.** Porém é um
   Substack **não revisado por pares** → a ideia está no ar, mas **não foi construída**.
   https://aiscientist.substack.com/p/claimrxiv-making-scientific-claims
2. **Nanopublications** (Groth/Gibson/Velterop 2010; Mons) — a claim como unidade
   atômica, versionável, com proveniência, **~16 anos antes**, com ecossistema vivo.
3. **Micropublications** (Clark/Ciccarese/Goble 2014) — grafo de claim+evidência+
   argumento com relações de suporte/desafio.
4. Precedentes de enquadramento: Octopus (2019), "The Scientific Paper Is Obsolete"
   (Somers, *The Atlantic* 2018), Manubot Manifesto (2019), Living Systematic Reviews
   (Elliott 2014).

---

## Matriz: o que o BIO NÃO pode reivindicar como novo

| Pilar do BIO | Já existe em | Novo? |
|---|---|---|
| Claim como objeto com ID permanente | Nanopublications, CIViC, Wikidata | ❌ Não |
| Proveniência / evidência ligada | GO, nanopubs, todos | ❌ Não |
| Evidência suporte vs contra | scite, micropublications, SciFact | ❌ Não |
| Versionamento do conhecimento | Wikidata, CIViC, MAGICapp | ❌ Não |
| Grafo de conhecimento | Monarch, Open Targets, ORKG, Hetionet | ❌ Não |
| Curadoria + governança por especialistas | ClinGen, CIViC, CPIC | ❌ Não |
| Nível de confiança/certeza | GRADE (padrão global) | ❌ Não (adotar GRADE) |
| Consenso vivo / contínuo | Living Guidelines, Cochrane LSR | ❌ Não |
| Vigilância da literatura por IA | Trialstreamer, RobotReviewer, ASReview | ❌ Não |
| "Claims, não artigos" como tese | ClaimRxiv, Octopus, nanopubs | ❌ Não |

---

## ✅ Área branca genuína do BIO (onde há contribuição defensável)

1. **Score de consenso/confiança quantitativo, por claim, que evolui no tempo e é
   versionado** — unindo extração automática + curadoria humana sobre o *mesmo* objeto.
   (scite faz no nível do artigo; GRADE não é contínuo; ninguém faz por-claim e vivo.)
2. **O loop vigilância→consenso:** automação que decide *qual claim ficou obsoleta* e
   roteia para re-validação humana leve. É o gargalo caro que mata os living reviews.
3. **Governança nível-ClinGen na largura/escala do Open Targets** — ninguém combina os dois.
4. **Modelagem de primeira classe de evidência *contraditória* por claim** (a maioria só gradua evidência de suporte).
5. **Propagação automática de retratação/revisão por um grafo de claims dependentes** —
   modelado pelas micropublications, **operado por ninguém.** A brecha mais limpa.
6. **Métrica de contribuição em nível de claim (KCS)** implantada — os blocos
   (CRediT, ORCID, micro-attribution) existem, o padrão não.
7. **O domínio: lipedema.** Nenhum dos sistemas acima cobre lipedema. O ativo real e
   difícil de copiar do autor (base de pacientes ABL/Amato Duo, consenso
   brasileiro, dados próprios) é o que dá ao BIO um caso concreto que ninguém tem.

---

## Implicações para a estratégia / próxima versão do paper

- **Reposicionar de "novo paradigma" para "integração + execução + domínio".** A
  honestidade aqui é o que torna o paper publicável (foi a crítica nº 1 do conselho).
- **Citar explicitamente** nanopublications, micropublications, Wikidata, CIViC,
  ClinGen, Open Targets, GRADE, Cochrane LSR, MAGICapp e **ClaimRxiv** na seção de Prior Art.
- **Reusar, não reinventar:** GRADE (confiança), MAGICapp (recomendação estruturada),
  Trialstreamer/RobotReviewer/ASReview (vigilância), modelo CIViC (dados), governança ClinGen.
- **Concentrar a novidade** nos itens 1, 2, 5, 6 e 7 da área branca acima.
- **O piloto de lipedema deixa de ser "prova de que o conceito existe" e passa a ser
  "prova de que a execução sustentável é possível num domínio órfão de infraestrutura".**

---

## Fontes principais (URLs reais)

**Claim primitives:** [nanopub.net](https://nanopub.net) · [Trusty URIs (ESWC 2014), arXiv:1401.5775](https://arxiv.org/abs/1401.5775) · [Micropublications, PMID 26261718](https://pubmed.ncbi.nlm.nih.gov/26261718/) · [Wikidata/Gene Wiki, DOI 10.1093/database/baw015](https://doi.org/10.1093/database/baw015) · [SemMedDB, PMID 23044550](https://pubmed.ncbi.nlm.nih.gov/23044550/) · [scite QSS, DOI 10.1162/qss_a_00146](https://doi.org/10.1162/qss_a_00146) · [ORKG, DOI 10.1145/3360901.3364435](https://doi.org/10.1145/3360901.3364435) · [SciFact, arXiv:2004.14974](https://arxiv.org/abs/2004.14974) · [W3C Web Annotation](https://www.w3.org/TR/annotation-model/)

**Curated KBs:** [ClinGen framework, PMID 28552198](https://pubmed.ncbi.nlm.nih.gov/28552198/) · [CIViC, PMID 28138153](https://pubmed.ncbi.nlm.nih.gov/28138153/) · [civicdb.org](https://civicdb.org) · [PharmGKB framework, PMID 34216021](https://pubmed.ncbi.nlm.nih.gov/34216021/) · [Open Targets, DOI 10.1093/nar/gkae1196](https://doi.org/10.1093/nar/gkae1196) · [Monarch 2024, PMID 38000924](https://pubmed.ncbi.nlm.nih.gov/38000924/) · [GO 2023, PMID 36866529](https://pubmed.ncbi.nlm.nih.gov/36866529/) · [GWAS Catalog 2023, PMID 36350656](https://pubmed.ncbi.nlm.nih.gov/36350656/) · [Hetionet, PMID 28936969](https://pubmed.ncbi.nlm.nih.gov/28936969/)

**Living evidence:** [Living SR (Elliott 2014), DOI 10.1371/journal.pmed.1001603](https://doi.org/10.1371/journal.pmed.1001603) · [GRADE (Balshem 2011), PMID 21208779](https://pubmed.ncbi.nlm.nih.gov/21208779/) · [GRADE-ADOLOPMENT, PMID 27713072](https://pubmed.ncbi.nlm.nih.gov/27713072/) · [MAGIC (Vandvik 2016), DOI 10.7326/M16-0387](https://doi.org/10.7326/M16-0387) · [Epistemonikos, DOI 10.1186/s12874-020-01157-x](https://doi.org/10.1186/s12874-020-01157-x) · [Trialstreamer, PMID 32940710](https://pubmed.ncbi.nlm.nih.gov/32940710/) · [ASReview, DOI 10.1038/s42256-020-00287-7](https://doi.org/10.1038/s42256-020-00287-7) · [livingevidence.org.au](https://livingevidence.org.au) · [magicevidence.org](https://www.magicevidence.org)

**Publishing / Git-for-science:** [octopus.ac](https://www.octopus.ac/) · [researchequals.com](https://www.researchequals.com/) · [Manubot, DOI 10.1371/journal.pcbi.1007128](https://doi.org/10.1371/journal.pcbi.1007128) · [Git for reproducibility (Ram 2013), PMID 23448176](https://pubmed.ncbi.nlm.nih.gov/23448176/) · [openalex.org](https://openalex.org) · [Scholia, arXiv:1703.04222](https://arxiv.org/abs/1703.04222) · [CRediT](https://credit.niso.org/) · [ClaimRxiv (Kejriwal, abr/2026)](https://aiscientist.substack.com/p/claimrxiv-making-scientific-claims) · ["The Scientific Paper Is Obsolete" (Somers 2018)](https://www.theatlantic.com/science/archive/2018/04/the-scientific-paper-is-obsolete/556676/)
