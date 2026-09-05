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
- **R-CLM-9 [Adopted]** **Evidência é permanente; revisão é evidence-complete.** Um artigo que uma vez
  sustentou um claim **permanece para sempre** no banco (claims.json `evidence[]`; retração = tombstone,
  nunca deleção — R-ID-5). Toda **revisão/recompilação** da resposta compila sobre a **base de evidência
  acumulada inteira** (todos os claims da pergunta + TODOS os seus artigos), **re-injetada** no contexto —
  nunca só sobre os artigos novos. A deduplicação só vale para **descoberta** (artigo já indexado não é
  re-sugerido como candidato novo, evitando claim duplicado); como evidência persistida, ele entra em toda
  revisão futura. (`loop.py: claim_brief()` injeta as evidências; SYS_COMPILE exige compilar de tudo.)
- **R-CLM-6 [Adopted]** Evidência de autoria do próprio autor é **preferida** quando for sobre o domínio,
  **mas só se for sobre o domínio** (claim fora de escopo não entra). (REVIEW_v0.1)

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
  default **`anthropic/claude-sonnet-4.6`**) > Anthropic > OpenAI, por presença de chave
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

## 10. Governança e camadas

- **R-GOV-1 [Adopted]** **L1 Registry** roda sem governança pesada (regras mínimas de identidade).
- **R-GOV-2 [Adopted]** **L2 Consensus** (especialistas endossam/discordam/qualificam) e **L3
  Recommendation** (sociedades) são **opcionais, acima** do registro. (docs/spec/governance-model)
- **R-GOV-3 [Adopted]** Modelo **founder-steward**: Amato fundador/guardião da metodologia; conhecimento aberto. (docs/05)
- **R-GOV-4 [Adopted]** Transparência de conflito de interesse **quando** houver camada de consenso.

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
  endereçável com identificador persistente. A pergunta segue sendo a navegação PRIMÁRIA (R-OBJ-1).
- **R-SITE-10 [Adopted]** **Referências de evidência são links diretos para o artigo-fonte.** `DOI:` →
  `https://doi.org/…`; `PMID:` → `https://pubmed.ncbi.nlm.nih.gov/…`; referências bibliográficas pré-MEDLINE
  (sem identificador) ficam em texto. Helper `ref_link()` em `site/scrlib.py`; aplicado em claims.html e nas
  páginas de pergunta (claims de apoio/contra + "Key references"). Abre em nova aba (`rel=noopener`).

---

## Changelog

- **2026-05-30** — v0.1: criação do rulebook consolidando as decisões das conversas (R-DOC,
  R-MIS, R-OBJ, R-ID, R-ALLOC, R-CLM, R-Q, R-VER, R-CIT, R-FRESH, R-AI, R-GOV, R-MR, R-HON,
  R-LIC, R-SITE). Meta-regra **R-DOC-1**: toda regra vital deve ser documentada aqui.
