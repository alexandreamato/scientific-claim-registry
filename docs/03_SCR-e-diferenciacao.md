# BIO — Scientific Claim Registry (SCR) e diferenciação

> Ideias novas surgidas na continuação da conversa de origem (jun/2026).
> Estas são, estrategicamente, as mais fortes de todo o projeto — e convergem
> com a "área branca" identificada independentemente na revisão de prior art
> (`02_prior-art-review.md`).

---

## 1. A separação SCR ↔ BIO (a sacada principal)

A conversa chegou a uma arquitetura mais elegante: **separar a instituição/
infraestrutura do motor/metodologia.**

| Camada | Nome | O que é |
|---|---|---|
| **Infraestrutura pública** | **SCR — Scientific Claim Registry** | O registro, o banco, os IDs persistentes das claims. Ex.: `SCR-LIP-000123` |
| **Motor / framework** | **BIO — Biological Intelligence Observatory** | A metodologia, a governança, a camada viva (consenso, grafo, vigilância, versionamento) |

> **BIO opera o SCR** — assim como CrossRef opera os DOIs e a ClinicalTrials.gov
> opera o registro de ensaios.

**Por que isso é poderoso:**

- **Comunicação imediata.** Um pesquisador entende "estamos registrando claims"
  na hora. "BIO" exige explicar arquitetura; "Registro de Claims Científicas" não.
- **Linhagem institucional.** O nome soa burocrático — e isso é uma vantagem. Os
  nomes que sobrevivem décadas são burocráticos: **PubMed, GenBank, CrossRef,
  ORCID, ClinicalTrials.gov**. Nenhum parece startup; todos parecem infraestrutura,
  e infraestrutura gera confiança.
- **Pode começar minúsculo.** Não precisa de IA, consenso, nem grafo mundial. A v1
  é literalmente uma lista de claims com ID:

  ```text
  SCR-LIP-000001
  Claim: Women with lipedema have increased prevalence of joint hypermobility.
  Status: Emerging
  Evidence: 8 supporting studies, 1 conflicting study
  Last review: 2026-05-30
  ```

  Isso por si só já é publicável e já é um registro.

**Analogias-âncora (a tese de uma frase):**

> Artigos têm DOI. Pesquisadores têm ORCID. Ensaios têm ClinicalTrials.gov.
> Sequências têm GenBank. **Por que as afirmações científicas (claims) não têm
> identificadores persistentes?**

Essa pergunta sozinha já é um editorial / palestra / artigo conceitual — e é muito
mais simples de comunicar do que toda a arquitetura do BIO.

**Sinal forte do conselho de IAs:** toda a crítica deles girou em torno de *como
definir/governar/versionar/contextualizar* claims — **nenhum disse "claims não
importam".** Todos aceitaram implicitamente a claim como objeto central. O núcleo
real do projeto talvez não seja o BIO, e sim a pergunta do DOI-para-claims.

> ⚠️ **Domínios a verificar (não comprar ainda):** scientificclaims.org,
> scientificclaimregistry.org, claimregistry.org, openclaims.org, claimscience.org,
> claimindex.org. Antes, entender melhor o ecossistema de nanopublications — e o
> melhor nome talvez ainda não tenha aparecido.

---

## 2. BIO ≠ Cochrane (o risco de virar "mais um Cochrane")

> O maior risco para o BIO é acabar virando "mais um Cochrane" — aí perde a singularidade.

| Aspecto | Cochrane | BIO |
|---|---|---|
| Unidade fundamental | Pergunta clínica | **Claim** |
| Produto final | Revisão sistemática | Grafo vivo de conhecimento |
| Atualização | Periódica | Contínua |
| Estrutura | Documento | Rede de claims |
| Governança | Grupo autoral | Comunidade versionada |
| Histórico de evolução | Limitado | **Completo** |
| Controvérsias | Sintetizadas | **Explicitamente mapeadas** |
| IA | Mínima | Assistente opcional |
| Objetivo | Síntese da evidência | **Infraestrutura do conhecimento** |

- Cochrane responde: *"O que sabemos hoje sobre X para Y?"*
- BIO responde: *"Como essa afirmação evoluiu, quais evidências a sustentam, quais
  especialistas discordam e quais claims dependem dela?"* — perguntas diferentes.

**Exemplo (glúten no lipedema):** onde a Cochrane conclui "evidência insuficiente,
fim", o BIO mantém um objeto vivo (`BIO-LIP-0042`, estado 🟡 Emerging, 68% favoráveis
/ 22% contra, conectado a HLA-DQ2/DQ8, permeabilidade intestinal, mastócitos;
trajetória 2018 Speculative → 2026 Emerging strengthening; lacuna: falta ECR
estratificado por HLA). É quase um **"prontuário da hipótese"**, não uma revisão.

> O BIO é mais uma mistura de **Cochrane + Git + Wikidata + PubMed + OpenAlex +
> ClinGen** do que uma Cochrane tradicional. O primeiro produto pode não ser um
> consenso nem um grafo — pode ser o **Claim Registry** (o que a ClinicalTrials.gov
> fez para ensaios).

---

## 3. BIO ≠ IAs científicas (Consensus.app, Elicit, Perplexity, OpenEvidence)

> "Se a resposta for 'não é melhor', então não vale a pena construir."

**BIO não compete com essas IAs — opera numa camada diferente.**

- As IAs atuais respondem *"O que a literatura diz?"* — e trabalham no nível da
  **publicação** (o artigo continua a unidade fundamental: buscam, resumem, agrupam).
- O BIO responde *"Qual é o estado atual do conhecimento?"* — no nível da **claim**.

**A analogia em camadas:**

> Consensus = Google · Wikipedia = Enciclopédia · **BIO = GitHub + Wikipedia**
> (porque nem a Wikipedia sabe *quando* mudou).

**O que as IAs atuais NÃO têm:**

1. **Memória científica persistente** — elas releem os artigos toda vez; não há
   objeto permanente. O BIO quer `BIO-LIP-000012` existindo por décadas.
2. **Histórico** — "em 2021 acreditávamos X; em 2024 surgiu Y; em 2027 abandonamos X".
3. **Controvérsia explícita** — as IAs tentam *sintetizar*; o BIO tenta *mapear o conflito*.
4. **Governança** — Consensus/Perplexity/ChatGPT têm algoritmos; o BIO teria especialistas.

**O reposicionamento decisivo** (responde à crítica "em 5 anos as IAs farão isso"):

> O problema central não é resumir artigos (NLP). É **definir claim, definir
> contexto, resolver conflitos, atribuir confiança, manter histórico e construir
> consenso** — isso é **governança**, não NLP.

E daí a narrativa muda de "BIO é uma plataforma" para:

> **BIO é a camada de conhecimento estruturado que as futuras IAs científicas irão
> consultar.** Uma IA diria: *"According to BIO-LIP-000234..."*. Você não compete
> com as IAs — você constrói a infraestrutura que elas consomem.

**O ativo mais defensável e difícil de a IA substituir:** o **versionamento da
crença científica** — transformar a evolução do conhecimento (quando a comunidade
passou a acreditar nisto? qual a trajetória da confiança?) num **objeto consultável**.
Nem PubMed, nem Consensus, nem ChatGPT, nem Cochrane fazem isso hoje.

---

## 4. Conexão com a revisão de prior art

Estas ideias **convergem com a área branca** que a revisão (`02_prior-art-review.md`)
identificou de forma independente — o que é um sinal forte de que é ali que mora a originalidade:

| Ideia nova da conversa | Item correspondente da área branca (doc 02) |
|---|---|
| SCR = registro com IDs persistentes e **adoção institucional** | Nanopublications criaram o *modelo* da claim mas nunca viraram *instituição adotada* — o gap é execução/adoção, não conceito |
| "Versionamento da crença científica" como objeto consultável | #1 da área branca: *score de consenso por-claim, vivo e versionado* |
| "Infraestrutura que as IAs consomem" | Posicionamento que evita competir com Consensus/Elicit; nenhum sistema do prior art ocupa essa camada explicitamente |
| "Por que claims não têm DOI?" | Reforça o reposicionamento de "novo paradigma" → "instituição/execução que faltava" |

**Cautela útil:** o registro de claims *como modelo* já existe (nanopublications,
CIViC, ClaimRxiv). O que **não** existe é um **registro de claims amplamente
adotado, com IDs persistentes reconhecidos pela comunidade** — exatamente como a
ClinicalTrials.gov virou obrigatória para ensaios. Esse é o alvo do SCR, e é um
problema de **governança + adoção + sustentabilidade**, não de tecnologia.

---

## 5. Implicações para os próximos passos

- **Considerar o SCR como a "porta de entrada" do projeto** (mais fácil de comunicar,
  publicar e adotar do que o BIO completo). BIO passa a ser "o operador do SCR".
- **Primeiro entregável concreto pode ser duplo:**
  1. Um **editorial/artigo conceitual curto**: *"Why scientific claims deserve
     persistent identifiers"* (a provocação DOI-para-claims) — independente e fácil de publicar.
  2. O **registro-piloto** de ~50 claims de lipedema com IDs `SCR-LIP-0000xx`
     (planilha/JSON), curadoria humana + GRADE — que também serve como a prova de execução do BIO.
- **Reforçar nos papers** as duas tabelas de diferenciação (vs Cochrane, vs IAs
  científicas) — respondem diretamente às críticas "isso já existe" e "a IA vai fazer".
