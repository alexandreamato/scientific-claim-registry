# SCR-LIP — Registro-piloto (Lipedema) v0.1

Primeiro registro-piloto do **Scientific Claim Registry**, domínio **lipedema**.
Construído a partir da biblioteca do Dr. Amato (`artigos lipedema`), **priorizando os
artigos do próprio autor** como evidência. GRADE honesto; a IA não opina; curadoria humana opcional.

**Modelo pergunta-cêntrico (ver `docs/10`):** os **345 claims** (atual; o seed v0.1 tinha 50) estão agrupados
sob **42 perguntas científicas** (`SQ-LIP-…`, seed em `questions.json`). A pergunta é o objeto navegável;
o claim é evidência ligada (papel supporting/contradicting/refines/context). O site gera uma
página de evidência versionada por pergunta (com **Knowledge Freshness** e JSON legível por máquina).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| **`scr.db`** | 🗄️ **Banco canônico** (SQLite) — fonte da verdade (claims + perguntas + evidência + versões + consenso) |
| `questions.json` | **Seed das perguntas** (`SQ-LIP-…`) + links a claims com papel |
| `claims.json` | Seed/registro dos claims (atual **345**; seed v0.1 = 50) — schema em `docs/spec/claim-schema.md` |
| `claims.csv` | Versão achatada para planilha/revisão |
| `_held_out_theory.json` | **Teoria IIT2/gfWAT do autor — fora do registro por ora** (decisão de 2026-05-30) |
| `build_registry.py` | Compilador (regenera json+csv a partir dos dados curados) |
| `REVIEW_v0.1.md` | **Revisão crítica** dos 50 claims (escopo, calibração, duplicação, DOIs) |
| `schema.sql` | Esquema (claims, evidence, relations, curators, versions, consensus, held_out, **questions, question_versions, claim_questions**) |
| `db.py` | CLI do banco: `build` · `export` · `stats` · `query "SQL"` |

## Status (2026-06-02)

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

- Cada claim deve, com o tempo, ganhar `consensus` (painel de especialistas) e `history` (versões).
- Fontes ainda não mineradas para crescer além de 50: demais sentenças do consenso Delphi
  (~90 no total), estudos de prevalência e os artigos do acervo ainda não usados.
- Regenerar após editar `build_registry.py`: `python3 build_registry.py`.

## Aviso

Claims não substituem julgamento clínico. Conteúdo sob CC BY 4.0.
