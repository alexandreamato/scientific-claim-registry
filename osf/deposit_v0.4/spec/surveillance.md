# SCR — Layer 1: loop de vigilância (arquitetura e operação)

> Como o registro se mantém vivo num **servidor modesto** (HestiaCP/Hetzner), sem stack pesada.
> Princípio: **site estático + cérebro local em Python + SQLite**. v0.1, 2026-05-30.

## Stack (decisão)

| Camada | Escolha | Por quê |
|---|---|---|
| Linguagem do loop | **Python** | todo o registro/NLP/LLM já é Python; PHP não ganha nada |
| Banco | **SQLite** (`scr.db`) | loop é 1 processo (1 escritor); arquivo único, sem servidor de DB |
| Servir o site | **estático** (HTML/JSON) | rápido, barato, à prova de carga; o dinamismo é o cron regenerando |
| API de **leitura** | **JSON estático** (`/api/`, `/q/<id>.json`) | sem backend; cacheável no Cloudflare; LLMs consomem direto |
| Receber **propostas** | **inbox mínimo** (`submit.php` 1-arquivo **ou** Cloudflare Worker) | só enfileira; não é o cérebro |
| LLM | **API remota** | a compute pesada é remota; o servidor só faz HTTP |

> MySQL/MariaDB só quando houver **escrita web concorrente** (ex.: Layer 2 — especialistas votando).
> Até lá, SQLite basta.

## O loop (passos)

```
PubMed/Europe PMC → extração → matching → atualização → nova versão (se mudou)
```
1. **Buscar** literatura nova por pergunta (Europe PMC REST, sem chave). `ingest.py` já faz.
2. **Diferença:** descartar o que já está indexado (por DOI/PMID).
3. **Classificar (LLM):** para cada artigo novo relevante → `{relevant, stance, statement, study_design}`
   (postura = supports/contradicts/refines a *pergunta*). Ver prompt abaixo. *(hoje é heurístico — plugar o LLM.)*
4. **Rascunhar:** criar claim **draft** com ID temporário (`db.request_id`), ligado à pergunta + evidência (provenance).
5. **Validar (identidade, não verdade):** bem-formado + dedup → `promote` (vira FINAL + alias) ou `merge`/`reject`.
6. **Recalcular Knowledge Freshness**; se a resposta mudou materialmente, o LLM **re-compila** a resposta → **nova versão** (commit congelado).
7. **Regenerar o estático** e publicar.

## Pipeline de comandos (rodar LOCAL)

```bash
cd registry
python3 ingest.py SQ-LIP-000005 --commit     # estagia candidatos (drafts) no scr.db
# (após plugar o LLM: classifica, promove/merge, versiona)
python3 db.py export                          # DB -> claims.json (mantém o seed em sincronia)
cd ../site && python3 build_questions.py && python3 build_site.py
rsync ... ./ alexandre@91.98.19.157:.../public_html/    # deploy estático
curl ... /purge_cache ...                     # purga o cache (R-SITE-6)
```

> ⚠️ **Ordem importa.** Depois do *seed* inicial (`db.py build`), **o `scr.db` é a fonte viva**: o
> `ingest`/loop **mutam** o banco. **NÃO rode `db.py build` de novo** (ele apaga e re-semeia do JSON
> → perderia os drafts/versões). Para sincronizar o JSON, use **`db.py export`** (DB → claims.json).

## Onde roda

- **Agora (recomendado): local.** Você roda o pipeline na sua máquina (na mão ou via `launchd`/cron)
  e faz o deploy do estático. O servidor fica **só estático, sem segredos**. Simples e seguro.
- **Depois (autonomia 24/7): cron no Hetzner.** *Mesmo script* num venv; o cron regenera o `public_html`
  in loco. Vantagem: roda mesmo com seu Mac desligado. Custo: venv + chave de API no servidor.

Exemplo de cron (mensal → semanal conforme amadurece):
```
# crontab -e   (rodar dia 1 às 03:00)
0 3 1 * *  cd /caminho/registry && /caminho/venv/bin/python ingest.py --all --commit >> ingest.log 2>&1
```

## API de leitura (estática, machine-first)

| Endpoint | Conteúdo |
|---|---|
| `GET /api/index.json` | metadados + lista de endpoints |
| `GET /api/questions.json` | todas as perguntas (estado, freshness, links) |
| `GET /q/<id>.json` | a pergunta: resposta atual, claims, evidência, versão, freshness, citação |
| `GET /api/claims.json` | todos os claims (evidência) |

Tudo CC BY 4.0, cacheado. É a "API para os robôs de IA" — `PubMed → SCR → IA → Usuário`.

## Receber propostas (inbox)

`site/submit.php` (1 arquivo) recebe `POST {question, kind, domain, email?, notes?}` (com honeypot),
valida o básico e **enfileira** em `../submissions.jsonl` (fora do `public_html`, a salvo do `rsync --delete`).
Drenar local: `scp alexandre@91.98.19.157:web/scientificclaims.org/submissions.jsonl .` → o loop processa.
Alternativa sem PHP: **Cloudflare Worker** grava na fila/KV. O cérebro (validar/dedup/LLM/ID/versão) é sempre local.

## Prompt da etapa LLM (contrato de `classify()`)

> System: *You compile scientific evidence. You do not give opinions or decide truth.*
> User: Given the QUESTION and an ARTICLE (title+abstract), return JSON:
> `{"relevant": bool, "stance": "supporting|contradicting|refines|irrelevant", "statement": "<one neutral sentence claim with explicit context>", "study_design": "...", "confidence_grade": "high|moderate|low|very_low"}`.
> Rules: stance is relative to the QUESTION's affirmative direction; if the article doesn't address the
> question, `relevant=false`. Be conservative; prefer `refines`/`low` when unsure.

(Recompilar a resposta da pergunta usa outro prompt: resume os claims atuais numa frase cautelosa
*evidence-bounded*, lista incerteza e — comparando com a versão anterior — descreve "what changed".)

## Custo

≈ tokens por artigo classificado + 1 recompilação por pergunta que mudou. Rodando mensalmente sobre
dezenas de perguntas, é baixo. A busca (Europe PMC) é grátis.

---

## Atualização (2026-05-31) — retrieval semântico + LLM agnóstico + reading lists

O loop evoluiu de protótipo para produção. Mudanças principais (ver RULES R-AI-6/7/8, R-CLM-9):

**1. Retrieval semântico via `bib` (a biblioteca do autor).** Substitui o FTS5 lexical como fonte
primária da biblioteca. `ingest.bib_search()`:
- `GET /semantic?q=<pergunta>` (API `bib serve`, embeddings/Ollama local) → ranqueia por significado;
- `fichamod.load(stem_to_path(stem))` → **ficha estruturada exata** (objetivo, intervenção, resultados,
  conclusão, grau, DOI) → vira o `abstractText` do candidato (entrada melhor que abstract cru).
- Fallback: `library_index` (FTS5) se a API estiver fora (`bib_available()`).
- Config: `BIB_API` (default `http://127.0.0.1:8900`), `BIB_DIR`.

**2. LLM agnóstico de provedor** (`ingest._chat_json`): OpenRouter (default `anthropic/claude-sonnet-4.6`)
> Anthropic > OpenAI, por presença de chave. `classify`/`match`/`recompile` usam a mesma função.
Sonnet 4.6 é decisivamente melhor que gpt-4o(-mini): descarta irrelevantes, distingue achado distinto de
restatement (merge), e recompila evidence-bounded com gradação de evidência.

**3. Ingestão de reading lists** (`loop.py --doi-file f.txt`): `ingest.fetch_dois()` resolve cada DOI no
Europe PMC. Fluxo "ferramenta externa (ex.: Consensus.app) descobre → SCR registra e versiona".

**4. Merge conservador endurecido:** prompt + modelo forte. Achado mecanístico/molecular/imagem vira
**claim novo**; só restatement da MESMA asserção corrobora (vira evidência anexada ao claim existente).

**5. Evidência permanente (R-CLM-9):** o loop só faz *append* de evidência (nunca deleta); a recompilação
injeta a **base de evidência inteira** (todos os claims + todos os artigos), não só os novos.

**Posicionamento provado:** mesmo recall semântico do Consensus, mas sobre o corpus de lipedema mais
completo (o do autor) **e** com memória versionada/persistente — que o Consensus não tem.
