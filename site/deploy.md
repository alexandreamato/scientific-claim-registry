# Deploy — scientificclaims.org

Site estático (HTML/CSS, sem dependências) hospedado no servidor próprio via SSH.
Mesmo servidor do `dieta.amato.io`. Domínio canônico: **scientificclaims.org**
(o `scr.bio` apenas redireciona via Cloudflare — não precisa de deploy).

## Acesso

```
Host:    91.98.19.157
Porta:   22
Usuário: alexandre
Pasta:   /home/alexandre/web/scientificclaims.org/public_html/
```

## Build (antes do deploy)

As páginas são **geradas** a partir do registro (`../registry/questions.json` + `claims.json`).
Rode antes de publicar:

```bash
python3 ../registry/translate.py   # preenche *_pt faltantes via OpenAI (idempotente; pula os já traduzidos)
python3 build_questions.py   # EN + PT: questions.html + q/<id>.html + q/<id>.json + snapshots + sitemap (hreflang)
python3 build_site.py        # EN + PT: claims.html + pt/claims.html (NÃO gera sitemap)
python3 make_images.py       # (só se mudar a OG image / favicon)
```

> Site **bilíngue**: EN na raiz, PT espelhado em `/pt/`. O `rsync --delete` já inclui `/pt/`.

## Publicar alterações

A partir desta pasta (`site/`):

```bash
rsync -avz --delete \
  --exclude='.inbox' --exclude='*.py' --exclude='deploy.md' --exclude='CLAUDE.md' --exclude='.git' --exclude='.claude' \
  -e "ssh -p 22" \
  ./ alexandre@91.98.19.157:/home/alexandre/web/scientificclaims.org/public_html/
```

> `--delete` mantém o servidor idêntico à pasta local (remove arquivos órfãos). Retire-o
> se houver arquivos no servidor que não devam ser apagados.

## ⚠️ Purgar o cache do Cloudflare (SEMPRE após o deploy)

O Cloudflare faz cache de `style.css`/JS/imagens na borda. **Sem purgar, visitantes continuam
vendo a versão antiga** (ex.: CSS desatualizado → página "quebrada"). Purgue após cada deploy:

```bash
# Token: env SCR_CF_TOKEN (canônico) com fallback ao arquivo ~/.config/scr_cf_token
CF="${SCR_CF_TOKEN:-$(cat ~/.config/scr_cf_token 2>/dev/null)}"
curl -s -X POST -H "Authorization: Bearer $CF" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/d3acb1b294cdbd9c19e801ab83b495a5/purge_cache" \
  --data '{"purge_everything":true}'
```
(Zona `scientificclaims.org` = `d3acb1b294cdbd9c19e801ab83b495a5`. Token: `SCR_CF_TOKEN` ou `~/.config/scr_cf_token`.)

## Pré-requisito no servidor (uma vez)

A pasta `web/scientificclaims.org/public_html/` precisa existir e estar servida pelo
vhost do domínio (no painel HestiaCP: adicionar o domínio `scientificclaims.org`).
O DNS no Cloudflare já aponta `scientificclaims.org` e `www` → **91.98.19.157** (proxied).

## SSL/TLS

Tráfego proxied pelo Cloudflare (🟠). Definir o modo SSL no Cloudflare conforme o servidor:
- servidor **com** certificado próprio (ex.: Let's Encrypt do HestiaCP) → modo **Full**;
- servidor **sem** certificado → modo **Flexible**.

## Acessar / verificar

```bash
ssh -p 22 alexandre@91.98.19.157
ssh -p 22 alexandre@91.98.19.157 "ls -la /home/alexandre/web/scientificclaims.org/public_html/"
```

## Conteúdo

- `index.html` — landing page (EN) · `pt/index.html` — landing (PT)
- `claims.html` — os 50 claims (gerado de `../registry/claims.json`; toggle EN/PT, filtro por estado)
- `style.css` — estilos (institucional, responsivo, sem dependências)
- `favicon.svg` · `robots.txt` · `sitemap.xml`
- `build_site.py` — gerador de `claims.html` + `sitemap.xml` (não vai pro servidor)

## Infra (resumo)

- **DNS/Cloudflare:** `scientificclaims.org` + `www` → A 91.98.19.157 (proxied). Redirects
  301: `www`→raiz e `scr.bio`→`scientificclaims.org` (regras dinâmicas no Cloudflare).
- **scr.bio** só ativa após trocar os NS na GoDaddy para `brad.ns`/`elsa.ns.cloudflare.com`.
- Domínio canônico/principal: **scientificclaims.org** (ver `docs/06_dominios.md`).
