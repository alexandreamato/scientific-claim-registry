# SCR — Roadmap

> ⚠️ **Atualização (2026-05-30):** após o pivô **pergunta-cêntrico / registra-não-arbitra**
> (docs/09–11), o núcleo passou a ser o **registro automatizado (Layer 1)**, não o consenso/Delphi
> (que virou Layer 2 **opcional**). As ondas abaixo são o plano original (founder-steward) —
> mantidas como histórico; o roadmap técnico vivo está no fim deste arquivo.

## ✅ Já feito (Onda 0 e parte da 1)
- [x] PDFs fundadores + **OSF** (osf.io/n97ez) + **Zenodo DOI** (10.5281/zenodo.20466195/196).
- [x] Editorial do SCR rascunhado (`docs/04`).
- [x] Domínios: **scientificclaims.org** (principal) + **scr.bio** (marca).
- [x] **Site no ar** (landing minimalista EN+PT, página de claims, 18 páginas de pergunta, JSON, freshness).
- [x] **Registro-piloto:** 50 claims sob 18 perguntas; banco canônico `scr.db`.

## 🎯 Roadmap técnico vivo (pergunta-cêntrico)
1. **Loop de vigilância da Layer 1 (próximo):** IA lê artigo novo (PubMed/Europe PMC) → extrai
   claim → liga à pergunta (ou cria) → marca supports/contradicts/refines → recalcula
   **Knowledge Freshness** → versiona a resposta **se** mudou (commit). Roda mensal → semanal.
2. **Interop machine-first:** índice `/api/`, JSON-LD / `ClaimReview`, IDs estilo nanopub/Trusty URI.
3. **Expansão de perguntas/domínios** (linfedema, EDS…) e curadoria humana opcional (Layer 2).
4. **Publicação:** editorial SCR → artigo do piloto.

---

## (Histórico) Plano original em ondas — founder-steward

## Onda 0 — Plantar a bandeira  ✅ concluída
- Registrar prioridade (OSF/Zenodo/DOI), editorial, domínios, landing. **Feito.**

## Onda 1 — Registro-piloto (1–3 meses)
- [ ] **50 claims fundamentais de lipedema** com IDs `SCR-LIP-0000xx` (planilha/JSON, schema em `docs/spec/claim-schema.md`).
- [ ] Curadoria 100% humana, GRADE, histórico. Sem IA, sem grafo.
- [ ] Amato como curador-chefe + 3–5 co-curadores fundadores.
- **Resultado:** prova de execução — algo concreto para mostrar.

## Onda 2 — Validação e rede (3–9 meses)
- [ ] **Artigo do piloto** (Amato 1º autor).
- [ ] 10–20 "Founding Curators" internacionais (Herbst, Gianesini, grupos DE/UK).
- [ ] Palestra "From Static Consensus to Living Consensus" em eventos da ABL.
- **Resultado:** legitimidade externa sem perder o leme.

## Onda 3 — A instituição (9–24 meses)
- [ ] Formalizar **BIO Foundation** (se houver tração) — Amato Diretor.
- [ ] Site do SCR consultável + API mínima + primeiros IDs citados por terceiros.
- [ ] Fomento (CNPq/FAPESP → internacional); 1–2 doenças afins (linfedema, EDS).
- **Resultado:** infraestrutura nascente.

## Onda 4 — Ecossistema (25+ meses)
- [ ] Plataforma multi-especialidade; vigilância por IA validada; integrações.
- [ ] Modelo sustentável: aberto + serviços premium (hospitais, indústria).
- [ ] Meta: IDs do SCR citados por IAs científicas ("according to SCR-LIP-000234…").

## Publicações (Amato 1º autor em todas)
1. Editorial SCR → JMIR / PLOS Digital Health / Learned Publishing (Onda 0).
2. Position paper v0.2 → Patterns / npj Digital Medicine (Onda 1–2).
3. BIO-Lipedema Pilot → npj Digital Medicine / Lancet Digital Health / JAMIA (Onda 2–3).

## Métrica de sucesso do piloto
Tempo médio de incorporação de nova evidência **< 30 dias** (vs anos no modelo
tradicional); adoção por ≥3 centros de referência; engajamento/retenção de curadores documentados.
