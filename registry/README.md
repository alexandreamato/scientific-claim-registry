# SCR-LIP — Registro-piloto de lipedema

O piloto foi iniciado com a biblioteca de lipedema do Dr. Amato e priorizou artigos do próprio autor na v0.1. No registro de trabalho de 2026-11-20, **42 perguntas** agrupam **216 proposições ativas com 841 achados**. O registro preserva também **514 claims substituídos ou retirados**. Uma proposição pode estar ligada a várias perguntas. Cada achado registra o resultado de um estudo em relação à proposição.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| **`scr.db`** | Projeção SQLite reconstruída a partir dos JSON versionados |
| `questions.json` | **Seed das perguntas** (`SQ-LIP-…`) + links a claims com papel |
| `claims.json` | Registro versionado de proposições, achados e claims arquivados — schema em `docs/spec/claim-schema.md` |
| `claims.csv` | Versão achatada para planilha/revisão |
| `_held_out_theory.json` | **Teoria IIT2/gfWAT do autor — fora do registro por ora** (decisão de 2026-05-30) |
| `build_registry.py` | Compilador histórico do seed da v0.1 |
| `REVIEW_v0.1.md` | **Revisão crítica** dos 50 claims (escopo, calibração, duplicação, DOIs) |
| `schema.sql` | Esquema (claims, evidence, relations, curators, versions, consensus, held_out, **questions, question_versions, claim_questions**) |
| `db.py` | CLI do banco: `build` · `export` · `stats` · `query "SQL"` |

## Histórico da v0.1 ao recorte de 2026-06-02

- **42 perguntas** (`SQ-LIP-…`) agrupam **345 claims** (cada claim ligado a ≥1 pergunta; grafo cross-pergunta).
- Crescimento: o seed v0.1 (2026-05-30) tinha **50 claims / 18 perguntas**; o loop de vigilância + ingestão de
  reading lists do Consensus levaram a **392 / 25** (live), depois **dedup cross-pergunta (R-OBJ-7)** consolidou
  392→**347**, **decomposição de 7 guarda-chuvas (R-Q-7)** abriu 25→**42** (SQ-013/015/023/012/004/017/020 →
  sub-perguntas por desfecho/modalidade/componente/mecanismo) e a **limpeza pré-publicação** removeu 2 claims
  off-domain (lymphedema/BCRL) → **345**. O **Zenodo v0.3** congelou um snapshot de **240** claims.
- Estado do conhecimento atual: 7 established · 12 probable · 323 emerging · 2 speculative · 1 no_evidence.
- **Higiene (2026-06-02):** 0 claims órfãos · 0 evidências sem grade · 100% PECO · títulos em toda evidência
  (R-CLM-16). Auditoria histórica em `claim_audit_2026-06.md` (já **remediada**).
- Snapshot histórico do seed de 50 claims: `REVIEW_v0.1.md`, `build_registry.py`.

## Princípios aplicados (honestidade epistêmica)

- **Evidência ≠ consenso ≠ verdade** — as três dimensões ficam separadas em cada claim.
- **GRADE honesto:** estudo transversal único = `low`/`emerging`; meta-análise = `moderate`/`probable`;
  série de casos = `low`; revisão sistemática sem estudos (gestrinona) = afirmação `established` de **ausência de evidência**.
- **`gaps` explícito** em todo claim (viés, reverse causation, amostra, etc.).
- **Teoria do autor (IIT2) excluída** do registro até ter suporte empírico — mas os *achados
  empíricos* que a inspiraram (histamina elevada, assinatura M2, padrão QST, associações HLA/
  celíaca/câncer/IgG) **permanecem** como claims independentes, atribuídos às fontes primárias.

## Como evoluir

- O [roadmap](../docs/roadmap.md) descreve a integração entre vigilância e incorporação de achados, a revisão das sínteses afetadas e a publicação de versões recuperáveis. Para a operação atual, consulte o [runbook](../RUNBOOK.md).

## Aviso

Claims não substituem julgamento clínico. As licenças por componente constam em [LICENSE](../LICENSE).
