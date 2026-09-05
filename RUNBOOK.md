# RUNBOOK — SCR (Scientific Claim Registry)

Como instalar, sincronizar, testar e atualizar o SCR a partir de um ambiente limpo
(**Fase 1 da descentralização** — ver `docs/spec/decentralization.md`). Caminhos são **relativos à raiz
do repositório**; rode os comandos a partir dela salvo indicação.

---

## 0. Cold-start (do zero ao site local, em ordem)

Qualquer pessoa consegue rodar tudo **localmente** sem credenciais — exceto o deploy da instância oficial
(seção 6, só maintainer). O núcleo é **stdlib do Python 3 (≥ 3.8)**; a única dependência externa é opcional.

```bash
# 1. Clonar e entrar
git clone <repo-url> scr && cd scr

# 2. Configurar segredos (opcional p/ build; necessário p/ rodar o loop com IA)
cp .env.example .env        # edite .env e preencha SCR_OPENROUTER_TOKEN se for usar o loop
set -a; [ -f .env ] && . ./.env; set +a    # carrega as vars no shell

# 3. (Opcional) dependência externa — só p/ gerar imagens do site
pip install -r requirements.txt

# 4. Reconstruir o banco canônico a partir dos seeds e validar paridade
python3 registry/db.py build
python3 registry/db.py verify        # deve dizer: ✓ parity OK

# 5. Buildar o site estático (gera HTML + JSON + sitemap)
cd site
python3 build_questions.py && python3 build_site.py && python3 build_home.py
cd ..
#    → abra site/index.html e site/q/SQ-LIP-000001.html no navegador

# 6. Sanidade do pipeline de ingestão — DRY-RUN (não grava nada; precisa de chave de IA)
python3 registry/loop.py SQ-LIP-000006 --source europepmc      # sem --commit = dry-run

# 7. Guards de qualidade (devem todos passar)
python3 registry/lang_check.py            # idioma (R-SITE-16)
python3 registry/enrich_evidence.py --check   # títulos de evidência (R-CLM-16)
python3 registry/audit_quality.py         # grade×desenho (R-CLM-13), read-only
```

Se chegou até aqui sem erro, o ambiente está reproduzido. **Deploy** (publicar na instância oficial) é a
seção 6 e exige credenciais do maintainer.

---

## 1. Pré-requisitos

- **Python 3 ≥ 3.8** — o núcleo (ingestão, banco, build) roda **só com a biblioteca padrão**.
- **Opcional:** `pip install -r requirements.txt` instala **Pillow** (apenas para `site/make_images.py`,
  favicon/og-image). Nada de framework pesado.
- **Opcional (alto recall):** o serviço `bib` local do autor — ver seção 4. Não é redistribuível; sem ele o
  loop usa Europe PMC.

---

## 2. Segredos e variáveis de ambiente

Os scripts resolvem cada segredo nesta ordem: **`SCR_*` (canônico) → nome convencional do fornecedor
(retrocompat) → arquivo `~/.config/...` (retrocompat)**. Defina-os via `.env` (ver `.env.example`) ou no
ambiente. Necessário só para o que usa IA/deploy:

| Função | Var canônica (`SCR_*`) | Fallbacks aceitos |
|---|---|---|
| LLM (loop/compilação) | `SCR_OPENROUTER_TOKEN` | `OPENROUTER_API_KEY` · `~/.config/scr_openrouter_token` |
| LLM alternativo | `SCR_ANTHROPIC_TOKEN` / `SCR_OPENAI_TOKEN` | `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` · arquivos |
| Modelo/provedor (opcional) | `SCR_LLM_MODEL` / `SCR_LLM_PROVIDER` | — |
| Deploy oficial (rsync) | `SCR_DEPLOY_SSH` | — |
| Cloudflare purge | `SCR_CF_TOKEN` | `~/.config/scr_cf_token` |

> **Build e leitura local não exigem segredo nenhum.** Chave de IA só é preciso para *rodar o loop*; as de
> deploy/Cloudflare, só para *publicar a instância oficial*.

---

## 3. Banco canônico e sincronização

`registry/scr.db` (SQLite) é **reconstrução determinística e lossless dos seeds JSON** (R-DATA-1) — por isso
**não é versionado** (`.gitignore`); regenere com `db.py build`.

> ⚠️ **Nunca** edite `registry/scr.db` direto. Altere os seeds `registry/claims.json` /
> `registry/questions.json` e rode o sync.

```bash
python3 registry/db.py build     # reconstrói o DB a partir dos seeds
python3 registry/db.py sync      # build + verify_parity (falha se DB ≠ seeds)
python3 registry/db.py verify    # checagem rápida de paridade
python3 registry/db.py stats     # estatísticas do registro
python3 registry/db.py query "SELECT id, statement FROM claims WHERE knowledge_state='established' LIMIT 5"
```

---

## 4. Loop de vigilância (ingestão de literatura)

Busca artigos e propõe claims numa pergunta. **Sem `--commit` = dry-run** (só mostra; não grava).

```bash
# Dry-run — exibe o que a IA proporia
python3 registry/loop.py SQ-LIP-000006 --source europepmc

# Commit — grava nos seeds + reconstrói o banco + versiona
python3 registry/loop.py SQ-LIP-000006 --source europepmc --commit
```

Se o `bib serve` (biblioteca pessoal do autor) estiver no ar, o loop faz busca **semântica** sobre ela
primeiro; offline, cai para **Europe PMC** automaticamente (`ingest.bib_available()`).

---

## 5. Higiene e guards

```bash
python3 registry/audit_quality.py          # relatório grade×desenho (read-only)
python3 registry/audit_quality.py --fix    # aplica teto Oxford
python3 registry/lang_check.py             # vazamento de idioma (R-SITE-16)
python3 registry/enrich_evidence.py        # preenche títulos faltantes; --check só audita (R-CLM-16)
```

---

## 6. Build local vs. Deploy da instância OFICIAL

**Build local — qualquer um:**
```bash
cd site
python3 build_questions.py    # perguntas + snapshots + sitemap
python3 build_site.py         # páginas de claims
python3 build_home.py         # home com dados vivos
cd ..
```

**Deploy da instância oficial — SÓ maintainer** (precisa de `SCR_DEPLOY_SSH` + `SCR_CF_TOKEN`; um clone novo
**não** publica em scientificclaims.org). Um host próprio aponta `SCR_DEPLOY_SSH` para o seu servidor.
```bash
# requer chaves SSH do maintainer e o token Cloudflare
rsync -avz --delete \
  --exclude='.inbox' --exclude='*.py' --exclude='deploy.md' --exclude='CLAUDE.md' \
  --exclude='.git' --exclude='.claude' --exclude='__pycache__' --exclude='.DS_Store' \
  -e "ssh -p 22" ./site/ "$SCR_DEPLOY_SSH"

# purgar o cache do Cloudflare (zona da instância oficial)
curl -s -X POST -H "Authorization: Bearer $SCR_CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/purge_cache" --data '{"purge_everything":true}'
```

> Automação server-side (Fase 2) deve usar o trilho **staging → diff → guards → promote → persistir** com
> *guard falho ⇒ não promove* — ver `docs/spec/decentralization.md`.
