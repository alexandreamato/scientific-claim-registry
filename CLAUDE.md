# CLAUDE.md — Projeto SCR (Scientific Claim Registry)

Guia para o Claude Code ao trabalhar neste repositório. **Leia antes de editar.**

## ⚠️ Rulebook — `docs/spec/RULES.md` (a documentação mais importante)

**Sempre que uma regra vital for definida, mencionada ou alterada em conversa, ela DEVE ser
registrada imediatamente em `docs/spec/RULES.md`** — com **ID estável** (`R-AREA-n`), frase
normativa curta e **status** (`[Adopted]`/`[Planned]`/`[Proposed]`) — e o **Changelog** do
rulebook atualizado. **Nunca apagar IDs** (marcar `(deprecada)`). O `RULES.md` é a **fonte
canônica das regras**; este CLAUDE.md e os demais docs apontam para ele e, em caso de conflito,
**o RULES.md prevalece**. Isto vale também para esta instrução (meta-regra **R-DOC-1**).

## O que é este projeto

O **Scientific Claim Registry (SCR)** — *"o sistema operacional da memória científica"*.
Não da verdade. Não do consenso. Da **memória**: ele guarda **perguntas científicas**, os
**claims** (afirmações) que as respondem, e a **evolução das respostas** ao longo do tempo.

> **Posicionamento canônico:**
> *"PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to scientific questions."*
> Ele **registra, não arbitra**. Lipedema é o domínio-piloto (disease-agnostic por design).

Autor/fundador: **Dr. Alexandre Campos Moraes Amato** — Amato Duo / Associação Brasileira de
Lipedema (ABL). ORCID `0000-0003-4008-4029`. Origem: conversa reconstruída em `docs/00_…`.

## Modelo de objeto (decisão central — docs/09 e docs/10)

| Camada | Nome | Papel |
|---|---|---|
| **Pergunta** | `SQ-LIP-0001` | **Objeto central navegável** — estável, neutra. O usuário entra por aqui. |
| **Claim** | `SCR-LIP-000001` | **Evidência estruturada e versionada** ligada à pergunta (papel supporting/contradicting/refines/context). É um **grafo** (claim ↔ várias perguntas). |
| **Artigo** | DOI/PMID | Fonte de evidência sob o claim. |

**Arquitetura em camadas — só a Layer 1 precisa existir:**
- **L1 Registry (o produto, automatizável):** registra perguntas+claims, acumula
  Supports/Contradicts/Refines + histórico. **Não julga.**
- **L2 Consensus (opcional):** especialistas endossam/discordam/qualificam.
- **L3 Recommendation (opcional):** sociedades médicas → conduta clínica.

**SCR = infraestrutura · BIO = framework de pesquisa** (o "motor"/método). Marca pública = SCR.

## Convenções

- **IDs:** pergunta `SQ-LIP-000001`; claim `SCR-LIP-000001` (`<SQ|SCR>-<DOMÍNIO>-<6 díg.>`). Prefixo
  `SQ` (pergunta) é distinto de `SCR` (claim) de propósito. **DOMÍNIO vem do dicionário canônico
  `registry/domains.json`** (código 2–4 letras, único/estável/nunca reusado; identidade real da doença =
  cross-ref MONDO/ICD-11/MeSH, não inventar). Ver R-ID-8.
- **Estados do conhecimento:** Speculative → Emerging → Probable → Established → Foundational.
- **Confiança da evidência:** **GRADE** (high/moderate/low/very_low). Não inventar score.
- **Knowledge Freshness:** % das fontes de evidência da pergunta dos últimos 5 anos
  (mede *Evidence Decay*). Freshness baixa ≠ resposta errada → base envelhecendo.
- **Três dimensões SEMPRE separadas:** Evidence Confidence · Consensus · Knowledge State.
- **A IA não opina.** Respostas são cautelosas e *evidence-bounded* ("Based on currently
  indexed evidence…"). Curadoria humana é **opcional**, não requisito.
- **Machine-first:** cada pergunta expõe JSON legível por máquina (`/q/<id>.json`) — o SCR
  é feito para LLMs/agentes consumirem (PubMed → SCR → IA → Usuário).
- **Idioma:** conceitos/conteúdo científico em inglês; notas estratégicas internas em PT;
  landing bilíngue (EN + `/pt/`).
- **Licenciamento (Postura B):** docs CC BY 4.0; dados CC BY-SA/ODbL; código futuro AGPL +
  licença comercial; marca registrada; contribuições sob CLA. Ver `docs/07_licenciamento.md`.

## Princípios inegociáveis nos textos

1. **Honestidade sobre prior art.** Não inventamos "scientific claims" nem a identidade
   persistente (nanopublications/Trusty URIs já existem; ClaimRxiv propôs a tese; SciFact é
   o campo de verificação; Epistemonikos/PICO organiza evidência por pergunta). A contribuição
   do SCR é **adoção + organização por domínio + acumulação versionada + freshness + machine-first**,
   **construída sobre** o que existe — não reinventando identificadores. Ver `docs/08`, `docs/10`.
2. **Registra, não arbitra.** Verdade/consenso/recomendação são camadas opcionais acima.
3. **Consenso ≠ verdade.** Expor divergência, nunca escondê-la num número só.
4. **Construir sobre, não reinventar** (nanopub/Trusty URI + DOI DataCite; PROV-O; ClaimReview).

## Dados e pipeline (`registry/`)

**Store canônico = `registry/scr.db` (SQLite), reconstrução LOSSLESS dos seeds, auto-sincronizado (R-DATA-1).**
Centraliza claims, evidências (com `grade`), relações, curadores, versões, phrasings, consenso (L2 vazio),
perguntas e a teoria IIT2. Cada objeto vai **verbatim** numa coluna `raw_json` (export byte-a-byte) + projeções
normalizadas para SQL.

- **Superfície de edição = seeds JSON:** `questions.json` e `claims.json` (o que loop/curadoria/site escrevem).
- **Porta de contribuição (protótipo, R-CONTRIB):** `submit.py` (`question` · `suggest` · `list` · `process`) —
  terceiros criam perguntas (portão de identidade) ou sugerem artigos (DOI/PMID), atribuído por ORCID. **Nunca
  escreve no registro — só na fila `submissions.json`;** conteúdo entra só via o loop neutro no `process` (BYO-compute).
- **Esquema:** `schema.sql`. **CLI:** `db.py` (`sync` · `build` · `export` · `verify` · `stats` · `query "SQL"`).
- **Auto-sync (NÃO é manual):** todo tool que muda os seeds chama `db.sync()` no commit (`loop.py`,
  `audit_quality.py`, `add_phrasings.py`, `propose_questions.py`, `curate.py`). `sync` = rebuild + `verify_parity`
  (falha se DB ≠ seeds). Para sincronizar à mão: `python3 db.py sync`. **Nunca** editar o DB in-place.
- **Pipeline:** editar seeds (ou rodar o loop) → **`db.sync()` automático** → `site/build_questions.py` +
  `site/build_site.py` → HTML → `rsync` deploy.
- `build_registry.py` foi o **seed** inicial dos 50 claims (histórico). Revisão em `REVIEW_v0.1.md`.

### Loop de vigilância da Layer 1 — FECHADO (`registry/loop.py` + `ingest.py`)

Ciclo automático: **retrieval → classify → promove/corrobora → recompila → versiona**.
- **Retrieval semântico (R-AI-7):** via **`bib`** (biblioteca local do autor, API `http://127.0.0.1:8900`):
  `/semantic` (embeddings/Ollama) + `fichamod` (ficha estruturada exata: objetivo/resultados/conclusão/grau/DOI).
  Subir com `./bib serve` na pasta da biblioteca. Fallback FTS5 (`library_index.py`) se a API cair. Também
  Europe PMC (`--source europepmc|all`) e **lista de DOIs** (`--doi-file`, p/ reading lists do Consensus).
- **Busca-por-contradição SEMPRE (R-AI-12):** todo run também roda `gather_contra` (Europe PMC null/negativo +
  semântica contrária) p/ não viesar o corpo de evidência. Classify endurecido (R-AI-11) rotula contradição.
  Automação: cron varre 2 perguntas/semana caçando contradição.
- **LLM (R-AI-6):** agnóstico — OpenRouter→**Opus 4.8** (default) > Anthropic > OpenAI. Chave em
  `~/.config/scr_openrouter_token` (única chave ativa; OpenAI/Cloudflare removidas).
- **Comandos:** `loop.py <SQ-id> [--source library|europepmc|all] [--doi-file f] [--accept N]
  [--no-recompile] [--commit]`. Sem `--commit` = dry-run. Garantias: `verify_ref` (DOI resolve), merge
  conservador (achado distinto vira claim novo; restatement corrobora), `safe_year` (sem ano futuro),
  evidência **nunca deletada** e re-injetada em toda revisão (R-CLM-9). Depois: build → rsync → purge.

## Site e infraestrutura (`site/`) — no ar em https://scientificclaims.org

- **Páginas:** `index.html` (EN, minimalista) · `pt/index.html` · **`questions.html`** (índice
  de perguntas) · **`q/SQ-LIP-xxxx.html` + `.json`** (página de evidência versionada por pergunta,
  com Knowledge Freshness) · `claims.html` (todos os 50 claims) · `favicon.svg`, `og-image.png`,
  `apple-touch-icon.png`, `logo.svg`, `robots.txt`, `sitemap.xml`.
- **Build → deploy:**
  ```bash
  cd site && python3 build_questions.py && python3 build_site.py && python3 build_home.py && \
  rsync -avz --delete --exclude='*.py' --exclude='deploy.md' --exclude='CLAUDE.md' \
    -e "ssh -p 22" ./ alexandre@91.98.19.157:/home/alexandre/web/scientificclaims.org/public_html/
  ```
  `build_questions.py` é dono do **sitemap**; `build_home.py` regenera o hero da home do dado real da pergunta
  em destaque (R-OBJ-6; prosa curada em `CARD_COPY`, metadados ao vivo). `make_images.py`
  regenera og-image/apple-touch (Pillow). Detalhes em `site/deploy.md`.
- **Servidor:** 91.98.19.157 (mesmo do dieta.amato.io), user `alexandre`, HestiaCP, chaves SSH OK.
- **Cloudflare (via API):** `scientificclaims.org`+`www` → A 91.98.19.157 (proxied), SSL **Full**,
  Always-HTTPS; redirects 301 `www`→raiz e `scr.bio`→`scientificclaims.org`. Canônico =
  **scientificclaims.org**; `scr.bio` = marca curta (pendente troca de NS na GoDaddy). Ver `docs/06`.

## Publicação e DOIs (Zenodo, CC BY 4.0)

- **SCR Protocol v1 (a "constituição", DOI próprio):** **10.5281/zenodo.20517114** · Registro:
  https://zenodo.org/record/20517114 (spec autônoma disease-agnostic = `docs/spec/PROTOCOL.md`; PDF+MD;
  `isPartOf` o concept DOI; publicado 2026-06-02). Ver R-PROTO-2.
- **Concept DOI** (sempre a última versão): **10.5281/zenodo.20466195**
- **Version DOI (v0.4, ATUAL):** **10.5281/zenodo.20665788** · Registro: https://zenodo.org/records/20665788
  (camada de verificação adversarial por dois modelos + proveniência ao nível da frase, R-AI-13/14; auditoria
  completa do piloto: 42 perguntas/347 claims, 416/423 evidências verificadas, 13 fabricações corrigidas; publicado 2026-06-12)
- **Version DOI** (v0.3): **10.5281/zenodo.20476673** · Registro: https://zenodo.org/records/20476673
  (framework implementado + dataset do piloto 25 perguntas/240 claims; publicado 2026-05-31)
- **Version DOI** (v0.2): **10.5281/zenodo.20466196** · Registro: https://zenodo.org/records/20466196
- **OSF:** https://osf.io/n97ez/ · Manutenção/versionamento: ver `osf/` (sempre Amato Duo + ORCID + CC BY).

## Mapa de documentos (`docs/`)

- `00_conversa-origem-chatgpt.md` — reconstrução da conversa fundadora
- `02_prior-art-review.md` — prior art (nanopubs, Wikidata, CIViC, ClinGen, GRADE, ClaimRxiv…)
- `03_SCR-e-diferenciacao.md` — SCR vs Cochrane vs IAs científicas
- `04_editorial-SCR-draft.md` — rascunho do editorial
- `05_estrategia-macro.md` — founder-steward, veículo institucional, fomento
- `06_dominios.md` — domínios (scientificclaims.org principal; scr.bio marca)
- `07_licenciamento.md` — Postura B (commons protegido)
- `08_scientific-claim-ecosystem.md` — revisão profunda do ecossistema de claims (NLP/nanopubs/KGs)
- `09_arquitetura-em-camadas.md` — "registra, não arbitra"; L1/L2/L3
- `10_objeto-central-pergunta-vs-claim.md` — **a pergunta é o objeto central**
- `11_quem-precisa-evidence-decay.md` — demanda (cientistas/LLMs), Evidence Decay/Knowledge Freshness, "OS da memória"
- `BIO_v0.1/v0.2`, `BIO_manifesto_completo_PT`, `AI_Council_Prompt/Review` — material fundador
- **`spec/RULES.md` — o rulebook canônico (a fonte das regras; mantenha sempre atualizado, R-DOC-1)**
- **`spec/PROTOCOL.md` — SCR Protocol v1 (draft): o NÚCLEO RÍGIDO mínimo, disease-agnostic e citável,
  destilado do RULES — a "constituição" que sobrevive ao fundador. Define conformância + periferia aberta +
  modelo de contribuição (criação aberta, sugestão-só-de-artigo, BYO-compute, stewardship federado). Área 16 do RULES.**
- `spec/methodology.md` — **fluxogramas Mermaid** (modelo de objeto/camadas · loop de vigilância · criação de perguntas · higiene contínua)
- `spec/consensus-ingestion.md` — **padrão R-AI-10**: ingestão de reading lists do Consensus via subagentes (fan-out) + `resolve_dois.py`
- `spec/decentralization.md` — **mapa para tirar o sistema da dependência do autor/laptop**: fases laptop→portável→server→federável, com custos/obstáculos (Fase 1 = portabilidade/bus-factor, recomendada primeiro)
- `spec/id-allocation.md` (formato infinito + ciclo temp→validado→final) · `spec/claim-schema.md`
  (modelo de dados da claim) · `spec/governance-model.md` (= Layer 2 opcional)
- `glossary.md` · `roadmap.md` · `one-pager.md`
- `registry/README.md` (banco + claims + perguntas) · `site/deploy.md` · `osf/` (registro de prioridade)

> Onde docs antigos divergem do estado atual, **docs/09–11 prevalecem** (pivô pergunta-cêntrico,
> registra-não-arbitra, machine-first). A versão inicial falava em "consenso vivo"/Delphi como
> núcleo — isso virou a **Layer 2 opcional**.

## Estado atual (2026-06-12)

**🛡️ CAMADA DE VERIFICAÇÃO (R-AI-13/14, R-CLM-17) — COMPLETA E PUBLICADA (Zenodo v0.4, `10.5281/zenodo.20665788`).**
Toda evidência carrega **proveniência ao nível da frase** (quote verbatim com grounding determinístico) + **verificação
adversarial por um segundo modelo** (stance + fidelidade em duas altitudes: por-fonte = contradição/deturpação; por-claim =
fabricação vs. união das fontes). Piloto **inteiro auditado**: **416/423 evidências verificadas, 0 disputed, 7 unverified**;
**13 fabricações corrigidas**; contaminação cross-paper, stance mislabels e erros de desenho expostos e limpos (cada
correção no change-log do claim). Tooling: `verify_claims.py` (auditoria, resumível) + `run_audit_all.sh`. Selo público
por-pergunta e global (R-SITE-17): rollup `evidence_verification` no JSON + selo na home/index/api.

Site no ar e **totalmente bilíngue** (EN raiz + PT `/pt/`, hreflang); **382 claims / 461 evidências sob 42 perguntas**
(Zenodo v0.3 = snapshot de 240; v0.4 = 347; 392→347 dedup R-OBJ-7; 25→42 decompor 7 guarda-chuvas R-Q-7;
347→382 pelo cron semanal de jun–ago — **os números aqui envelhecem sozinhos: conferir com `db.py stats`**)
(SQ-LIP-…, cada claim com **página própria** `/c/<id>.html` + JSON e back-links às perguntas); Knowledge
Freshness e JSON por pergunta; **tags+keywords, busca e paginação client-side**; referências como **links
diretos** (DOI/PMID → artigo); citação com **autor corporativo**; estado **`no_evidence`** (lacuna ≠
prova de ausência, R-CLM-7); **dicionário de domínios** (MONDO/ICD-11/MeSH + resolvedor).

**🎯 LOOP DA LAYER 1 FECHADO, COM RETRIEVAL SEMÂNTICO E SONNET** (`registry/loop.py` + `ingest.py`):
**`bib` /semantic** (embeddings sobre a biblioteca curada do autor) + ficha estruturada → **classify
(Claude Sonnet 4.6 via OpenRouter)** → verify_ref → promove/**corrobora** (merge conservador) → recompila
(evidence-complete, R-CLM-9) → **versiona por pergunta** (snapshots imutáveis). Também ingere **reading
lists de DOIs** (`--doi-file`, ex.: Consensus.app). Já refeitas com esse fluxo: Q1/Q2/Q3/Q4 (reading lists)
e Q5/Q11 (biblioteca). Qualidade ≈ Consensus no recall, **superior na memória** (versionada e persistente).
**Pendências:** rotacionar chaves (OpenRouter/OpenAI/**Zenodo** apareceram no chat); dedup
por-pergunta (hoje global); endurecer ainda o prompt do merge se preciso. Próximas frentes (plano de
capitalização): **camada 3** = publicar o corpus verificado como dataset (HuggingFace/Croissant/nanopub);
e ainda em aberto da revisão: mapa de lacunas estruturado, bus-factor/reprodutibilidade por fontes públicas.

## Memória

Memória persistente do projeto em
`~/.claude/projects/-Users-alexandreamato-…-bio/memory/` (índice em `MEMORY.md`).
