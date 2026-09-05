# Ingestão de reading lists via Consensus + subagentes (padrão — R-AI-10)

> Forma **padrão** de enriquecer perguntas com a literatura descoberta pelo **Consensus MCP**.
> Regra canônica em [`RULES.md`](./RULES.md) (R-AI-10); estende R-AI-8 (reading lists de DOIs).

## Por que subagentes

O Consensus MCP devolve **20 papers com abstracts completos** por busca (~6k tokens) e tem
**rate-limit agressivo** (cai na 2ª chamada paralela). Fazer isso no fluxo principal: (a) inunda o
contexto da conversa, (b) trava no rate-limit, (c) exige transcrição manual de títulos. **Solução:**
**subagentes em fan-out** absorvem o output gigante e a espera do rate-limit **no contexto deles** e
devolvem só a **lista limpa de DOIs**. Medido: ~130k tokens por subagente ficaram fora do contexto
principal. Mais barato e mais rápido que o fluxo direto.

## Pipeline padrão

```
1. DISCOVER (subagentes + Consensus MCP)         ← contexto isolado, em paralelo
   fan-out N subagentes, cada um com um lote de perguntas:
     para cada pergunta: Consensus search → filtra papers que mencionam a doença
       → resolve DOIs (resolve_dois.py) → grava /tmp/<SQ-ID>.dois
   subagente devolve só "SQ-ID: N DOIs" (NUNCA cola abstracts)

2. INGEST (loop principal, SERIAL)               ← escreve claims.json + scr.db
   para cada /tmp/<SQ-ID>.dois:
     python3 loop.py <SQ-ID> --doi-file /tmp/<SQ-ID>.dois --commit
   (serial porque todos escrevem o mesmo claims.json/scr.db; db.sync por commit — R-DATA-1)

3. PUBLISH
   build_questions.py + build_site.py → rsync deploy
```

**Divisão de trabalho:** subagentes fazem **só descoberta+resolução** (read-only no registro);
o orquestrador roda os loops em **série** (nunca em paralelo — conflito de escrita). O classify do
loop faz o filtro final de relevância (descarta o que não é da doença, mesmo que tenha passado).

## Template do subagente (copiar/adaptar)

> Um subagente `general-purpose` por lote (~6 perguntas). Rodar os lotes em paralelo (Agent tool,
> múltiplas chamadas numa mensagem). Cada subagente:

```
Você monta reading lists (listas de DOIs) para um registro científico de <DOENÇA>, usando o
Consensus MCP. Você SÓ escreve arquivos em /tmp — nunca toca em arquivos do projeto.

Suas perguntas (ID | texto):
<SQ-ID> | <texto da pergunta>
... (≈6)

SETUP único: ToolSearch com query `select:mcp__claude_ai_Consensus__search`.

Para CADA pergunta, em ordem:
1. mcp__claude_ai_Consensus__search UMA vez, query acadêmica focada que SEMPRE inclua "<doença>".
   Uma busca por vez (nunca paralela).
2. Se "Rate limit exceeded": `sleep 30` (Bash) e repetir a MESMA busca — até 5 tentativas.
3. MANTER só papers cujo título OU abstract mencione "<doença>"/variantes; DESCARTAR ruído.
4. Resolver DOIs: montar papers=[[title, sobrenome_1o_autor, ano], ...] num JSON e rodar
   `python3 registry/resolve_dois.py papers.json /tmp/<SQ-ID>.dois`.
5. `sleep 20` entre perguntas (rate-limit compartilhado).

MENSAGEM FINAL: curta — uma linha por pergunta `<SQ-ID>: <N> DOIs`. NÃO colar abstracts/títulos.
```

## Notas

- **R-Q-6 na prática:** perguntas estreitas → reading lists limpas (liposucção, keto: 10–20 DOIs de
  lipedema); perguntas de nicho → poucas, e tudo bem (ADHD 1, glúten 1, gestrinona 3).
- **R-CLM-12:** o loop também varre a biblioteca do autor em todo run LIP — os artigos do autor
  entram mesmo que não venham do Consensus.
- **Termos de uso do Consensus:** usamos os **DOIs** para ingerir dos primários (Crossref/Europe PMC),
  não redistribuímos a análise do Consensus. Descoberta, não redistribuição.
- **Resolução imperfeita:** `resolve_dois.py` pode pegar um "reply/commentary" no lugar do paper;
  `verify_ref` + classify do loop filtram. Aceitável para descoberta.
