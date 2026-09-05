# SCR — Rulebook (especificação canônica)

> **Documento vivo.** Consolida as regras que definimos nas conversas. Cada regra tem um
> **ID estável** (`R-AREA-n`) para referência. Quando uma regra mudar, edite-a aqui e
> registre na seção **Changelog** (não apague IDs — marque `(deprecada)`).
> Detalhamento e racional ficam nos docs numerados (`docs/NN`). Status: **[Adopted]** =
> decidida · **[Planned]** = decidida, ainda não implementada · **[Proposed]** = em aberto.
>
> **Como adicionar regra:** próximo número livre na área; frase normativa curta (MUST/SHOULD);
> link ao doc de racional; status.

---

## Meta — documentação das regras

- **R-DOC-1 [Adopted]** **Sempre que uma regra vital for definida, mencionada ou alterada em
  conversa, ela DEVE ser registrada aqui imediatamente** — com ID estável, frase normativa e
  status — e o **Changelog** atualizado. **IDs nunca são apagados** (marcar `(deprecada)`).
  Este rulebook é a **fonte canônica**; em conflito com qualquer outro doc, **ele prevalece**.

---

## 0. Identidade do projeto

- **R-MIS-1 [Adopted]** O SCR é o **registro/índice adotado de afirmações científicas** — *"o
  sistema operacional da memória científica"*. Guarda **perguntas, claims e a evolução das
  respostas**. (docs/11)
- **R-MIS-2 [Adopted]** O SCR **registra, não arbitra**. Não decide verdade, consenso nem conduta.
  (docs/09)
- **R-MIS-3 [Adopted]** Linha canônica: *"PubMed stores scientific papers. ScientificClaims.org
  stores the evolving answers to scientific questions."*
- **R-MIS-4 [Adopted]** **SCR = infraestrutura (marca pública)** · **BIO = framework/método de
  pesquisa** (o motor). (docs/03, docs/09)
- **R-MIS-5 [Adopted]** Lipedema é o **domínio-piloto**; o sistema é **disease-agnostic** por design.
- **R-MIS-6 [Adopted]** O SCR é a **"change layer of science"**: responde não só *"o que sabemos?"* mas
  *"o que mudou, e quando?"*. Linha canônica: *"ScientificClaims.org is not a database of papers. It is a
  versioned memory of how scientific answers evolve over time."* A infraestrutura é da **memória**, não da
  verdade (memória é automatizável; verdade não). A homepage **mostra uma pergunta viva**, não um manifesto.

## 1. Modelo de objeto

- **R-OBJ-1 [Adopted]** A **pergunta científica** (`SQ-…`) é o **objeto central navegável** —
  neutra e estável. (docs/10)
- **R-OBJ-2 [Adopted]** O **claim** (`SCR-…`) é **evidência estruturada e versionada** ligada a
  perguntas; **não** é a unidade de navegação. (docs/10)
- **R-OBJ-3 [Adopted]** O **artigo** (DOI/PMID) é a fonte de evidência sob o claim.
- **R-OBJ-4 [Adopted]** Claim ↔ pergunta é **grafo** (um claim pode responder a várias perguntas),
  não árvore. Papel do vínculo ∈ `supporting | contradicting | refines | context`.
- **R-OBJ-5 [Adopted]** Arquitetura em **camadas**; só a **Layer 1** precisa existir: L1 Registry
  (automatizável, o produto) · L2 Consensus (opcional) · L3 Recommendation (opcional). (docs/09)
- **R-OBJ-6 [Adopted]** **Três camadas distintas, sem confundir: Pergunta → Claims → Answer.** A
  **pergunta** (`SQ-…`) é a entidade **primária** (objeto navegável, persistente). Os **claims**
  (`SCR-…`) são o **substrato** (evidência versionada por baixo). A **answer** é uma entidade
  **DERIVADA**: uma **renderização** da literatura compilada dos claims+evidência — **não** é um objeto
  armazenado de verdade, **nem um veredito**. A resposta *atual* é re-derivada (temporária); cada mudança
  material é **congelada como uma versão imutável e citável** (R-VER-4) — é essa **trajetória versionada**
  (Answer v1→v2→v3) o diferencial central ("versioned memory of scientific answers"), e ela só é confiável
  porque o substrato é auditável: grade por fonte (R-CLM-11/13), datas (R-VER-5), proveniência de IA
  (R-AI-9). O SCR **registra a evolução; não arbitra a verdade** (R-MIS). Reflexo público: a home e o
  rótulo da resposta ("síntese renderizada, não um veredito") deixam as três camadas explícitas.
- **R-OBJ-8 [Adopted]** **Rótulos de exibição dos papéis = Consistent · Conflicting · Refining · Contextual.** As
  chaves internas do modelo de dados e do JSON-API permanecem `supporting`/`contradicting`/`refines`/`context`
  (machine-first intacto, R-MR), mas o que o humano lê é **Consistent / Conflicting / Refining / Contextual** —
  descreve a *relação da evidência com a resposta*, sem semântica de debate ("contradicting" soava adversário).
  Nuance preservada: `contradicting` (aponta para o lado oposto, ex. SQ-024) é distinto de `refines` (limita a
  generalização) — não amolecer o conflito genuíno. Render: `build_questions.py` (T), `build_site.py` (ROLE_L),
  `scrlib.ROLE_LABEL`+LEGEND. Origem: revisão externa (ChatGPT).
- **R-OBJ-7 [Adopted]** **Um achado = UM claim, ligado a várias perguntas (grafo) — não claims gêmeos.** R-OBJ-4
  diz que o claim é um grafo; na prática o loop criava **claims paralelos** porque o dedup era só por-pergunta:
  o mesmo paper relevante a outra pergunta virava claim novo em vez de **religar** o existente. Auditoria 2026-06:
  ~139 redundantes; só **4** claims sob >1 pergunta. **Conserto (2 partes):** (1) **Preventivo** — o `loop.py`
  mantém um índice `DOI→claims` global; antes de criar um claim, se o mesmo paper já é claim sob outra pergunta E
  o juiz `SYS_MATCH` confirma a **mesma afirmação**, ele **liga** o claim existente a esta pergunta (grafo) em vez
  de duplicar. (2) **Retroativo** — passe de subagentes julgou os 74 grupos de mesmo-DOI; **45 duplicados reais
  fundidos** (achados distintos do mesmo paper são mantidos — um paper legitimamente gera vários claims). Resultado:
  392→347 claims, grafo 4→44. **Cuidado canônico:** mesmo-DOI **não** implica duplicado; só a mesma *afirmação* (R-CLM-1).

## 2. Identificadores (formato)

- **R-ID-1 [Adopted]** Formato **estruturado**: `<PREFIXO>-<DOMÍNIO>-<SEQ>`.
- **R-ID-2 [Adopted]** PREFIXO: `SQ` = pergunta · `SCR` = claim.
- **R-ID-3 [Adopted]** DOMÍNIO: 2–4 letras maiúsculas (`LIP`, `LYM`, `EDS`…), **extensível**.
- **R-ID-4 [Adopted]** SEQ: inteiro ≥1, **mínimo 6 dígitos** zero-pad, **sem teto** (overflow para
  7+ dígitos permitido) → **infinito**. (docs/spec/id-allocation)
- **R-ID-5 [Adopted]** SEQ **nunca é reutilizado** (retração = tombstone, não reemissão).
- **R-ID-6 [Adopted]** Leitura **case-insensitive**, canônico em **maiúsculas**.
- **R-ID-7 [Adopted]** A **versão** (`vX.Y`) é **separada** do ID; o código-base não muda entre versões.
- **R-ID-8 [Adopted]** **O DOMÍNIO vem de um dicionário canônico** (`registry/domains.json`): código de 2–4
  letras maiúsculas, **único, estável, nunca reusado nem reaproveitado** (domínio errado/fundido = `deprecated`
  tombstone, não reciclado). O código é só um **shard de namespace sem semântica clínica**; a **identidade
  autoritativa da doença é o cross-reference** (`MONDO` / `ICD-11` / `MeSH`) — *construir sobre ontologia
  existente, não inventar* (R-HON). Cross-refs nunca são fabricados: preenchidos da fonte ou ficam `null`.
  Status do domínio ∈ `active | proposed | deprecated`. `ingest.py` lê os termos de busca desse dicionário.

> **Identidade federada (R-ID-9/10/11) — decisão de 2026-06-03, arquitetura HÍBRIDA.** Portão da Fase 4 da
> descentralização (`docs/spec/decentralization.md`). Resolve "se qualquer um roda um SCR, quem impede dois hosts
> de emitirem `SQ-CAR-000001` com sentidos diferentes?". `[Proposed]` até entrar no `PROTOCOL.md` §4–5 e ser
> implementado.

- **R-ID-9 [Proposed]** **Emissão é qualificada por host (sem mint central).** O código `SQ-LIP-000001` é
  **local à instância**; o **identificador global físico** é **`<host>/q/<código>`** (ex.:
  `scientificclaims.org/q/SQ-LIP-000001`). Cada host mint localmente, sem gargalo de uma autoridade central.
  Modelo git (hash global + branch local) / Trusty URI. Federável por construção; sem colisão entre hosts.
- **R-ID-10 [Proposed]** **A âncora de domínio é a autoridade de namespace inter-host.** Um código de domínio
  (`LIP`) só é globalmente comparável **via seu cross-ref** (MONDO/ICD-11/MeSH, R-ID-8): dois hosts usando `LIP`
  significam a mesma doença **sse** mapeiam para o **mesmo `MONDO:…`**. O **SCR não é a autoridade** do namespace
  de doenças — **delega à MONDO** (autoridade externa já global). Resolve metade do problema sem governança nova.
- **R-ID-11 [Proposed]** **Tecido único por resolução `sameAs`, não por mint central.** A "resposta única que
  evolui" é **reconstruída entre hosts** por uma camada `sameAs`: perguntas de hosts distintos com **mesma âncora
  de domínio + phrasing canônico equivalente** (estende o juiz R-Q-5 de *intra* para *inter*-host) são ligadas
  `sameAs` e resolvíveis juntas. Federação **não fragmenta** a tese; o tecido global emerge da resolução (como
  web/Wikidata sameAs, DOI, nanopub/Trusty — R-MR-2 "construir sobre"). **Pré-requisito da Fase 4.**

## 3. Ciclo de vida do código (alocação)

- **R-ALLOC-1 [Adopted]** Criar código é uma **solicitação**: o sistema emite primeiro um
  **temporário (draft)** `…-D######`; o **final** só é alocado na validação. (`db.py request`)
- **R-ALLOC-2 [Adopted]** Validação → **promote** (aloca SEQ canônico + alias TEMP→FINAL),
  **merge** (alias TEMP→existente, sem queimar número) ou **reject** (tombstone). (`db.py promote|merge|reject`)
- **R-ALLOC-3 [Planned]** O TEMP, após promote/merge, **301-redireciona para sempre** ao destino
  (alias gravado; emitir o redirect-stub no build ainda pendente). (`db.py resolve` já segue o alias)
- **R-ALLOC-4 [Adopted]** **Validar = identidade, não verdade:** bem-formado + deduplicação
  (+ sign-off humano opcional, Layer 2). O número final **não** depende de comitê.
- **R-ALLOC-5 [Adopted]** Contadores canônicos são **monotônicos** por escopo `(prefixo,domínio)`,
  semeados do maior SEQ existente; drafts têm contador próprio e são descartáveis.

## 4. Claims (unidade de evidência)

- **R-CLM-1 [Adopted]** Todo claim tem **contexto explícito** (PECO: população, condição, exposição,
  comparador, desfecho, escopo). Claim sem contexto perde sentido. (docs/spec/claim-schema)
- **R-CLM-2 [Adopted]** Certeza da evidência usa **GRADE** (high/moderate/low/very_low) — **não**
  inventar score próprio.
- **R-CLM-3 [Adopted]** **Três dimensões sempre separadas:** Evidence Confidence · Consensus ·
  Knowledge State. Nunca colapsar num número só.
- **R-CLM-4 [Adopted]** Campo **`gaps` obrigatório** (viés, reverse causation, amostra, etc.).
- **R-CLM-5 [Adopted]** Estados do conhecimento (escala de **maturidade da evidência**):
  Speculative → Emerging → Probable → Established → Foundational. **Hoje é um campo curado
  manualmente** (não calculado); o loop põe claims auto-ingeridos em `emerging`. *(Futuro possível:
  derivar de GRADE + nº de fontes + balanço de stance — decisão de design em aberto.)*
- **R-CLM-7 [Adopted]** **Ausência de evidência ≠ evidência de ausência.** Quando uma revisão não
  encontra estudo algum, o estado **NÃO** é um degrau alto da escada (nunca `Established`) — usa-se o
  estado ortogonal **`no_evidence` ("Evidence gap" / "Lacuna de evidência")**, e a resposta diz
  *"não há evidência em nenhuma direção"*, jamais um "Não" categórico. Ex.: gestrinona
  (`SQ-LIP-000016` / `SCR-LIP-000040`).
- **R-CLM-8 [Adopted]** **Nunca expor nome de arquivo local** como referência: `ref` é DOI:/PMID:/citação
  bibliográfica. `ref_link()` colapsa qualquer filename a "Sobrenome ANO"; o dado é corrigido na fonte.
- **R-CLM-10 [Adopted]** **Sistema de banimento de artigos** (curadoria humana, Layer 2 — `registry/curate.py`
  + `exclude.json`). Uma referência pode ser **banida** por categoria — `retracted | low_quality | off_topic |
  predatory | superseded | duplicate` — o que a **remove do registro** (claim órfão é apagado, R-CLM-9 não se
  aplica a *erro de ingestão* corrigido por curadoria) **e a impede de ser reingerida** (o loop lê
  `ingest.excluded_set()` e pula). **`curate.py check-retractions [--ban]`** varre todos os DOIs do registro no
  Crossref (campo `updated-by` type `retraction`) e detecta/auto-bane retratações. **Rodar é ROTINA, não
  opcional:** LaunchAgent semanal `org.scientificclaims.retractions` (domingo 04:30, `cron_retractions.sh`)
  varre → auto-bane retratados → rebuild+deploy se mudou → log em `retractions.log`. Banir por qualidade/escopo
  é decisão humana; retratação é fato auto-detectável.
- **R-CLM-11 [Adopted]** **Qualidade pesa: evidência forte OFUSCA a fraca.** Num claim com múltiplas fontes, a
  conclusão e a resposta compilada são **ponderadas pela qualidade** de cada fonte. Alta qualidade (revisão
  sistemática/metanálise, ECR, coorte prospectiva grande; GRADE high/moderate; baixo risco de viés) **supera e
  ofusca** baixíssima qualidade (relato de caso, transversal pequeno/não controlado, GRADE very_low, preprint,
  periódico predatório) sobre o MESMO ponto. Forte vs fraca em desacordo → a resposta segue a **forte**; a fraca
  é sinalizada como preliminar e nunca tem peso igual. Um monte de estudos ruins não derruba um bom. Implementado:
  `evidence[].grade` por-fonte + `SYS_COMPILE` pondera; `claim_brief` passa design/grade/risco-de-viés ao compilador.
- **R-CLM-12 [Adopted]** **Lipedema: SEMPRE buscar nos artigos do autor.** Em toda ingestão de uma pergunta do
  domínio LIP, o loop **também** busca a biblioteca curada do autor (`bib /semantic`) — inclusive em runs por
  reading-list — para que os artigos do próprio autor sejam considerados e **citados nos claims quando
  relevantes** (estende R-CLM-6: evidência do autor é preferida no domínio). Autoria é detectada (`amato_authored`,
  stem `amato_*`) e propagada à evidência. Como a ficha do `bib` traz os **resultados** (não só o abstract),
  achados enterrados no corpo (ex.: resultado ajustado nulo, p=0,141) viram claims — `fetch_dois` resolve o DOI
  pela ficha do `bib` antes do Europe PMC.
- **R-CLM-13 [Adopted]** **O grau curado humano é TETO do grade da máquina.** Para todo artigo presente na
  biblioteca curada do autor (`bib`, campo `grau`, nível Oxford N1=topo … N6=mecanismo/opinião/narrativa), o
  grade GRADE atribuído pelo LLM **não pode exceder** o teto derivado desse grau (`N1/N2→high`, `N3→moderate`,
  `N4/N5→low`, `N6→very_low`). Curadoria humana **rebaixa**, nunca eleva — uma revisão narrativa N6 jamais entra
  como `moderate`/`high`. Operacionaliza a R-CLM-11 na **entrada** (fecha o buraco do SCR-LIP-000221, em que uma
  revisão narrativa N6 da menopausa estava marcada `moderate`/supporting). **Prevenção:** `loop.py cap_grade()`
  aplica o teto em `make_claim`/`add_evidence` na ingestão. **Detecção:** `audit_quality.py` cruza todo
  `evidence[].grade` contra o `grau` do `bib` — `--fix` rebaixa super-avaliados e preenche grades faltantes
  (só abaixa/preenche, nunca sobe), e roda em modo-relatório no cron semanal (`cron_retractions.sh`) como rede
  de segurança. Guidelines/consensos (Delphi/S2k) caem para `very_low` como **evidência** — coerente com
  "consenso ≠ evidência" (R-CLM-2/3). Migração inicial: 45 evidências rebaixadas + 161 grades preenchidos.
- **R-CLM-14 [Adopted]** **Metadados de evidência são SEMPRE limpos — sanitizados na escrita.** Título, autores
  e periódico vêm do Crossref/Europe PMC com markup JATS/HTML que vaza (`<scp>`, `<i>`, `<sub>`, `<sup>`,
  `<italic>`, quebras de linha). **Todo** ponto de escrita passa pela função canônica `ingest.clean_text()`
  (remove tags + colapsa espaços) — aplicada no `enrich_evidence.py` (onde os metadados entram). O registro
  **nunca** armazena markup. Defesa em profundidade: `scrlib.clean_text()` também sanitiza no render (rótulos/
  hover/citação), então nem dado legado nem fonte nova mostram tag. Migração: 19 campos limpos (4 com tags JATS,
  ex.: `<scp>lipedema-associated</scp>` no SCR-LIP-000184). Vale também para `question.first_mention.title`.
- **R-CLM-16 [Adopted]** **O TÍTULO do artigo é padrão em toda evidência — gravado na ingestão.** Cada entrada de
  evidência carrega `title` (+ `authors`/`journal` quando há), para o hover do *Evidence over time*, as referências
  e citações sempre mostrarem **"Título — Autores (Ano)"**, nunca um DOI cru. Na origem: `loop.cite_meta(art)` injeta
  os metadados do artigo no `make_claim`/`add_evidence` (sanitizado, R-CLM-14). Backfill retroativo: `enrich_evidence.py`
  (Crossref) + fallback Europe PMC para DOIs fora do Crossref (eurrev/Clin Ter/German Med Sci). Render: `ev_label`
  cai para a `ref` só se não houver título — e refs em formato citação ("Allen & Hines, 1940") já são legíveis.
  Migração: 170 sem título (40%) → 164 enriquecidos (158 Crossref + 6 Europe PMC); restam 6 citações históricas
  completas (fallback OK). Origem: hover do timeline mostrando código cru em vez do título.
  **Não pode regredir — tripla garantia:** (1) **origem** — `loop.cite_meta` grava o título na ingestão;
  (2) **auto-cura** — o cron semanal roda `enrich_evidence.py` (Crossref+EPMC, idempotente) e dá `db.sync`;
  (3) **guard** — `enrich_evidence.py --check` falha (exit 1) e loga aviso se qualquer evidência DOI/PMID ficar
  sem título. Refs em formato citação são isentas (já legíveis).
- **R-CLM-15 [Adopted]** **PECO é preenchido na INGESTÃO, não com placeholder.** O `make_claim` criava claims com
  `population/exposure/comparator/outcome = "—"` (86% do registro ficou sem PECO — auditoria 2026-06). Conserto na
  fonte: o passo `classify` (`ingest.llm_classify`, **mesma chamada de LLM**, sem custo extra) agora retorna o PECO,
  e o `make_claim` o usa. Todo claim novo nasce com contexto PECO real (ex.: *population: women with stage II
  lipedema · exposure: tumescent liposuction · outcome: limb pain (VAS)*). `backfill_peco.py` (Sonnet) foi a
  migração única dos 338 legados; daqui pra frente é automático. Sem PECO estruturado, o claim não é localizável
  independentemente da prosa — é requisito, não enfeite.
- **R-CLM-9 [Adopted]** **Evidência é permanente; revisão é evidence-complete.** Um artigo que uma vez
  sustentou um claim **permanece para sempre** no banco (claims.json `evidence[]`; retração = tombstone,
  nunca deleção — R-ID-5). Toda **revisão/recompilação** da resposta compila sobre a **base de evidência
  acumulada inteira** (todos os claims da pergunta + TODOS os seus artigos), **re-injetada** no contexto —
  nunca só sobre os artigos novos. A deduplicação só vale para **descoberta** (artigo já indexado não é
  re-sugerido como candidato novo, evitando claim duplicado); como evidência persistida, ele entra em toda
  revisão futura. (`loop.py: claim_brief()` injeta as evidências; SYS_COMPILE exige compilar de tudo.)
- **R-CLM-6 [Adopted]** Evidência de autoria do próprio autor é **preferida** quando for sobre o domínio,
  **mas só se for sobre o domínio** (claim fora de escopo não entra). (REVIEW_v0.1)
- **R-CLM-17 [Adopted]** **Duas confianças distintas, nunca fundidas: GRADE ≠ confiança de extração.** O `grade`
  (R-CLM-11/13) mede a qualidade do **estudo** (desenho, viés). A **`extraction_confidence`** (high/moderate/low)
  mede quão bem o **sistema leu a fonte** — se o statement reflete fielmente o que o abstract diz. Um RCT
  excelente lido a partir de um abstract magro/ambíguo pode ter `grade=high` **e** `extraction_confidence=low`;
  são eixos ortogonais. O `classify` retorna ambos na mesma chamada (sem custo extra) e a evidência grava os dois;
  a página do claim mostra a confiança de leitura ao lado do GRADE. Complementa a verificação adversarial (R-AI-14):
  extraction_confidence é a **auto-avaliação** do primário; o verdict é o **veredito independente** do segundo modelo.

## 5. Perguntas e respostas

- **R-Q-1 [Adopted]** A pergunta é **neutra** (não embute conclusão).
- **R-Q-2 [Adopted]** A resposta é **cauteloso e *evidence-bounded*** ("Based on currently indexed
  evidence…"). **A IA não opina** nem declara verdade. (docs/11)
- **R-Q-3 [Adopted]** Template fixo da página de pergunta: *current answer · knowledge state · last
  updated · what changed · evidence direction · supporting/contradicting claims · major uncertainty
  · version history · key references · machine-readable JSON*.
- **R-Q-4 [Adopted]** **Estratégia de criação** (`docs/spec/creation-strategy.md`). **Pergunta = unidade de
  demanda; claim = unidade de evidência.** CLAIMS nascem do **loop** (`loop.py`) só sob perguntas existentes.
  PERGUNTAS vêm de 4 fontes: (1) **cobertura taxonômica** (eixos = tags), (2) **descoberta pela literatura**
  (LLM propõe perguntas neutras nas lacunas, **aterradas** na biblioteca — `propose_questions.py`), (3) **inbox
  humano** (R-MR-5), (4) **ferramentas externas** (Consensus/PubMed). Ciclo: proposta → **TEMP** `SQ-LIP-D######`
  → curadoria **promote/merge/reject** → **FINAL** (nasce `speculative`, `claims:[]`) → loop popula. Validar =
  identidade (neutra/única/aterrada), não verdade (R-ALLOC-4).
- **R-Q-5 [Adopted]** **Pergunta canônica + frases alternativas (phrasings); dedup semântico na camada da
  pergunta.** Cada SQ tem UM `text`/`text_pt` **canônico, estável e neutro** e uma lista `phrasings`/`phrasings_pt`
  — formas alternativas de fazer **a mesma** pergunta (a mesma resposta satisfaz todas; mesmo escopo/população/
  intenção). Evita **duplicar perguntas semanticamente iguais**: uma paráfrase vira *phrasing*, não um SQ novo.
  **Portão de canonicalização** na criação (`propose_questions.py` + `phrasings.py`, espelha o merge conservador
  de claims R-CLM-1): cada candidato é julgado contra `text`+`phrasings` das perguntas existentes (juiz LLM) →
  **same** (alta confiança ≥0.85) ⇒ **funde como phrasing** na canônica (não cria SQ); **related** ⇒ cria SQ novo
  **+ link `related`** (veja-também); **novel** ⇒ cria normal. No limiar, escolhe **related** — nunca colapsa
  perguntas distintas. **Onde paga:** busca do site casa phrasings (mais recall, sem páginas novas); `/q/<id>.json`
  e `/api/questions.json` expõem phrasings (**machine-first**: roteia qualquer formulação → SQ canônico); SEO.
  Página mostra "Também perguntada como". Backfill inicial: 3–4 phrasings bilíngues nas 25 perguntas (`add_phrasings.py`).
  Escalável: juiz LLM hoje; *embeddings-ready* (Ollama/`bib`) quando o nº de perguntas crescer.
- **R-Q-6 [Adopted]** **Perguntas (e claims) são propositadamente FOCADOS, restritos e objetivos — princípio
  estrutural.** Uma pergunta deve ser **estreita, específica, direcionada e empiricamente respondível**: uma
  **única relação** (uma exposição/intervenção × um desfecho), com **população e contexto delimitados**. É
  **PROIBIDO** criar perguntas **amplas, abertas, guarda-chuva ou subjetivas** ("o que causa o lipedema?", "como
  tratar?", "qual a melhor abordagem?"). **Quanto mais objetiva a pergunta, mais alta a qualidade dos claims:**
  o retrieval e o classify só separam o relevante do irrelevante quando o alvo é nítido (ex.: SQ-LIP-000021 —
  *"TDC reduz dor/volume em lipedema?"* — deixou o classify descartar limpo 7 papers de linfedema; uma pergunta
  ampla teria diluído tudo). **Claims também são atômicos:** uma afirmação verificável por claim (R-CLM-1).
  **Operacional:** o prompt de discovery (`SYS_PROPOSE`) exige especificidade e **rejeita** o que for amplo; uma
  lacuna ampla deve ser **decomposta** em várias perguntas estreitas, ligadas por `related` (R-Q-5). Vale para
  todas as 4 fontes de criação (R-Q-4) e para a curadoria humana. É a base da qualidade do registro — entra no
  planejamento, na estrutura e na estratégia de tudo. (Reforça R-Q-1 neutra e R-Q-4.)
- **R-Q-7 [Adopted]** **O DESFECHO é obrigatório; "eficaz/seguro" sozinho é proibido; sintomático ≠ modificador
  de doença; L1 não responde "é a solução".** Afia a R-Q-6: toda pergunta nomeia o **desfecho** (o "O" do PICO).
  "Effective / works / better / safe" sem desfecho é vago e força resposta superestimada (caso-protótipo
  SQ-LIP-000013 "liposucção é eficaz e segura?" — eficaz para *quê*? dor? volume? cura?). **Duas regras irmãs:**
  (1) **sintomático vs modificador-de-doença** sempre separados — uma intervenção pode reduzir sintoma sem alterar
  a doença, e isso deve ser dito; (2) formulação **normativa** ("é a solução / devemos fazer") é **L3
  (recomendação)**, não L1 — reformular como pergunta empírica de desfecho. **Mecanismo (escala):** (a) **resposta
  estruturada por desfecho** — para pergunta guarda-chuva navegável, o compilador emite `outcomes[]`
  {outcome, direction, confidence(GRADE), disease_modifying, note}, renderizado como "By outcome" na página + JSON;
  (b) **decompor** os piores guarda-chuvas em sub-perguntas de um desfecho (ligadas por `related`). `SYS_COMPILE`
  endurecido: nunca afirmar "effective" sem desfecho; desfecho sem evidência = "not demonstrated", não benefício
  implícito. Revisão das 25 perguntas = **auditoria de especificação-de-desfecho**.

## 6. Versionamento

- **R-VER-1 [Adopted]** Toda mudança material da resposta = **nova versão (commit)**; **sem mudança,
  sem versão nova**.
- **R-VER-2 [Adopted]** Cada versão tem **snapshot congelado, imutável e citável**
  (`/q/<id>/v<ver>.html`); a página atual (`/q/<id>.html`) **sempre resolve** para a versão corrente.
- **R-VER-3 [Adopted]** Do snapshot dá para ir à **versão atual** e ao **histórico**; o atual lista
  todas as versões.

## 7. Citação

- **R-CIT-1 [Adopted]** Cita-se a **versão** (captura o estado da evidência naquela data).
- **R-CIT-2 [Adopted]** Oferecer múltiplos formatos: **Vancouver (padrão)**, APA, Chicago, BibTeX, com botão copiar.
- **R-CIT-3 [Adopted]** Autor das citações por pergunta = **autor corporativo `Scientific Claim Registry`**
  (não o nome de uma pessoa). Bases de dados/infraestrutura são citadas pela organização (cf. ClinicalTrials.gov,
  GenBank, PubMed); isso **aumenta a citabilidade** e é mais honesto, pois as respostas são compiladas por IA.
  No BibTeX, `author = {{Scientific Claim Registry}}` (chaves duplas = autor corporativo). A **prioridade
  intelectual** do fundador é preservada pelo paper-framework com DOI `10.5281/zenodo.20466195`, não pelo
  carimbo do nome em cada página. *(Substitui o antigo "Amato ACM, ed.")*

## 8. Knowledge Freshness / Evidence Decay

- **R-FRESH-1 [Adopted]** **Knowledge Freshness** por pergunta = % das fontes de evidência dos
  **últimos 5 anos** (+ ano novo/antigo, nº de fontes). (docs/11)
- **R-FRESH-2 [Adopted]** **Freshness baixa ≠ resposta errada** — sinaliza base **envelhecendo**.
- **R-FRESH-3 [Adopted]** Exibida na página e no JSON de cada pergunta.
- **R-FRESH-4 [Adopted]** **Freshness alta ≠ robustez** — quando `pct ≥ 90` **e** `sources < 6`, a página
  exibe o badge **"small evidence base (n=…)"** (tooltip: recência, não robustez) e o JSON expõe
  `knowledge_freshness.small_base=true`. Evita ler 100% de atualidade sobre base mínima como evidência forte
  (origem: SQ-031 DXA 100%/n=4). Espelha R-FRESH-2 no outro extremo. (`site/build_questions.py:small_base_badge`)

## 9. IA e automação

- **R-AI-1 [Adopted]** A IA é **compiladora, não autora**: **propõe** (extrai claims, liga evidência,
  detecta contradições, calcula freshness, sintetiza a resposta); **nunca** decide verdade nem opina.
  Disclaimer: *"Based on currently indexed evidence, this is the best automated synthesis of this question."*
- **R-AI-2 [Adopted]** **Loop de vigilância da Layer 1 — FECHADO.** `registry/loop.py`: gather
  (biblioteca FTS + Europe PMC, `ingest.py`) → **classify (OpenAI)** stance + frase + design + GRADE →
  **verify_ref** (resolve DOI em doi.org; descarta referência suja) → promove claim novo → liga à
  pergunta → **recompila a resposta (IA compiladora, R-AI-1)** → **versiona** (snapshot da versão antiga
  congelado) → rebuild → deploy. Demonstrado: SQ-LIP-000005 → v1.1 com 2 claims reais da biblioteca.
- **R-AI-4 [Adopted]** **Nunca criar claim com referência não-verificável:** o DOI/PMID DEVE resolver
  (doi.org / PubMed); senão o candidato é descartado (não inventar nem aceitar DOI sujo de OCR/pdftotext).
- **R-AI-5 [Adopted]** Claim **auto-ingerido** carrega `provenance{auto,engine,question,source,ingested}`,
  entra como `emerging`, sem curador, `gaps` marcando "não revisado" — sinaliza que é de máquina (Layer 1).
- **R-VER-4 [Adopted]** **Versionamento é por pergunta** (`version`/`updated`/`history[]` em `questions.json`):
  adicionar/alterar claim material → bump de versão; o build (re)gera só o snapshot da versão ATUAL e
  **nunca reescreve versões passadas** (ficam congeladas em disco) → snapshots imutáveis e citáveis de fato.
- **R-VER-5 [Adopted]** **Toda claim e pergunta tem datas: `created` · `updated` (última) · `history[]`**
  (log datado de cada mudança — para claim: created + cada evidência anexada; para pergunta: cada versão).
  `loop.py` mantém (make_claim cria o log, add_evidence anexa); `add_dates.py` faz backfill idempotente.
  Exibido nas páginas (claim: "Created · Last updated" + "Change log"; pergunta: "Criado" + histórico de versões)
  e no JSON. É o requisito mínimo de rastreabilidade temporal do "registro de memória".
- **R-AI-3 [Adopted]** Curadoria humana é **opcional** (Layer 2), não requisito para o registro existir.
- **R-AI-6 [Adopted]** **LLM agnóstico de provedor** (`ingest._chat_json`): **OpenRouter** (preferencial,
  default **`anthropic/claude-opus-4.8`**) > Anthropic > OpenAI, por presença de chave
  (`~/.config/scr_openrouter_token` etc.; override `SCR_LLM_PROVIDER`/`SCR_LLM_MODEL`). **Sonnet é
  decisivamente melhor** que gpt-4o(-mini) no merge (distingue achado distinto de restatement) e na
  recompilação; usar modelo forte é requisito de qualidade, não luxo.
- **R-AI-7 [Adopted]** **Retrieval é semântico, sobre a biblioteca curada do autor.** O loop busca via
  **`bib`** (API local `http://127.0.0.1:8900`): `/semantic` (embeddings/Ollama) ranqueia por significado e
  `fichamod` carrega a **ficha estruturada exata** (objetivo/resultados/conclusão/grau/DOI) como entrada do
  classify — muito superior a FTS5 lexical. Fallback p/ `library_index` (FTS5) se a API estiver fora.
  *Diferencial vs Consensus: mesmo recall semântico, mas sobre o corpus de lipedema mais completo (o do autor),
  e com memória versionada persistente que o Consensus não tem.*
- **R-AI-8 [Adopted]** **Ingestão por lista de DOIs** (`loop.py --doi-file`): aceitar uma *reading list*
  externa (ex.: referências do Consensus) e processá-la pelo mesmo pipeline (classify→merge→compile). É o
  fluxo "ferramenta externa descobre → SCR registra/versiona".
- **R-AI-9 [Adopted]** **Proveniência de IA é pública: qual MODELO consolidou cada resposta aparece na página.**
  Toda recompilação estampa na pergunta `compiled_by {model, label, date}` (ex.: `anthropic/claude-opus-4.8` ·
  "Claude Opus 4.8"), e cada entrada de `history[]` registra o `engine` daquela versão. **Só o modelo — NÃO o
  provedor/meio de acesso** (openrouter/anthropic-API é irrelevante; o que importa é a IA). Exibido no rodapé da
  resposta — *"Consolidação por IA: Claude Opus 4.8 · <data> — limitada à evidência; a IA não opina"* — e no JSON/`/api`. Estampado por `loop.py` (`compiled_by()`/`model_label()`) nas duas recompilações
  (ingestão e `--recompile-only`); backfill nas 25 perguntas. Transparência mínima do "registro de memória": quem lê
  (humano ou agente) sabe qual IA gerou a síntese e quando, reforçando R-AI-1 (evidence-bounded, não opina).
- **R-AI-10 [Adopted]** **Ingestão de reading lists do Consensus é via SUBAGENTES (fan-out).** O Consensus MCP
  devolve 20 abstracts/busca (~6k tokens) e tem rate-limit agressivo; rodar isso no fluxo principal inunda o
  contexto e trava. **Padrão** (`docs/spec/consensus-ingestion.md`): N subagentes em paralelo, cada um com um lote
  de perguntas, fazem **descoberta** (Consensus search → filtra por menção à doença → resolve DOIs com
  `resolve_dois.py` → grava `/tmp/<SQ-ID>.dois`) **no contexto deles** e devolvem só `SQ-ID: N DOIs`. O orquestrador
  então roda `loop.py --doi-file` **em série** (escrevem o mesmo claims.json/scr.db) → build → deploy. Subagentes são
  **read-only** no registro (só /tmp). O classify do loop faz o filtro final de relevância. Mais barato e rápido que
  o fluxo direto (~130k tokens/subagente ficam fora do contexto principal). Estende R-AI-8 (reading lists de DOIs);
  usamos DOIs para ingerir dos primários, sem redistribuir a análise do Consensus.
- **R-AI-11 [Adopted]** **Anti-viés de confirmação no classify.** Sistemas de claim-verification detectam suporte
  melhor que contradição; um corpo de evidência ~100% supporting é **red flag**, não feature. Diagnóstico real:
  contradicting = **2,4%** das evidências, **18/25 perguntas com zero** contraditório. O `SYS_CLASSIFY` (ingest.py)
  agora **proíbe default 'supporting'** e exige stance preciso: **contradicting** = resultado **null/negativo/não
  significativo/falha de replicação** ou efeito oposto (um null bem-powered É contradição, não 'context');
  **refines** = suporte qualificado/após ajuste/subgrupo; **context** = on-topic mas não testa a relação (não
  diretamente informativo); **supporting** só para achado afirmativo genuíno. Na dúvida, 'context' > 'supporting'.
  **Transparência (R-SITE-13):** perguntas sem contraditório exibem aviso de possível sub-detecção. *Forward-fix*
  (vale para ingestões novas); re-varredura do passado fica para depois.
- **R-AI-12 [Adopted]** **Buscar contradição é parte do fluxo E da automação — sempre.** R-AI-11 só ajuda se o
  artigo discordante for **recuperado**; a query topo-focada (`build_query`) traz sobretudo confirmação. Por isso
  **todo run do loop** executa um **passo de busca-por-contradição** (`ingest.gather_contra`): query Europe PMC com
  termos de **null/negativo/oposição** (`"no association"`, `null`, `negative`, `"did not"`, `refute`…; janela
  temporal ampliada — nulls costumam ser antigos) **+** busca semântica "evidência contrária" na biblioteca. Roda em
  **qualquer modo** (inclusive reading-list), injetado incondicionalmente no `loop.py` (como o R-CLM-12). **Na
  automação:** o cron semanal (`cron_retractions.sh`) faz uma **varredura rotativa** de **2 perguntas/semana**
  (`loop --source all --accept 4 --commit`), ciclando as 25 (~a cada 13 semanas) — o registro caça contradição
  continuamente, sozinho. O classify (R-AI-11) rotula o que vier; quem não acha registra isso honestamente
  (caveat R-SITE-13). Custo baixo (2 loops/semana).
- **R-AI-13 [Adopted]** **Proveniência ao nível da frase (quote grounding).** Verificar que o **DOI resolve**
  (R-AI-4) prova que a *fonte existe*, **não** que a claim é **fiel** à fonte. Por isso todo item de evidência
  carrega um **`quote`**: um trecho **verbatim** (≤300 caracteres) do abstract/ficha que **fundamenta a stance e o
  statement** — copiado palavra-por-palavra, sem parafrasear/traduzir/corrigir. O grounding é **determinístico**:
  `ingest.is_grounded()` exige que o `quote` (normalizado) seja **substring exata** do texto-fonte classificado
  (quote <20 chars normalizados é fraco demais → não-grounded). Isso torna cada claim **falsificável por
  inspeção** e pega um quote alucinado **de graça, sem modelo**. Renderizado na página do claim (`evquote`).
- **R-AI-14 [Adopted]** **Verificação adversarial por dois modelos (independente).** Antes de uma evidência entrar
  como fato, um **segundo modelo, DISTINTO** do classificador primário (`ingest.verify_model_name()`, default
  por-provedor distinto do primário; `SCR_VERIFY_MODEL` força) **re-deriva a stance sozinho** e julga se o
  statement é **fiel** ao abstract (sem exagero/especificidade inventada/direção trocada). `verify_extraction()`
  combina **grounding determinístico (R-AI-13) + concordância de stance + fidelidade**: `verdict='verified'`
  **sse** grounded **E** stance concordante **E** fiel; senão `'disputed'`. Um erro de extração tem de **sobreviver
  a dois modelos distintos** para entrar como verificado. **Registra, não arbitra (R-MIS):** item `disputed`
  **nunca é descartado** — é gravado com `needs_review=true`, badge ⚠ no site, e o **compilador (R-AI-1) é
  instruído a tratá-lo como provisório** (nunca deixa um disputed conduzir/virar a resposta). Auditoria
  retroativa da evidência legada via **`verify_claims.py`** (re-verifica + backfill de quote/verdict; reproduzível
  por fontes públicas — biblioteca do autor só enriquece). Estende R-AI-4 (de "ref resolve" para "ref resolve **E**
  extração verificada").
  **Duas ALTITUDES de fidelidade (refinamento de calibração).** Um statement pertence a um *claim* que pode ter
  **múltiplas fontes** — ele legitimamente diz **mais** que qualquer fonte isolada. Checar fidelidade *por-fonte*
  como "esta fonte contém tudo?" gera falso-positivo sistemático em claims-síntese. Por isso a fidelidade é checada
  em duas altitudes: **(i) por-fonte** (`verify_extraction`) marca `faithful=false` **só** se a fonte **contradiz**
  o statement **ou** ele **deturpa/atribui-lhe** um específico (n amostral, população, método, autor, número) que ela
  não contém — *não* por dizer mais; **(ii) por-claim** (`verify_statement_integrity`) checa o statement contra a
  **UNIÃO** das fontes do claim e marca `fabricated` se há específico presente em **nenhuma** fonte (fabricação real).
  Assim: síntese multi-fonte deixa de ser falsamente sinalizada, conflito entre fontes (uma contradiz) **continua**
  pego por (i), e fabricação **continua** pega por (ii). O `combined_source_text` dá ao verificador a fonte mais
  completa (ficha PT + abstract EN) — específico só é "inventado" se ausente de ambos. Na auditoria, diferenças de
  stance de *nuance* (supporting↔refines) **não** inflam disputa (mesma regra do loop forward). Resultado por-claim
  em `claim.statement_integrity`; banner no site quando `fabricated`.

## 10. Governança e camadas

- **R-GOV-1 [Adopted]** **L1 Registry** roda sem governança pesada (regras mínimas de identidade).
- **R-GOV-2 [Adopted]** **L2 Consensus** (especialistas endossam/discordam/qualificam) e **L3
  Recommendation** (sociedades) são **opcionais, acima** do registro. (docs/spec/governance-model)
- **R-GOV-3 [Adopted]** Modelo **founder-steward**: Amato fundador/guardião da metodologia; conhecimento aberto. (docs/05)
- **R-GOV-4 [Adopted]** Transparência de conflito de interesse **quando** houver camada de consenso.
- **R-GOV-5 [Proposed]** **Resolver de referência é central por CONFIANÇA, não por força.** A camada `sameAs`
  (R-ID-11) que reconstrói o tecido único entre hosts segue uma **regra pública** (no `PROTOCOL.md`): "mesma
  âncora de domínio MONDO + phrasing canônico equivalente". O steward roda o **resolver oficial** (o mais usado),
  mas **qualquer um pode rodar o seu** seguindo a mesma regra e **auditar o oficial**. O oficial é confiável por
  padrão via a **marca** (R-LIC), **não** por monopólio da resolução. Coerente com *registra-não-arbitra*
  (R-MIS-2): o resolver **não pode decidir `sameAs` no escuro** — está preso à regra pública. Centralização
  "mole" (popularidade/confiança), reversível: se o oficial trapacear, é visível e forkável.
- **R-GOV-6 [Proposed]** **O centro irredutível = marca + edição do protocolo; a jogada de sobrevivência é
  pessoa → fundação.** Tudo o mais é descentralizado (mint de IDs R-ID-9, rodar o pipeline, contribuir
  R-CONTRIB, ler, os dados R-LIC). A **única** função que **precisa** ser central é (1) **quem detém o nome
  confiável** ("SCR", R-LIC) e (2) **quem edita a spec canônica** (`PROTOCOL.md`/`RULES.md`, R-DOC-1) — é
  **autoridade/confiança**, não infraestrutura, e concentra como em todo padrão (Linux→Linus, Python→Guido,
  Web→W3C). Não é defeito; é como protocolos funcionam. **Bus-factor desse centro:** migrar de **uma pessoa**
  (founder-steward, R-GOV-3) para uma **FUNDAÇÃO** dona da marca e guardiã da spec (modelo Linux/Python/Mozilla
  Foundation) — assim até o último centro **sobrevive ao fundador**. Fecha a preocupação "depende 100% de mim".

## 11. Legibilidade por máquina (machine-first)

- **R-MR-1 [Adopted]** Toda pergunta expõe **JSON** (`/q/<id>.json`) para LLMs/agentes. (docs/11)
- **R-MR-2 [Adopted]** **Construir sobre, não reinventar:** identidade via nanopub/Trusty URI (+ DOI
  DataCite como ponte), proveniência PROV-O, interop `ClaimReview`. (docs/08)
- **R-MR-3 [Planned]** Emitir nanopublication/ClaimReview.
- **R-MR-4 [Adopted]** **API de leitura = JSON estático** (`/api/index.json`, `/api/questions.json`,
  `/api/claims.json`, `/q/<id>.json`) — sem backend, cacheável. É a "API para os robôs de IA". (docs/spec/surveillance)
- **R-MR-5 [Adopted]** **Receber propostas = inbox mínimo** (`site/submit.php` 1-arquivo **ou** Cloudflare
  Worker) que só **enfileira**; o cérebro (validar/dedup/LLM/ID/versão) é **sempre local**. A fila fica em
  `public_html/.inbox/` (protegida, fora do `rsync --delete`).

## 12. Honestidade e prior art

- **R-HON-1 [Adopted]** **Não reivindicar falsa novidade.** A identidade persistente de claims já
  existe (nanopublications); a tese foi proposta (ClaimRxiv); NLP trata claim como objeto (SciFact);
  Epistemonikos/PICO organiza evidência por pergunta. **Sempre citar.** (docs/08)
- **R-HON-2 [Adopted]** A contribuição do SCR é **adoção + organização por domínio + acumulação
  versionada + Knowledge Freshness + machine-first**, sobre o que já existe.

## 13. Licenciamento e marca

- **R-LIC-1 [Adopted]** Postura **B (commons protegido)**: docs **CC BY 4.0**; dados **CC BY-SA/ODbL**;
  código futuro **AGPL + licença comercial dupla**; **marca registrada**; contribuições sob **CLA**. (docs/07)
- **R-LIC-2 [Adopted]** Não usar permissiva pura nem NonCommercial nos dados/código.

## 14. Site e convenções

- **R-SITE-1 [Adopted]** Canônico = **scientificclaims.org**; **scr.bio** = marca curta que redireciona.
- **R-SITE-2 [Adopted]** **Site totalmente bilíngue.** EN na raiz, PT espelhado em `/pt/` — *toda* página de
  pergunta e de claim tem versão PT (`/pt/questions.html`, `/pt/claims.html`, `/pt/q/<id>.html`,
  `/pt/q/<id>/v<ver>.html`), além das homes. Cada página declara `hreflang` (en / pt-BR / x-default) e um
  seletor de idioma que aponta para a página equivalente. O `sitemap.xml` lista os dois idiomas com `hreflang`.
- **R-SITE-7 [Adopted]** **PT automatizado.** O conteúdo PT vem de campos `*_pt` no JSON
  (`text_pt`/`current_answer_pt`/`major_uncertainty_pt` nas perguntas; `statement_pt` nos claims).
  `registry/translate.py` (OpenAI) preenche **apenas os `*_pt` faltantes** (idempotente — nunca sobrescreve
  tradução revisada) antes do build, de modo que perguntas/claims novos (ex.: do laço de vigilância) ganham PT
  automaticamente. O JSON legível por máquina (`/q/<id>.json`) é **canônico em EN** e inclui os campos `*_pt`;
  não é duplicado por idioma.
- **R-SITE-3 [Adopted]** Banco canônico = `registry/scr.db`; pipeline seeds → `db.py` → `build_questions.py`
  + `build_site.py` → `rsync` deploy. (CLAUDE.md)
- **R-SITE-4 [Adopted]** Afiliação do autor = **Amato Duo**; ORCID `0000-0003-4008-4029`; DOI conceito **10.5281/zenodo.20466195**.
- **R-SITE-5 [Adopted]** **Menu superior idêntico em todas as páginas:** `Questions · Claims · PT/EN`
  (marca → home). Sem variação por página (só o item ativo muda).
- **R-SITE-6 [Adopted]** **Sempre purgar o cache do Cloudflare após cada deploy** (senão visitantes
  veem CSS/JS antigos → página quebrada). Ver `site/deploy.md`.
- **R-SITE-8 [Adopted]** **Toda pergunta tem `tags` (categorias) + `keywords` (busca), bilíngues.** Tags = chaves
  canônicas em EN (labels PT via `TAG_PT`), exibidas como chips clicáveis (deep-link `?tag=`); keywords incluem
  sinônimos EN+PT. Expostos na página, no `<meta name="keywords">` e no JSON/API.
- **R-SITE-9 [Adopted]** **Busca e paginação são client-side, sem backend.** Índice de busca embutido em cada
  card/linha (`data-search` = id+texto+resposta+tags+keywords, minúsculo); a busca combina com o filtro por
  estado e com a **paginação** (12/pág perguntas, 15/pág claims) sobre o conjunto já filtrado. Vale p/ EN e PT.
  Para escala futura (milhares de itens) migrar para índice pré-construído (Pagefind/MiniSearch).
- **R-SITE-11 [Adopted]** **Todo claim tem página própria resolvível** `/c/<id>.html` (+ `/pt/c/`) e
  `/c/<id>.json`, mostrando todas as evidências (com link de artigo), contexto PECO, proveniência e os
  **back-links às perguntas que ele responde** (o grafo bidirecional). Reforça a tese: claim é objeto
  endereçável com identificador persistente. A pergunta segue sendo a navegação PRIMÁRIA (R-OBJ-1). A página de
  claim abre com um painel **"Claim at a glance"** (tipo · estado · GRADE · nº de fontes · perguntas que responde ·
  datas) na mesma linguagem estruturada das perguntas (R-SITE-12), com caption *"structured evidence — not a
  verdict"*. O `build_site.py` **poda automaticamente** páginas/JSON de claims removidos (banidos/merge) para o
  site nunca divergir do registro.
- **R-SITE-12 [Adopted]** **A resposta da pergunta aparece em DOIS registros** (R-OBJ-6, "answer = renderização,
  não veredito"): (1) **"Answer at a glance"** — painel **estruturado/infraestrutura** no topo (estado do
  conhecimento · evidência com contadores **linkando aos claims** que a sustentam · confiança GRADE = grau
  **predominante** das fontes, não o span inteiro · freshness · versão+data) — a view objetiva que um agente/LLM
  ou informata lê; (2) **"Current synthesis"** — a prosa compilada pela IA, rotulada *"AI-compiled — not a
  verdict"* + caption "síntese renderizada, versionada". Logo abaixo, **"What's new in vX"** destaca o último
  delta (o ativo mais original — a evolução). A confiança estruturada pode ser **mais rígida** que a prosa (ex.:
  Estado=Provável vs Confiança=very low) — é o "três dimensões separadas" (R-MIS) à mostra. Claims permanecem
  cidadãos de primeira classe (os contadores são portas para eles).
- **R-SITE-13 [Adopted]** **Resumo executivo + estabilidade + caveat de contradição** no topo da pergunta (evolui o
  "at a glance"). Resolve o "texto longo demais": **resposta em 1 linha** (primeira frase, sem boilerplate) ·
  estado · GRADE · **estabilidade** · evidência linkada · **limitação principal** (`major_uncertainty`) · **mudança
  recente** (what's new) · freshness · versão+data. **Answer Stability** é um **rótulo transparente** (New/Evolving/
  Stabilizing/Settled derivado de estado + nº de revisões; "contested" se há contraditório) — **nunca um score %
  inventado** (falsa precisão é proibida, como score GRADE inventado). **Caveat de contradição:** toda pergunta com
  **zero contraditório** exibe aviso honesto de possível sub-detecção (R-AI-11). A síntese em prosa continua abaixo
  para quem quer profundidade.
- **R-SITE-14 [Adopted]** **"Bottom line" no topo da página da pergunta** — destilação de 2 frases em linguagem
  comum (frase 1 = o que a evidência sustenta · frase 2 = o que não sustenta / permanece incerto), acima do Resumo
  executivo. Estrutura em 4 níveis: **Bottom line → Resumo executivo → Síntese completa → Claims**. O compilador
  emite `bottom_line`/`bottom_line_pt` (R-Q-7 SYS_COMPILE); backfill barato `bottom_line.py` (das respostas+outcomes
  existentes); exposto no JSON. Origem: revisão externa (ChatGPT) — "readable in 10 seconds".
- **R-SITE-15 [Adopted]** **Segundo gráfico temporal: "Answer over time"** — além de *Evidence over time* (os
  estudos), uma timeline das **versões publicadas da resposta** (`history[]`): um nó por versão, ordem cronológica,
  a atual destacada. Reforça a tese "memória versionada". `version_track()` em `build_questions.py`.
  **Linkar só o que existe (honestidade de snapshot):** um nó é **clicável apenas se o snapshot `q/<id>/v<ver>.html`
  existe em disco** (a versão atual é sempre escrita no build, logo sempre clicável). Versões antigas cujo snapshot
  nunca foi capturado — ex.: a pergunta bumpou v1.0→v1.1 na mesma sessão antes de qualquer deploy — renderizam como
  nó **não-clicável** ("snapshot not archived"), pois o texto daquela resposta **não é reconstruível** a partir dos
  seeds (só a atual + metadados do histórico ficam guardados). O mesmo vale para os links "view this version" do
  histórico textual. Evita 404. Origem: pedido do autor + 404 em SQ-042 v1.0.
- **R-SITE-16 [Adopted]** **Guard de vazamento de idioma — automático.** Como o conteúdo PT/EN é gerado por IA
  (R-SITE-7), uma recompilação/backfill pode derivar para o idioma errado (um `bottom_line_pt` em espanhol, um
  `change_pt` em inglês). `lang_check.py` (heurístico, sem LLM) varre **todos** os campos de texto de perguntas e
  claims (base EN + `*_pt`, incl. phrasings, outcomes, histórico, notas de evidência) e **falha (exit 1)** se algum
  estiver no idioma errado. Roda no **cron** (passo 2b, após a varredura de contradição, antes do build) e sob
  demanda (`python3 lang_check.py [--verbose]`). Origem: 5 vazamentos achados (3 ES + 2 EN) numa revisão de página.
- **R-SITE-17 [Adopted]** **A verificação (R-AI-14) é exposta como SELO público, por-pergunta e global.** A QA da
  evidência não pode ficar invisível: cada **pergunta** expõe um rollup (`verification_rollup`) — "N de M fontes
  verificadas de forma independente" — na glance e no **JSON** (`evidence_verification`); o **registro inteiro**
  expõe um número global no `api/questions.json`, na **index de perguntas** e na **home** (selo `verseal`, EN+PT).
  É o reflexo machine-first do diferencial: um registro de claims onde **cada evidência é verificada por um segundo
  modelo com proveniência ao nível da frase**. Disputed/unverified aparecem honestamente ao lado de verified.
- **R-SITE-10 [Adopted]** **Referências de evidência são links diretos para o artigo-fonte.** `DOI:` →
  `https://doi.org/…`; `PMID:` → `https://pubmed.ncbi.nlm.nih.gov/…`; referências bibliográficas pré-MEDLINE
  (sem identificador) ficam em texto. Helper `ref_link()` em `site/scrlib.py`; aplicado em claims.html e nas
  páginas de pergunta (claims de apoio/contra + "Key references"). Abre em nova aba (`rel=noopener`).

## 15. Dados e persistência (banco ↔ seeds)

- **R-DATA-1 [Adopted]** **O `scr.db` é o store canônico — reconstrução determinística e LOSSLESS dos seeds,
  sincronizado automaticamente, sempre da mesma forma.** Os JSON (`claims.json`, `questions.json`) são a
  **superfície de edição** (o que o loop/curadoria/site escrevem). O **banco centraliza tudo** para consulta SQL
  e é mantido em **lockstep**: cada objeto claim/pergunta é gravado **verbatim** numa coluna `raw_json` (fonte de
  verdade do export) + projeções normalizadas para query (incl. `evidence.grade`/`grade_source`, `history`,
  `question_phrasings`). **Garantias:** (1) **lossless** — `db.py export` reproduz os seeds byte-a-byte (build e
  export são inversos); (2) **automático** — **todo** tool que muda os seeds chama `db.sync()` no commit
  (`loop.py`, `audit_quality.py`, `add_phrasings.py`, `propose_questions.py`, `curate.py`) — não é passo manual;
  (3) **sem drift** — `db.sync()` = rebuild + `verify_parity()`, que **falha** se DB ≠ seeds (grava em `sync_state`).
  **Padrão único:** `python3 db.py sync` (ou `import db; db.sync()`). O banco **nunca** é editado in-place; é sempre
  um rebuild total dos seeds — reproduzível, sem estado oculto. Comando de auditoria: `db.py verify`. Origem: o DB
  havia ficado órfão (50 claims/18 perguntas vs 240/25 nos JSON) porque o ferramental virou JSON-first; R-DATA-1
  fecha esse buraco tornando o sync padronizado e inquebrável.

## 16. Protocolo aberto e contribuição federada (sustentabilidade)

> Núcleo da virada estratégica de 2026-06-02: **o SCR é um protocolo (núcleo rígido mínimo), não a curadoria de
> toda a ciência.** Destilado em **`docs/spec/PROTOCOL.md` (SCR Protocol v1)** — a "constituição" disease-agnostic
> e citável. Estas regras estão **[Proposed]** (decisão de direção tomada; implementação pendente).

- **R-PROTO-1 [Proposed]** **Núcleo rígido vs periferia aberta.** Existe um **SCR Protocol** = subconjunto mínimo,
  disease-agnostic e versionado das regras (modelo de objeto, identificadores, alocação, contrato de claim,
  versionamento, freshness, machine-first, proveniência/neutralidade, as 4 regras inegociáveis). **Tudo o resto**
  — qual domínio, qual IA, qual fonte de retrieval, profundidade de curadoria, quem paga o compute, qual idioma —
  é **periferia aberta e plural**, fora do protocolo. Regras do piloto lipedema (ex.: R-CLM-12/R-AI-7 biblioteca
  do autor) são **escolhas da implementação de referência, não requisitos do protocolo**. Modelo mental:
  *o protocolo é o "git" das respostas científicas; um host (scientificclaims.org) é o "GitHub"*.
- **R-PROTO-2 [Proposed]** **O protocolo é a constituição que sobrevive ao fundador** — congelado como spec
  autônoma com **DOI próprio** (**10.5281/zenodo.20517114**, publicado 2026-06-02), separado do conteúdo de qualquer domínio. `PROTOCOL.md` é a destilação pública;
  `RULES.md` (R-DOC-1) segue canônico para a implementação de referência. Em conflito de **interoperabilidade**,
  o PROTOCOL é normativo para **conformância**; RULES é normativo para o **comportamento da referência**.
- **R-CONTRIB-1 [Proposed · protótipo `submit.py`]** **Criação é aberta.** Qualquer pessoa/grupo pode **criar uma
  pergunta ou claim** (solicitação → TEMP → validação de **identidade**, R-ALLOC). O portão é **identidade
  (dedup/canonicalização), não verdade** (R-ALLOC-4). Falha de match degrada suave: cria duplicata, dedup conserta
  depois (R-OBJ-7). Protótipo: `submit.py question` usa `phrasings.judge_same` — duplicata→link p/ SQ existente;
  novel→cunha TEMP `SQ-<DOM>-Dnnnnnn`.
- **R-CONTRIB-2 [Proposed · protótipo `submit.py`]** **Contribuição de evidência é SÓ sugestão de artigo.** Um
  contribuidor só pode **sugerir artigos (DOI/PMID) "a considerar"** — **nunca** escrever/editar claim ou resposta.
  A sugestão é **input**; o resultado é compilado pelo processo neutro (evidence-bounded + GRADE + busca de
  contradição, R-AI-12). **Pior caso de abuso = compute desperdiçado, não claim corrompido** — é o modelo
  *pull-request*, e é o que torna a abertura segura sem quebrar "registra não arbitra". **Invariante do protótipo:
  `submit.py` NUNCA escreve no registro publicado — só na fila `submissions.json`;** o conteúdo só entra via o loop
  neutro no `submit.py process`. Operacional: o `--doi-file` (R-AI-8) virado para fora; estende o inbox mínimo (R-MR-5).
- **R-CONTRIB-3 [Proposed · protótipo `submit.py`]** **Contribuição é atribuível** — ORCID (formato validado) na
  criação/sugestão; proveniência registrada na fila e em `question.contributors`.
- **R-CONTRIB-4 [Proposed · protótipo `submit.py`]** **Compute distribuído (BYO-compute).** A compilação pode rodar
  com a chave de IA do **contribuidor/instituição**; o host guarda o resultado e provê o protocolo. **Desacopla o
  custo do fundador** — é o que evita que a ideia "fique parada". Protótipo: `submit.py process` invoca o loop com
  o modelo configurado no ambiente (`SCR_LLM_MODEL`/chave do contribuidor). **Pendente:** superfície web pública
  (form + fila) — hoje é CLI local.
- **R-CONTRIB-5 [Proposed]** **Stewardship federado.** Um domínio pode ser **apadrinhado** por um grupo (ex.:
  sociedade médica) que financia e cura (L2) seu domínio, enquanto o host mantém os trilhos e a neutralidade (L1
  segue *registra-não-arbitra*). Generaliza o founder-steward (R-GOV-3) para **multi-steward**. Prova de tese =
  **um domínio não-Amato** stewarded por terceiro (ex.: `SQ-CAR-…`) — vale mais que mais perguntas de lipedema.
- **R-CONTRIB-6 [Proposed]** **Padrão aberto + serviços em volta — NÃO fechar o protocolo.** Sustentabilidade vem
  de serviços **ao redor** de um padrão aberto, não de ser dono dele (HTTP/git/DOI/ORCID venceram abertos).
  Fechar o protocolo **mata a neutralidade que é o moat**. O protocolo e o **read público ficam abertos para
  sempre**; monetização possível no **consumo enterprise** (API/analytics/vigilância de evidência, ângulo
  machine-first). Alinha Postura B (R-LIC-1).

---

## Changelog

- **2026-06-12** — **R-SITE-17 [Adopted]: verificação como selo público (camada 1 do plano de capitalização).** Toda a
  QA de verificação (R-AI-13/14) estava invisível por-evidência. Agora: rollup por-pergunta (`verification_rollup` em
  `build_questions.py`) na glance + no JSON (`evidence_verification`); número global no `api/questions.json`, na index de
  perguntas e na home (selo `verseal` EN+PT via `build_home.py`). Estado publicado: **416/423 verificadas, 0 disputed, 7
  unverified** (pilot 98%). Também: **fechados os 50 disputed** da auditoria completa — 19 por stance (verificador), 31 por
  fidelidade em 5 lotes (síntese tolerada c/ nota, contaminação cross-paper corrigida, falsos-positivos identificados).
- **2026-06-10** — **R-AI-14: grounding é ENRIQUECIMENTO, não árbitro (calibração na auditoria completa, 42 perguntas).**
  Auditadas todas as 423 evidências: 62% das disputas eram `stance_agreed=True ∧ faithful=True ∧ grounded=False`
  — o verificador (que leu a fonte) **confirmava o conteúdo**, mas o quote falhava o casamento de substring exata
  (formatação/idioma/span não-verbatim). Isso afogava a revisão humana com itens corretos. Conserto: **`disputed`
  só quando o CONTEÚDO falha** (stance diverge **ou** não-fiel); `quote_grounded` vira **flag de qualidade**, não
  veto. O site só exibe o quote quando `grounded` (garantia verbatim honesta). Re-derivado dos dados já gravados,
  **sem nova chamada LLM** (veredito = função pura de stance_agreed/faithful/grounded). Efeito global: disputed
  144→**53** (12,5%, alinhado à pergunta calibrada), verified 272→**363**; 91 flips disputed→verified. Restam 53
  disputas legítimas (não-fiel/stance/contradição/stance-legado-'unclassified') + **13 claims com fabricação** real
  (integridade por-claim). Fecha a calibração do item 1 em escala.
- **2026-06-10** — **R-AI-14 refinado: fidelidade em DUAS ALTITUDES (calibração do piloto SQ-LIP-000001).** A auditoria
  da 1ª pergunta revelou que a checagem de fidelidade *por-fonte* ("a fonte contém tudo?") gerava falso-positivo em
  claims-síntese (statement legitimamente diz mais que uma fonte só) e contra abstracts fracos (consenso Delphi só de
  metodologia). Conserto: **(i)** o verificador por-fonte (`verify_extraction`/`SYS_VERIFY`) agora marca `faithful=false`
  **só** por **contradição** ou **deturpação/atribuição** de específico a *esta* fonte — não por dizer mais; **(ii)** nova
  checagem **por-claim** (`verify_statement_integrity`/`SYS_INTEGRITY`) contra a **união** das fontes pega **fabricação**
  (específico em nenhuma fonte). `combined_source_text` dá ficha PT + abstract EN ao verificador (corrige o falso
  "inventou '46 women'" que estava no abstract EN). Auditoria deixa de inflar disputa por nuance de stance. Render:
  `claim.statement_integrity` + banner. Efeito medido na SQ-LIP-000001: verified 17→20, disputed 14→9 (restantes =
  síntese/fonte-fraca/conflito real, todos legítimos). Também: correções editoriais de calibração (264 atribuição;
  001 de-dup; **bugs de stance** 128 contradicting→supporting, 397 contradicting→context).
- **2026-06-10** — **R-AI-13 + R-AI-14 + R-CLM-17 [Adopted]: verificabilidade da claim (item 1 da revisão de melhorias).**
  O ponto único de falha era "uma IA classifica stance/claim, verificado só por 'o DOI resolve'". Conserto:
  **(R-AI-13)** proveniência ao nível da frase — toda evidência carrega um `quote` **verbatim** do abstract, com
  grounding **determinístico** (`ingest.is_grounded`, substring exata) que pega quote alucinado sem modelo;
  **(R-AI-14)** verificação **adversarial por um segundo modelo distinto** (`verify_extraction`) que re-deriva a
  stance e julga fidelidade — `verdict='verified'` só se grounded + stance concordante + fiel, senão `disputed`
  (gravado com `needs_review`, badge ⚠, compilador trata como provisório; **registra, não arbitra** — nunca deleta);
  **(R-CLM-17)** `extraction_confidence` (qualidade da **leitura**) separada do GRADE (qualidade do **estudo**).
  Implementação: `ingest.py` (`_chat_json` aceita model override; `verify_model_name`/`DEF_VERIFY`; `quote`+
  `extraction_confidence` no contrato do classify; `is_grounded`+`verify_extraction`), `loop.py`
  (`_evidence_entry` carrega os campos; verifica cada item antes de entrar; compilador ciente de `verified`),
  `schema.sql`+`db.py` (colunas `quote/extraction_confidence/verified/verify_verdict/verify_json`), `build_site.py`
  (badge verified/needs-review/unverified + quote `evquote`), **novo `verify_claims.py`** (auditoria retroativa da
  evidência legada, backfill, reproduzível por fontes públicas). Legado: 423 evidências entram como `unverified`
  até `verify_claims.py` rodar. Estende R-AI-4 ("ref resolve" → "ref resolve **E** extração verificada").
- **2026-06-03** — **Fluxogramas atualizados** (`docs/spec/methodology.md` + `rendered/`, SVG+PNG re-renderizados
  via `mmdc`): diagrama 1 (rótulos Consistent/Conflicting/Refining/Contextual + grafo cross-pergunta + resposta =
  bottom line→exec→outcomes→claims); diagrama 2 (busca de contradição R-AI-12, dedup cross-pergunta R-OBJ-7,
  título/PECO na ingestão R-CLM-15/16, outcomes+bottom_line no recompile); diagrama 4 (cron com guards de título
  R-CLM-16 e idioma R-SITE-16 + varredura de contradição); **novo diagrama 5 — porta de contribuição** (R-CONTRIB,
  `submit.py`, "nunca escreve no registro"). Pequenos ajustes pré-GitHub: `.env.example` com `SCR_DEPLOY_SSH`
  placeholder; `site/deploy.md` alinhado a `SCR_CF_TOKEN`.
- **2026-06-03** — **Fase 1 (portabilidade) fechada — ajustes de execução** (revisão externa): `.env.example`
  criado; segredos padronizados no esquema **`SCR_*`** com cascata `SCR_* → vendor → ~/.config` (`ingest.py`,
  cron `SCR_CF_TOKEN`); `.gitignore` passa a ignorar **`registry/scr.db`** (decisão: DB não-versionado, rebuild
  via `db.py build`); `RUNBOOK.md` reescrito com **cold-start §0**, **build-local separado de deploy-oficial**
  (deploy exige creds do maintainer) e **caminhos relativos** (removidos `file://`/absolutos que vazavam o path e
  quebravam fora do Mac). Núcleo confirmado **stdlib-only**; única dep = Pillow. Falta só `git init`+push.
- **2026-06-03** — **Governança do federado (R-GOV-5/6 `[Proposed]`).** **R-GOV-5:** o resolver `sameAs` oficial é
  central por **confiança, não força** — segue regra pública, qualquer um roda o seu e audita o oficial; confiável
  via marca, não por monopólio (coerente com registra-não-arbitra). **R-GOV-6:** o **centro irredutível = marca +
  edição da spec** (autoridade/confiança, não infra, como todo padrão); a jogada de sobrevivência é migrar esse
  centro de **pessoa → fundação** (modelo Linux/Python/Mozilla), fechando o "depende 100% de mim". Origem: pergunta
  do autor "tem algo centralizado no final? / eu que mando no resolver?".
- **2026-06-03** — **Mapa de descentralização + identidade federada.** `docs/spec/decentralization.md` (fases
  laptop→portável→server→federável; custos/obstáculos) revisado externamente e endurecido: Fase 1 com checklist
  (RUNBOOK/.env.example/`scr.db` não-versionado/cold-start/segredos via `os.environ`), Fase 2 com trilho
  **staging→guard→publish** (guard falho aborta), Fase 3 com **fila isolada + aprovação humana** (anti
  prompt-injection/spam/corrupção). **Decisão arquitetural — namespaces globais (portão da Fase 4): HÍBRIDA** →
  **R-ID-9** (emissão host-qualificada, sem mint central), **R-ID-10** (âncora MONDO = autoridade inter-host),
  **R-ID-11** (tecido único por resolução `sameAs`) `[Proposed]`; refletida no `PROTOCOL.md` §4. Origem: revisão
  externa apontando que federar sem resolver namespaces gera forks incompatíveis.
- **2026-06-02** — **Varredura de vazamento de idioma (PT/EN/ES) — site inteiro.** (1) `bottom_line_pt` em
  **espanhol** em SQ-008/012/025 (backfill Sonnet derivou) → prompt do `bottom_line.py` endurecido (PT-BR
  explícito, "NEVER Spanish", exemplos evidência≠evidencia / o lipedema≠la lipedema) e regenerados. (2) Varredura
  abrangente (perguntas+claims, todos os campos `*_pt`/EN incl. phrasings, outcomes, histórico, evidências) achou
  **2** `history.change_pt` em **inglês** (SQ-013 v1.2, SQ-018 v1.1) → traduzidos. **Resultado: 0 campos com idioma
  suspeito.** Relaciona R-SITE-7 (PT automatizado).
- **2026-06-02** — **Limpeza pré-GitHub:** removidos 2 claims **off-domain** (lymphedema/BCRL, órfãos:
  SCR-LIP-000377/000384) → **347→345**; SCR-LIP-000103 (lipedema, órfão) ligado a SQ-020 (recompilada v1.5);
  **14 evidências sem grade** receberam grade conservador capeado por desenho (`grade_source=cleanup_default`);
  README/CLAUDE.md sincronizados (345/42); `claim_audit_2026-06.md` marcado HISTÓRICO/remediado; **`.gitignore`**
  criado (caches, `*.bak*`, logs, segredos); caches `__pycache__`/`.DS_Store` removidos. Estado: **0 órfãos · 0
  evidências sem grade · 100% PECO · 100% títulos**. Token Zenodo confirmado fora do repo.
- **2026-06-02** — **Revisão externa (ChatGPT) — 3 melhorias na página da pergunta:** **R-OBJ-8** rótulos
  Consistent/Conflicting/Refining/Contextual (chaves de dados intactas); **R-SITE-14** "Bottom line" de 2 frases no
  topo (compilador emite `bottom_line`; backfill `bottom_line.py` nas 42; no JSON); **R-SITE-15** 2º gráfico
  "Answer over time" (timeline das versões publicadas da resposta). Também R-CLM-16 reforçada (título via
  `cite_meta` na ingestão + guard) e SQ-001 first_mention corrigido (Allen & Hines 1940).
- **2026-06-02** — **`submit.py` — protótipo da porta de contribuição** (realiza R-CONTRIB-1…4): CLI local com
  `question` (portão de identidade via `judge_same` → link p/ existente ou TEMP), `suggest` (DOI/PMID verificado
  a resolver → fila), `list`, `process` (promove TEMP→final e entrega sugestões ao loop neutro, BYO-compute).
  Invariante central: **nunca escreve no registro publicado — só na fila `submissions.json`**; conteúdo entra só
  pelo compilador neutro. Validado E2E em dry-run (duplicata SQ-001→0.99; nova→TEMP→promove p/ SQ-LIP-000043;
  DOI resolve; guard "promova a pergunta antes da sugestão"). Pendente: superfície web pública.
- **2026-06-02** — **Área 16 — Protocolo aberto + contribuição federada [Proposed]** (`R-PROTO-1/2`,
  `R-CONTRIB-1…6`): virada de "curar toda a ciência" → "definir o protocolo e abrir a porta". Núcleo rígido
  mínimo destilado em **`docs/spec/PROTOCOL.md` (SCR Protocol v1, draft)**, disease-agnostic e citável (a
  constituição que sobrevive ao fundador). Decisões-chave: criação aberta com portão de identidade-não-verdade;
  **contribuição de evidência = só sugerir artigo** (modelo pull-request, abuso = compute, não corrupção);
  **BYO-compute** (custo sai do fundador); **stewardship federado** por sociedades; **não fechar o protocolo**
  (aberto é o moat; monetizar serviços em volta). Origem: conversa estratégica sobre manter a ideia viva.
- **2026-06-02** — **R-FRESH-4 [Adopted]**: badge **"small evidence base (n=…)"** quando freshness ≥90% e
  fontes <6 (atualidade alta ≠ robustez); flag `small_base` no JSON. Dispara em SQ-031 (DXA), SQ-016 (gestrinona),
  SQ-006 (TDAH). Origem: SQ-031 100%/n=4 podia ser lida como evidência forte.
- **2026-06-02** — **Dedup + decomposição (faça 1 e 2):** **R-OBJ-7 [Adopted]** dedup cross-pergunta no loop
  (mesmo DOI vira link no grafo, não claim paralela) + passada retroativa consolidou **392→347 claims** (grafo
  cross-pergunta 4→44); **R-Q-7** aplicada decompondo 3 guarda-chuvas em sub-perguntas focadas, **25→34 perguntas**:
  SQ-013→SQ-026/027/028 (dor/volume/doença), SQ-023→SQ-029/030/031 (RM/linfocintilografia/DXA),
  SQ-015→SQ-032/033/034 (conservador/peso/psicossocial; componente cirúrgico reusa SQ-013 via grafo).
  **2ª rodada (25→42):** SQ-012→035/036 (hormônios/hereditariedade; reusa SQ-025), SQ-004→037/038
  (subdiagnóstico/triagem), SQ-017→039/040 (progressão→linfedema/incapacidade), SQ-020→041/042 (QoL/saúde mental).
  Sub-perguntas com `related` bidirecional renderizado nas páginas. Achado revelado: SQ-030 (linfocintilografia)
  **não diferencia** lipedema de linfedema — invisível enquanto agregada em SQ-023.
- **2026-06-02** — Remediação do piloto: **PECO preenchido em 392/392** (era 86% vazio); **teto grade×desenho**
  (R-CLM-13 estende a desenho; `review→moderate` após revisão — não `low`); **R-Q-7** (resposta por desfecho,
  sintoma×doença) com SQ-013 protótipo; **cache-busting do CSS** (`style.css?v=hash` — servidor manda max-age 10
  anos, sem token de purge); **proveniência R-AI-9 mostra só o modelo**, não o provedor/meio.
- **2026-06-02** — **R-AI-12 [Adopted]**: busca-por-contradição sempre-ligada — passo `gather_contra` (Europe PMC
  null/negativo + semântica contrária) em todo run do loop, e varredura rotativa de 2 perguntas/semana no cron.
- **2026-06-02** — **R-AI-11 + R-SITE-13 [Adopted]**: anti-viés de confirmação (classify proíbe default
  'supporting'; null bem-powered = contradicting) + resumo executivo no topo da pergunta (resposta 1-linha,
  limitação, mudança recente, **estabilidade** como rótulo transparente, **caveat** de contradição nas 18/25 com
  zero contraditório). Diagnóstico: contradicting = 2,4%.
- **2026-06-02** — **R-SITE-12 [Adopted]**: página de pergunta em dois registros — "Answer at a glance"
  (estruturado, contadores linkando aos claims, confiança = grau predominante) + "Current synthesis" (prosa,
  "not a verdict") + "What's new in vX" em destaque. Operacionaliza R-OBJ-6 na página.
- **2026-06-01** — **R-OBJ-6 [Adopted]**: clarificação das três camadas — Pergunta (primária) → Claims
  (substrato) → Answer (derivada/renderizada, versionada, **não** um veredito). Diferencial = trajetória
  versionada das respostas. Reposicionamento refletido na home e no rótulo da resposta no site.
- **2026-05-31** — **R-AI-10 [Adopted]**: ingestão de reading lists do Consensus via subagentes em fan-out
  (descoberta+resolução de DOI no contexto deles; loops em série no orquestrador). `resolve_dois.py` +
  `docs/spec/consensus-ingestion.md`. Mais barato/rápido; ~130k tokens/subagente fora do contexto principal.
- **2026-05-31** — **R-Q-6 [Adopted]**: perguntas (e claims) propositadamente focados/restritos/objetivos — uma
  relação por pergunta, população delimitada; proibido amplas/abertas/subjetivas; lacuna ampla → decompor em
  estreitas. Quanto mais objetiva a pergunta, mais alta a qualidade dos claims. Embutido no `SYS_PROPOSE`. Princípio
  estrutural (planejamento/estrutura/estratégia).
- **2026-05-31** — **R-CLM-14 [Adopted]**: metadados de evidência sempre sanitizados na escrita
  (`ingest.clean_text` no `enrich_evidence`) + defesa no render (`scrlib.clean_text`); remove markup JATS/HTML
  (`<scp>` etc.). Migração: 19 campos limpos. Origem: `<scp>` aparecendo no hover do timeline.
- **2026-05-31** — **R-AI-9 [Adopted]**: proveniência de IA pública — `compiled_by {model,label,provider,date}`
  por pergunta + `engine` por versão, exibido no rodapé da resposta e no JSON/API; estampado automaticamente nas
  recompilações; backfill nas 25. Também: R-AI-6 corrigida (default real = `claude-opus-4.8`).
- **2026-05-31** — **R-DATA-1 [Adopted]**: `scr.db` restaurado como store canônico = rebuild determinístico
  lossless dos seeds (`raw_json` + projeções), com `db.sync()` (build+parity) chamado automaticamente por todo
  tool que edita os seeds. Corrige o DB órfão (50/18 → 240/25) e impede drift silencioso futuro.
- **2026-05-31** — **R-Q-5 [Adopted]**: pergunta canônica + `phrasings`/`phrasings_pt`; portão de
  canonicalização na criação (`phrasings.py`: juiz LLM same/related/novel, fusão automática conservadora
  ≥0.85) evita perguntas duplicadas; phrasings entram em busca/JSON/API/página. Backfill nas 25 perguntas.
- **2026-05-31** — **R-CLM-13 [Adopted]**: grau curado humano (`bib grau`, Oxford N1..N6) é TETO do grade da
  máquina; prevenção na ingestão (`loop.py cap_grade`) + detecção (`audit_quality.py`, cron). Origem: revisão de
  qualidade do SCR-LIP-000221 (revisão narrativa N6 da menopausa marcada `moderate`). Migração: 45 rebaixados +
  161 preenchidos. Fecha o vão de R-CLM-11 na entrada.
- **2026-05-30** — v0.1: criação do rulebook consolidando as decisões das conversas (R-DOC,
  R-MIS, R-OBJ, R-ID, R-ALLOC, R-CLM, R-Q, R-VER, R-CIT, R-FRESH, R-AI, R-GOV, R-MR, R-HON,
  R-LIC, R-SITE). Meta-regra **R-DOC-1**: toda regra vital deve ser documentada aqui.
