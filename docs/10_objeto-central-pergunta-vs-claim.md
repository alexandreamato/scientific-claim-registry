# SCR — Qual é o objeto central? (Pergunta vs Claim)

> Decisão de modelagem mais importante do projeto (Amato, 2026-05-30). Quatro modelos
> possíveis levam a projetos radicalmente diferentes. Recomendação ao final.

## Os quatro modelos

| Modelo | Objeto central | Vantagem | Problema |
|---|---|---|---|
| **1. DOI para claims** | claim registrada à mão | simples, parecido com DOI | quem registra? duplicatas; não escala. ❌ |
| **2. PubMed para claims** | claim **descoberta por IA** (extrai do artigo, casa com existente ou cria nova) | escalável, sustentável | *claim matching* é difícil; NLP imperfeito (melhora em 5 anos) |
| **3. GitHub para claims** | a **evolução da formulação** (SCR-000001 → v2 mais precisa) | guarda como o enunciado amadurece — não existe hoje | exige curadoria/seleção de versões |
| **4. Pergunta científica** | a **Scientific Question** (SQ); claims viram evidência sob ela | perguntas são neutras, estáveis e naturais | matching de perguntas + ligação claim↔pergunta |

## A virada: o objeto certo é a PERGUNTA

A claim **já embute uma conclusão**:
> *"Women with lipedema have increased prevalence of joint hypermobility."*

A pergunta é **neutra**:
> *"Does lipedema increase the prevalence of joint hypermobility?"*

E **pesquisadores, pacientes e IAs pensam em perguntas.** O usuário não quer *achar uma claim* —
quer *responder uma pergunta*. A claim é só um **tijolo** dentro dessa resposta.

```
SQ-LIP-0007   "Does lipedema increase the prevalence of joint hypermobility?"
  ├─ Knowledge state: Probable (era Emerging em 2022)
  ├─ Claims a favor:   SCR-LIP-000017 (hipermobilidade ~44%) …
  ├─ Claims contra:    SCR-LIP-0000xx …
  ├─ Claims que refinam: "…apenas em mulheres adultas por critério de consenso"
  ├─ Evidência:        artigos / revisões ligados
  ├─ Timeline:         como a resposta evoluiu
  └─ Controvérsias:    onde os claims divergem
```
Busca "gluten" → `SQ-LIP-0021 "Does gluten affect lipedema symptoms?"` → dentro: claims de
suporte, claims contrárias, evidência, timeline, estado do conhecimento, controvérsias.

**Por que é mais poderoso:** *perguntas são relativamente estáveis; claims mudam.* A pergunta é o
índice navegável; o claim é a unidade de evidência versionada por baixo.

## A síntese (os quatro modelos compõem — não competem)

- **Pergunta (SQ)** = o **objeto navegável/entrada**, estável, neutro, com ID persistente.
- **Claim (SCR)** = a **unidade de evidência estruturada e versionada** que responde a perguntas
  (suporta / contradiz / refina). Um claim pode ligar-se a >1 pergunta → é um **grafo**, não árvore.
- **Artigo** = a fonte de evidência sob o claim.
- **Modelo 2 (IA extrai)** = *como* perguntas e claims são populados (automático, sustentável).
- **Modelo 3 (versão)** = aplica-se a ambos (a formulação da pergunta e do claim evoluem).
- **Modelo 1 (IDs)** = ambos recebem ID persistente (SQ-… e SCR-…).

> **Linha-âncora:** *"PubMed indexes papers. SCR indexes scientific questions and their evolving claims."*

## Honestidade sobre prior art (a pergunta-como-organizador já existe)

- **Epistemonikos / L·OVE** ("Living OVerview of Evidence") **organiza toda a evidência numa matriz
  de perguntas PICO** vivas — é o precedente mais próximo do Modelo 4. **Cochrane** e a **EBM (PICO)**
  inteiras são organizadas por *pergunta clínica*. Então "evidência por pergunta" **não é novo**.
- O que continua **distintivo** no SCR: **pergunta E claim como objetos identificados (IDs
  persistentes), com claims versionados como evidência granular, registro aberto e legível por
  máquina, populado por IA** — não uma síntese narrativa por equipe (Cochrane) nem uma matriz de
  revisões (L·OVE). A unidade aqui é o *claim sob a pergunta*, com histórico — não a revisão.
- Honestidade obriga citar **Epistemonikos L·OVE, PICO, Cochrane** ao lado de nanopublications/SciFact.

## Aposta recomendada (alinhada à sua)

❌ Registro manual de claims · ❌ Conselho humano definindo tudo · ❌ Consenso como núcleo
✅ **Registro automático** · ✅ **IA extraindo claims** · ✅ **Perguntas como entidade principal** ·
✅ **Claims como evidência estruturada** (versionada)

**Recomendação: adotar o modelo Pergunta-cêntrico** (Pergunta = contêiner navegável; Claim =
evidência versionada; IA popula; tudo com ID). Resolve duplicação (claims convergem sob a mesma
pergunta), dá entrada natural ao usuário, e mantém o claim como o tijolo estruturado.

## Cautela honesta (não esconder a dificuldade)

- O problema de *matching* **não some — muda de lugar**: agora há matching de **perguntas** +
  matching de **claims** + ligação **claim↔pergunta**. Mas perguntas são **menos numerosas e mais
  estáveis**, e o PICO dá estrutura → no líquido é **mais tratável e mais útil**.
- É um **grafo** (claim ↔ várias perguntas; pergunta ↔ vários claims), não uma árvore.
- Knowledge state pode viver **na pergunta** (a melhor resposta atual) e/ou no claim.

## O que isto muda no projeto (se adotado)

1. **Banco:** adicionar tabelas `questions` (SQ-LIP-…) e `claim_questions` (M2M, com papel
   supports/contradicts/refines). O `scr.db` já tem o resto.
2. **Piloto:** reagrupar os **50 claims de lipedema** sob ~15–20 **perguntas** (SQ-LIP-…) — vira
   um índice navegável por pergunta.
3. **Site:** a linha-âncora passa a *"PubMed indexes papers. SCR indexes scientific questions and
   their evolving claims."*; a página de registro passa a navegar por pergunta → claims.
4. **Pipeline (Layer 1):** IA, ao ler um artigo novo, extrai claim → liga à pergunta existente
   (ou cria pergunta) → marca supports/contradicts/refines.
