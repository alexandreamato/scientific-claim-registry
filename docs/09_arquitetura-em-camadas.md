# SCR — "PubMed para claims": arquitetura em camadas (decisão estratégica)

> Refinamento fundador (Amato, 2026-05-30). Resolve a tensão da revisão de prior art:
> o ativo durável não é o consenso — é o **registro versionado de claims**. O SCR deve
> **registrar, não arbitrar**.

## A armadilha conceitual (e a saída)

Existem **dois produtos diferentes** escondidos dentro do BIO:

| | **Produto A — Motor de conhecimento** | **Produto B — Autoridade epistemológica** |
|---|---|---|
| O que faz | extrai claims, detecta artigos novos, liga evidências, calcula grafos, acha contradições, resume | decide: a claim está correta? que artigo pesa mais? a hipótese é plausível? mudou o estado do conhecimento? |
| Natureza | **automatizável** (IA já faz parte; fará muito mais em 5 anos) | **problema humano** — não porque humanos sejam melhores, mas porque a **sociedade exige responsabilidade** |
| Custo / sustentabilidade | barato, escalável | caro, depende de especialistas, reuniões, governança |

**A armadilha:** tentar que o BIO seja uma **Cochrane** (que *decide* → cara, dependente de
especialistas). **A saída:** ser um **PubMed para claims** — que *não julga, registra*.

> PubMed indexa (não decide) → sustentável. Consensus resume (não decide) → sustentável.
> Cochrane decide → cara, dependente de especialistas. **O SCR deve ser o PubMed dos claims.**

## Os quatro problemas que NÃO se deve resolver ao mesmo tempo

O conselho de IAs apontou o maior risco sem perceber: o BIO tentava resolver **simultaneamente**
quatro problemas distintos. Separe-os:

1. **Armazenamento** (registrar claims + relações + histórico) ← *o produto*
2. **Verdade** (a claim é correta?)
3. **Consenso** (especialistas concordam?)
4. **Recomendação clínica** (o que fazer com isto?)

Tentar (2)+(3)+(4) dentro do registro é o que torna o projeto pesado e mortal. **O SCR resolve só (1).**

## Arquitetura em camadas

```
Layer 3 — Clinical Recommendation     Sociedades médicas. Decidem conduta.        (humano, lento, caro)
Layer 2 — Consensus                   Especialistas OPCIONAIS votam/qualificam.   (humano, opcional)
Layer 1 — Scientific Claim Registry   Registra claims + Supports/Contradicts/     (AUTOMATIZÁVEL, o produto)
                                       Refines + histórico. NÃO julga.
```

**Layer 1 (o produto, primeiro):**
```
SCR-LIP-000017  "Women with lipedema have increased prevalence of joint hypermobility."
  ← novo artigo → IA detecta:  Supports   SCR-LIP-000017
  ← novo artigo → IA detecta:  Contradicts SCR-LIP-000017
  ← novo artigo → IA detecta:  Refines    SCR-LIP-000017
O registro apenas acumula histórico. Sem conselho, sem votação, sem Delphi, sem reuniões.
```
Isso **sobrevive sem governança pesada**. Consenso e recomendação são **camadas opcionais acima**,
construídas por quem quiser (sociedades, IAs, grupos) — não dentro do registro.

## A pergunta fundadora (troca decisiva)

- ✅ **"Why do scientific claims not have a persistent, adopted registry?"** — resolvível por máquinas.
- ❌ *"How do we create a living consensus?"* — depende de instituições humanas.

A primeira pergunta é o produto. A segunda é uma camada opcional que talvez nem precise existir
dentro do SCR: daqui a 10 anos, ChatGPT/Claude/Gemini poderiam **consultar o registro e gerar
consensos sob demanda**. Nesse cenário, o ativo durável **não é o consenso — é o banco de claims
versionadas**. Bancos de dados sobrevivem mais que organizações: **PubMed, GenBank, CrossRef,
ClinicalTrials.gov** persistem porque **armazenam fatos estruturados, não porque arbitram a verdade.**

## Reconciliação honesta com a revisão de prior art (`08_…`)

Um fato duro a respeitar: **já existe identidade persistente para claims — nanopublications**
(~10M, Trusty URIs). Isso **não enfraquece** esta estratégia — **fortalece**:

- **PubMed não inventou o identificador** (DOIs/PMIDs já existiam); virou **o índice adotado** sobre
  o MEDLINE. Analogamente, o SCR não precisa inventar a identidade do claim (nanopub/Trusty URI já
  dá) — precisa ser **o índice adotado, humano-acessível e organizado por domínio**, que acumula
  as relações Supports/Contradicts/Refines.
- Portanto a frase de marketing **"claims não têm identidade persistente" é imprecisa** (nanopubs).
  A versão honesta: **"claims não têm um *registro/índice adotado e universal*"** — como artigos
  não tinham antes do PubMed/MEDLINE. O gancho-pergunta continua forte; só ajusta-se a precisão.
- **Construir sobre, não reinventar:** usar Trusty URI/nanopub como substrato de ID (e DOI DataCite
  como ponte citável, modelo ORKG); emitir nanopub + ClaimReview para interoperar. A novidade do
  SCR é **ser o índice adotado, por domínio, que acumula evidência automaticamente** — não a identidade.

## O que isto muda no projeto

- **Registro-first, automação-first.** Layer 1 (registro automatizado) é o produto a construir e
  divulgar. Curadoria humana, consenso (painel Delphi) e recomendação saem do núcleo → viram
  **camadas opcionais acima**, não pré-requisitos.
- **O banco já é registry-first.** `registry/scr.db`: `evidence.stance` (supporting/contradicting/
  mentioning — **adicionar `refines`**) é exatamente o "Supports/Contradicts/Refines SCR-xxxxx";
  `relations` liga claim↔claim; `claim_versions` é o histórico. O `consensus_votes` é a **Layer 2
  opcional** — fica vazio sem prejuízo do produto.
- **Governança deixa de ser "antes da automação".** O doc de governança (`spec/governance-model.md`)
  passa a descrever a **Layer 2 opcional**, não o núcleo. O núcleo (Layer 1) precisa de regras
  mínimas (o que entra como claim, como se liga evidência), não de conselho científico.
- **Piloto de lipedema = semear a Layer 1.** Os 50 claims já são o índice inicial. O próximo passo
  natural é o **pipeline automatizado** que detecta artigos novos e propõe Supports/Contradicts/
  Refines (IA propõe; entra no histórico) — não um painel de votação.
- **Mensagem do site:** liderar por *"um registro de claims científicos que acumula evidência ao
  longo do tempo — ele registra, não arbitra"* + o modelo em camadas + a pergunta fundadora.

## Posicionamento em uma frase

> O **Scientific Claim Registry** é o **índice adotado de afirmações científicas** — o *PubMed dos
> claims*: registra cada claim com identificador persistente e acumula, ao longo do tempo, as
> evidências que a sustentam, contradizem ou refinam. Ele **não arbitra a verdade**; isso fica para
> camadas humanas opcionais acima (consenso, recomendação clínica). O ativo durável é o **banco de
> claims versionadas** — e bancos de fatos estruturados sobrevivem mais que qualquer organização.
