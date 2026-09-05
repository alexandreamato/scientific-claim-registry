# Descentralização — tirar o SCR da dependência de uma pessoa e de um laptop

> Mapa de planejamento (2026-06-03). **Não é execução** — é a sequência de fases, dependências, custos e
> obstáculos honestos, para o autor decidir o ritmo. Origem: constatação de que "o sistema ainda está 100%
> dependente de mim e do meu computador". Quando uma fase virar decisão firme, registrar como regra no
> `RULES.md` (R-DOC-1).

## O diagnóstico (onde a dependência vive hoje)

| Componente | Onde roda | Dependência de você |
|---|---|---|
| Loop / ingestão (`loop.py`, `ingest.py`) | seu Mac | chave OpenRouter (`~/.config/scr_openrouter_token`) + **biblioteca `bib` local** (`127.0.0.1:8900`, semantic + ficha) |
| Build + deploy (`site/build_*.py` + rsync) | seu Mac | suas chaves SSH para `91.98.19.157` |
| Cron (sweeps, guards, higiene) | **launchd do seu Mac** | só respira quando o Mac está ligado |
| Porta de contribuição (`submit.py`) | seu Mac | CLI local — ninguém de fora alcança |
| Seeds + `scr.db` | Dropbox / seu Mac | reconstrutível, mas o pipeline e o runbook estão na sua máquina/cabeça |
| **Site + JSON API** | **servidor Hetzner** | ✅ **já independente** |

**Resumo:** o lado **leitura** já está fora de você; o lado **escrita** (ingerir, compilar, buildar, deployar,
os guards, receber contribuição) é 100% seu laptop. Mac desligado uma semana → o sistema para de respirar.
Mac perdido → o pipeline some (os dados sobrevivem no Dropbox/Zenodo, mas a capacidade de *operar* não).

Há **dois problemas distintos** dentro de "depende de mim":
- **(A) Operacional** — só roda quando eu rodo.
- **(B) Bus-factor** — se eu/meu disco sumir, a operação acaba.

São independentes; o mapa abaixo resolve um de cada vez.

---

## As fases

### Fase 0 — Hoje (laptop-bound)
Tudo do lado escrita no seu Mac. Ponto único de falha = seu Mac + seu conhecimento tácito.
Já pronto nesta direção: protocolo com DOI (10.5281/zenodo.20517114), README/LICENSE/CITATION.cff, `.gitignore`,
os 3 guards (título R-CLM-16, idioma R-SITE-16, grade R-CLM-13), `submit.py` (protótipo).

### Fase 1 — Portável / bus-factor  **(resolve B · recomendada primeiro)**
**Meta:** qualquer pessoa — ou você num Mac novo — reergue tudo do zero a partir do repositório.
**Passos:**
- **Repo público no GitHub** (código + seeds + docs + protocolo). Licenças já definidas (LICENSE, Postura B).
- **Externalizar segredos** (nunca no repo): `.env.example` documentando o que é preciso —
  `SCR_OPENROUTER_TOKEN`, alvo/chave SSH de deploy, `SCR_CF_TOKEN`. (Já gitignorados.)
- **`RUNBOOK.md`** — receita de cold-start: pré-requisitos (Python 3, deps), como `db.sync`, rodar o loop numa
  pergunta, buildar, deployar, rodar os guards. O "como ligar de novo".
- **Fixar dependências** (`requirements.txt`). Hoje o pipeline é quase só **stdlib** (urllib/json/sqlite3) —
  barreira baixa; o LLM é HTTP via OpenRouter. (pandoc/weasyprint só para o PDF do protocolo, opcional.)
**Custo:** ~zero. **Esforço:** baixo (≈80% já feito nesta sessão).
**Destrava:** laptop morto ≠ projeto morto. **Pré-requisito de tudo o que vem depois.**
**Obstáculo honesto:** a **`bib`** (seu corpus curado + embeddings Ollama) **não é portável** — é sua biblioteca
pessoal de PDFs (IP de terceiros, não redistribuível). Um clone novo roda com retrieval **só Europe PMC** (menos
recall no seu próprio corpus). Essa assimetria é permanente: a `bib` é simultaneamente seu diferencial **e** sua
dependência. Aceitar que ela fica pessoal e o resto fica portável — a `bib` é **adaptador opcional de alto recall**
(`ingest.bib_available()` já degrada para Europe PMC quando ela não está no ar).

**Entregáveis para FECHAR a Fase 1 (checklist — ✅ feito 2026-06-03):**
- [x] **`RUNBOOK.md`** — cold-start completo + build-local vs deploy-oficial separados; caminhos **relativos**
  (sem `file://`/absoluto que vazaria o path local e quebraria fora do seu Mac).
- [x] **`.env.example`** — vars `SCR_*` sem valores. Scripts migrados para **`os.environ`** com cascata
  **`SCR_* → nome convencional → arquivo ~/.config`** (`ingest._openrouter_key` etc.; cron lê `SCR_CF_TOKEN`).
  Roda em contêiner/GitHub Actions sem mudar código; nomes antigos ainda funcionam.
- [x] **`requirements.txt`** — núcleo **stdlib-only**; única dep externa = **`Pillow`** (só `site/make_images.py`).
  Opcionais fora do pip: `weasyprint`+`pandoc` (PDF do protocolo) e o serviço `bib`.
- [x] **Decisão `scr.db`: NÃO versionar** — rebuild determinístico lossless dos seeds (R-DATA-1). `.gitignore`
  ignora `registry/scr.db` (+ `*.sqlite*`); seeds são o que se commita; `db.py build` regenera no cold-start.
- [x] **Cold-start no RUNBOOK §0:** `git clone` → `cp .env.example .env` → `db.py build` → `db.py verify` →
  build site → `loop … ` **dry-run** → 3 guards → (deploy = só maintainer).

**Falta para a Fase 1 ficar 100%:** só `git init` + push para o GitHub público (decisão operacional do autor).

### Fase 2 — Automação server-side  **(resolve A)**
**Meta:** o sistema respira sem o seu Mac.
**Passos:**
- Repo no servidor (Hetzner já existe), segredos no env do servidor.
- O `cron_retractions.sh` passa a rodar **no servidor** (cron do Hetzner), não no launchd do Mac. Ele já faz
  sweep de contradição + guards + build + deploy condicional; no servidor o "deploy" vira build **in loco**
  (sem rsync).
- Retrieval server-side = **Europe PMC + listas de DOI** (o fallback já está codado; `bib` indisponível lá).
**Custo:** gasto da chave de IA rodando sozinha — o sweep (2 perguntas/semana) é barato; recompilações custam
mais. Bounded e pequeno no ritmo atual. Servidor já pago.
**Destrava:** batimento independente; freshness/higiene continuam mesmo com você offline.

**Trilho auditável obrigatório (staging → guard → publish).** "Os guards mitigam" não basta para um cron que
compila **e publica** sozinho. O ciclo server-side DEVE ser:
1. **Staging** — o loop escreve numa cópia/branch de trabalho, nunca direto no site público.
2. **Diff/relatório** — gerar um diff legível (o que mudou em quais perguntas/claims/versões) + log.
3. **Guards** — rodar os 3 (idioma R-SITE-16, título R-CLM-16, grade R-CLM-13) + `db.py verify` (paridade).
   **Qualquer guard falho ABORTA a promoção** (não publica; loga; alerta).
4. **Promote** — só então o build vai para o site público (rsync/in-loco).
5. **Persistir** — commit automático (ou artefato versionado) + snapshots imutáveis (R-VER-2) + logs guardados.
Isto transforma o cron de "publicador cego" em "pipeline com portão". (Hoje o `cron_retractions.sh` já faz
sweep+guards+build condicional; falta o **gate explícito**: guard falho ⇒ não promove.)

**Obstáculos:** segredos no servidor (ver Fase 1, via `.env`/secrets do runner); **confiança na compilação não
supervisionada** — coberta pelo trilho acima + guards. Decisão: o sweep-base usa a chave do projeto (custo seu)
até contribuintes trazerem a própria (BYO-compute).

### Fase 3 — Intake público de contribuição  **(a porta de verdade)**
**Meta:** outra pessoa contribui sem você rodar nada.
**Passos:**
- Endpoint web mínimo (o inbox de R-MR-5): form/Cloudflare Worker/`submit.php` que recebe
  {proposta de pergunta | sugestão de artigo + ORCID} → grava numa **fila no servidor**.
- O cron da Fase 2 processa a fila pelo compilador neutro (a lógica do `submit.py process`, server-side).
**Custo:** mínimo (Worker free / PHP no HestiaCP). **Destrava:** gente de fora alimenta o registro, atribuída por
ORCID — é o `submit.py` virado para fora (R-CONTRIB-2 já especificado).

**Blindagem obrigatória — fila isolada + aprovação humana.** O intake público **NUNCA** altera os seeds
canônicos (`questions.json`/`claims.json`) da produção direto. Fluxo:
1. A submissão pública entra numa **fila de auditoria isolada** (ex.: `.inbox/` no servidor ou banco de
   rascunhos) — separada das seeds, gitignorada/efêmera.
2. Verificações automáticas: ORCID válido, DOI resolve, rate-limit, dedup de identidade (TEMP).
3. **Aprovação/rejeição humana** (curador) lista a fila antes de qualquer build. Só o aprovado passa pelo
   compilador neutro e entra no trilho de staging da Fase 2.
Isso fecha três vetores de uma vez: **injeção de prompt**, **spam de créditos de IA**, **corrupção das seeds**.
A superfície já é estreita ("só sugira um artigo" → pior caso = compute desperdiçado), mas a fila isolada +
aprovação humana é a defesa em profundidade. (O `submit.py` já honra a invariante "nunca escreve no registro,
só na fila" — a Fase 3 é exigir o mesmo do endpoint público + o passo de aprovação.)

### Fase 4 — Federável / steward externo
**Meta:** um terceiro roda o próprio domínio (ou co-administra).
Agora o protocolo (doc + DOI) + repo público + pipeline reprodutível + intake público tornam possível uma
sociedade/pesquisador adotar o SCR para `SQ-CAR-…` com a própria chave/servidor, **ou** administrar um domínio
na instância compartilhada (multi-steward, R-CONTRIB-5; CLA; marca). **É aqui que recrutar faz sentido** — o
"lugar" para onde recrutar finalmente existe.
**⛔ PORTÃO (pré-requisito não-negociável):** **não entrar na Fase 4 antes de resolver a identidade global de
namespaces** (próxima seção). Sem isso, dois hosts podem emitir `SQ-CAR-000001` com sentidos diferentes → forks
incompatíveis. Resolvido, o SCR vira de fato um protocolo; não resolvido, é só um site bem estruturado.

---

## Identidade global de namespaces — o portão da federação (decisão arquitetural mais sensível)

**O problema (não resolvido hoje).** O protocolo diz que o domínio vem de um dicionário canônico e que os códigos
são únicos/estáveis (R-ID). Isso vale **dentro de um host**. Mas se qualquer um roda o próprio SCR, **quem impede
dois hosts de emitirem `SQ-CAR-000001` com sentidos diferentes?** Sem resposta, descentralizar produz **forks
incompatíveis**.

**As duas arquiteturas (framing do revisor):**
1. **Registry central de namespaces** — uma fundação/`scientificclaims.org` mantém o dicionário global de
   domínios e mint dos códigos. Dá um **tecido global único** (`SQ-LIP-000001` = a mesma coisa em todo lugar).
   Custo: **governança central** (ponto único que precisa ser neutro e disponível). Modelo DOI/ORCID/ISBN.
2. **IDs qualificados por host** — o ID global vira `scientificclaims.org/q/SQ-LIP-000001`; o `SQ-LIP-000001`
   "pelado" é só local à instância. **Mais federável** (sem gargalo central de mint). Modelo git (hash global +
   branch local) / npm (`@scope/nome`) / Trusty URI.

**A tensão com a TESE do SCR.** O pitch é *"a resposta única e evolutiva a uma pergunta científica"* — um objeto
canônico que **acumula** evidência ("PubMed tem muitos papers; o SCR tem a resposta que evolui"). Opção 2 pura
**fragmenta** isso: N hosts com N perguntas paralelas sobre a mesma coisa = exatamente o que o SCR existe para
evitar. Opção 1 pura cria **gargalo de governança** e contradiz "protocolo aberto, hosts competindo".

**Recomendação — híbrido (opção 2 para emitir + resolução para o tecido único), com o domínio já ancorado fora.**
Três camadas, alinhadas a "construir sobre, não reinventar" (R-MR-2):
- **Domínio = ancorado em ontologia externa (JÁ É R-ID-8).** `LIP` ≡ `MONDO:0013577` / ICD-11 / MeSH. O SCR
  **não precisa ser a autoridade** do namespace de doenças — delega à MONDO, que já é a autoridade global. Isso
  resolve metade do problema sem governança central nova. ✅ já existe.
- **Emissão = qualificada por host (opção 2).** Cada host mint localmente (sem gargalo); o ID **global físico** é
  `host/q/<code>` (sem colisão). Federável.
- **Tecido único = camada de resolução `sameAs`.** Estende o juiz de canonicalização (R-Q-5, hoje *intra*-host)
  para *inter*-host: perguntas de hosts diferentes com a **mesma identidade canônica** (mesmo domínio MONDO +
  phrasing equivalente) são ligadas por `sameAs` e resolvíveis juntas. O "tecido único" é **reconstruído por
  resolução** (como a web acha o mesmo tópico via links/sameAs, ou Wikidata Q-IDs, ou nanopub/Trusty), **não**
  por mint central. Sem gargalo, sem fragmentação.

**Veredito:** para "protocolo aberto + hosts competindo", **opção 2 + resolução** é o caminho — e o domínio já
está ancorado externamente, o que é o pedaço mais difícil resolvido.

**✅ DECIDIDO (2026-06-03): arquitetura HÍBRIDA.** Encodada como **R-ID-9** (emissão qualificada por host),
**R-ID-10** (âncora de domínio = autoridade inter-host, delega à MONDO) e **R-ID-11** (tecido único por resolução
`sameAs`, não mint central) no `RULES.md`, e no `PROTOCOL.md` §4. Status `[Proposed]` → vira `[Adopted]` quando
implementada. **Portão da Fase 4 agora tem direção definida** (falta a implementação da camada `sameAs` + IDs
host-qualificados antes de federar de fato).

## Grafo de dependência e ritmo sugerido

```
Fase 1 (portável)  ──►  Fase 2 (server)  ──┐
        │                                   ├──►  Fase 4 (steward externo)
        └──────────────►  Fase 3 (intake) ──┘
```

- **Fase 1 é o portão.** Barata, alta apólice de seguro, ~80% pronta. Fazer a seguir.
- **Fases 2 e 3** podem ir quase em paralelo depois da 1 ("roda sem mim" + "aceita gente de fora").
- **Fase 4** (recrutar) só depois que 1+2+3 existirem. Hoje é prematuro — você está certo.

## O que **permanece** pessoal (e tudo bem)

Descentralizar a **infraestrutura** ≠ remover o fundador. Ficam seus por design:
- a **`bib`** (corpus curado) — diferencial de qualidade, não redistribuível;
- o **founder-steward** da metodologia (R-GOV-3) e o **veto metodológico**;
- a **marca** "SCR" (Postura B / R-LIC).

O objetivo não é você sair — é o sistema **sobreviver e operar sem depender da sua máquina estar ligada**.

**O único centro irredutível (R-GOV-5/6).** Mesmo descentralizando todas as máquinas, sobra um centrinho: **(1) o
nome confiável** ("SCR", marca, R-LIC) e **(2) quem edita a spec canônica** (R-DOC-1). É **autoridade/confiança**,
não infraestrutura — concentra como em todo padrão (Linux→Linus, Python→Guido, Web→W3C), e não é defeito. O
**resolver `sameAs` oficial** (R-ID-11) é central por **confiança, não força**: segue regra pública, qualquer um
roda o seu e audita o oficial (R-GOV-5). A jogada final de bus-factor para esse último centro é **migrar de uma
pessoa para uma FUNDAÇÃO** dona da marca e guardiã da spec (R-GOV-6) — assim até ele sobrevive ao fundador.
