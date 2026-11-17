# SCR — Formato e regra de criação de códigos (IDs)

> Como os identificadores do registro são **estruturados, infinitos** e como nascem
> (**temporário → validado → final**, com redirect permanente). v0.1, 2026-05-30.

## 1. Formato — estruturado e infinito

```
<PREFIXO>-<DOMÍNIO>-<SEQ>
```
- **PREFIXO:** `SQ` = pergunta (Scientific Question) · `SCR` = claim (evidência).
- **DOMÍNIO:** 2–4 letras maiúsculas (`LIP` lipedema, `LYM` linfedema, `EDS`…). **Extensível**
  → novos domínios são apenas novos códigos. Infinito em domínios.
- **SEQ:** inteiro ≥ 1, **mínimo de 6 dígitos** com zero-pad, **sem teto** — pode transbordar
  para 7, 8, … dígitos. Infinito em quantidade. Ex.: `SCR-LIP-000001` … `SCR-LIP-1000000`.

Regras: **case-insensitive na leitura, canônico em maiúsculas**; SEQ **nunca é reutilizado**
(mesmo após retração — vira tombstone, não é reemitido); a **versão** (`v1.0`) é separada do ID.

## 2. Ciclo de vida — temporário → validado → final

Qualquer origem (IA extraindo de um artigo, ou um humano) **solicita** um código. O sistema
emite primeiro um **código temporário (draft)**; o **final** só é alocado na validação.

```
[request]  →  TEMP (draft)            ex.: SCR-LIP-D000007   (status: draft)
                 │
          [validate]
         ┌───────┼───────────────┬───────────────┐
     promote                  merge            reject
        │                        │                 │
   FINAL canônico          alias p/ existente   tombstone
   SCR-LIP-000051          (sem queimar nº)     (410/withdrawn)
        │                        │
   TEMP 301→FINAL           TEMP 301→existente
```

- **request → TEMP (draft).** Código provisório em sub-namespace `D` (ex. `SCR-LIP-D000007`),
  resolvível como página provisória. **Não consome número canônico.**
- **validate:**
  - **promote** → aloca o **próximo SEQ canônico** do contador `(prefixo,domínio)` (monotônico,
    nunca reusado) → `SCR-LIP-000051`. Cria **alias** `TEMP → FINAL`. O TEMP passa a **301-redirect**
    para o FINAL, **para sempre** (citações/links antigos não quebram). Status: `published`.
  - **merge** → se for duplicata de um código já existente, **alias** `TEMP → existente` (redirect),
    **nenhum número novo é queimado**. Status: `merged`.
  - **reject** → TEMP vira **tombstone** (resolve para aviso "withdrawn", HTTP 410). Nenhum número
    final é emitido. Status: `rejected`.

**Por que TEMP-first:** drafts são baratos e descartáveis; o **espaço canônico fica limpo e
significativo** (sem buracos por rejeições/duplicatas). Só conhecimento validado ganha número final.

## 3. O que é "validar" (alinhado a "registra, não arbitra")

Validação é sobre **identidade**, não sobre verdade:
1. **Bem-formado:** claim tem statement + contexto + ≥1 evidência; pergunta é neutra e tem PICO mínimo.
2. **Deduplicação (matching):** não é o mesmo claim/pergunta que um código já existente
   (se for, → **merge**).
3. **(Opcional, Layer 2) sign-off humano** de curador. Por padrão a Layer 1 valida automaticamente
   (bem-formado + dedup); o número final **não** depende de comitê.

## 4. Resolução / redirect (toda forma de código resolve)

| Código | Resolve para |
|---|---|
| FINAL canônico | a página (`/q/<id>.html` ou claim) |
| TEMP/draft (pré-validação) | página provisória |
| TEMP/alias (pós-validação) | **301** → canônico (ou existente, no merge) |
| rejeitado | aviso "withdrawn" (410) |

A camada web emite **stubs de redirect** para cada alias no build (hoje estático; no futuro,
resolução dinâmica). A tabela de aliases é **permanente**.

## 5. Implementação no banco (`registry/`)

- `id_counters(scope, next_seq)` — `scope` = `SCR-LIP` (canônico) ou `SCR-LIP-D` (draft). Inc atômico.
- `id_requests(temp_id, prefix, domain, kind, status, canonical_id, note, created, decided)`.
- `id_aliases(from_code, to_code, kind, created)` — permanente.
- CLI (`db.py`): `request <PREFIXO> <DOMÍNIO> ["nota"]` → emite TEMP · `promote <TEMP>` → aloca
  FINAL + alias · `merge <TEMP> <FINAL>` · `reject <TEMP>` · `resolve <código>` (segue aliases).
- Contadores são **semeados** no `db.py build` a partir do maior SEQ já existente por escopo.

> Resumo: **TEMP barato e descartável → validação por identidade (não verdade) → FINAL canônico
> infinito, com o TEMP redirecionando para sempre.** Mantém o espaço de IDs limpo, citável e perene.
