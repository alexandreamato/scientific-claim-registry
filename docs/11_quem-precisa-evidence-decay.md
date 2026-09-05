# SCR — Quem precisa disto, e a feature que dói hoje (Evidence Decay)

> Estratégia de demanda (Amato, 2026-05-30). "A pergunta não é 'como construir?', é
> 'qual comportamento humano muda se isso existir?'". Projetos morrem por falta de
> necessidade, não de tecnologia.

## Para quem o SCR é (e em que ordem)

1. **Público geral — não é o alvo (vem por último, indiretamente).** Pessoas querem
   *respostas*; Google/ChatGPT/Perplexity já dão. Não construir o SCR pensando nelas.
2. **Cientistas — onde começa a doer.** Três dores reais:
   - **Estado atual da questão:** "Existe relação entre mastócitos e lipedema?" → hoje são
     *dias* no PubMed só para saber o ponto de partida. O SCR responde isso de cara.
   - **A lacuna:** hoje "precisamos de mais estudos" — mas *quais*? O SCR aponta: "a principal
     lacuna é ausência de estudos prospectivos."
   - **Quando a área mudou:** "quando a hipótese mastocitária ganhou força?" — hoje quase
     impossível; o SCR responde em segundos (histórico de versões da resposta).
3. **LLMs — o ouro.** LLMs **não têm memória científica estruturada** — têm texto. Hoje:
   `PubMed → IA → Usuário` (a IA reinterpreta tudo a cada vez). Com o SCR:
   `PubMed → SCR → IA → Usuário` — o SCR é a **camada intermediária** que a IA consulta
   (`SQ-LIP-0021` → estado atual, claims, controvérsias, histórico) em vez de refazer RAG.
   **Você deixa de competir com a IA e vira infraestrutura para a IA.**
4. **Sociedades médicas — consultam para atualizar guidelines.**

## A feature que torna indispensável: Evidence Decay / Knowledge Freshness

A maior dor da ciência **não é achar artigos** (PubMed já faz). É que **o conhecimento
envelhece e ninguém sabe exatamente quando.** Uma guideline de 2022; em 2026 já há 15 artigos
e 3 revisões novas — e ninguém atualizou.

O SCR pode ser o primeiro sistema a **medir a frescura do conhecimento por pergunta**:
> `Knowledge Freshness = 21%` → a maior parte da evidência é antiga (base envelhecendo).
> `Knowledge Freshness = 91%` → resposta alinhada com a literatura atual.

**Definição operacional v0.1 (transparente):** % das fontes de evidência indexadas da pergunta
publicadas nos últimos 5 anos (+ ano mais novo/antigo e nº de fontes). **Freshness baixa ≠
resposta errada** — sinaliza apenas que a base é antiga e *talvez* precise de revisão.
*(Já implementado nas páginas de pergunta e no JSON.)*

**Honestidade sobre prior art:** "evidence decay" não é conceito novo — Shojania et al. (2007),
*"How quickly do systematic reviews go out of date?"* (Ann Intern Med, DOI:10.7326/0003-4819-147-4-200708210-00179)
mostrou que ~23% das revisões ficam desatualizadas em 2 anos; a literatura de *living evidence*
fala em "signals for updating". O que o SCR acrescenta é **expor isso como métrica viva, por
pergunta, num registro aberto e legível por máquina** — o que nem PubMed nem Cochrane oferecem.

## O reposicionamento final: o SO da memória científica

Houve uma evolução enorme: do **consenso vivo + especialistas + votação** (frágil) para algo
muito mais simples e durável:

> **O sistema operacional da memória científica.** Não da verdade. Não do consenso. Da **memória**.
> PubMed guarda artigos. O SCR guarda **perguntas, claims e a evolução das respostas.**

**Frase-âncora (adotada no site):**
> *"PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to scientific questions."*

## A estratégia de adoção (o atalho)

Você **não precisa convencer bilhões de pessoas** a usar o SCR. Precisa convencer os **sistemas
que respondem perguntas científicas** (LLMs, ferramentas de evidência, sociedades). Se eles
passarem a depender dele, ele vira **infraestrutura** — e infraestrutura sobrevive décadas
(PubMed, GenBank, CrossRef, ClinicalTrials.gov). Por isso o SCR é **machine-first**: cada
pergunta tem um **JSON legível por máquina** (`/q/SQ-LIP-0021.json`) para a IA consumir.

## Implicações já implementadas / próximas

- ✅ **Knowledge Freshness** por pergunta (páginas + JSON).
- ✅ **JSON legível por máquina** por pergunta (machine-first).
- ⏭️ O **loop de vigilância** (Layer 1): IA lê artigo novo → liga à pergunta → marca
   supports/contradicts/refines → recalcula freshness → versiona a resposta se mudou.
- ⏭️ Endpoint/índice `/api/` e talvez JSON-LD/`ClaimReview` para interoperar com IAs.
