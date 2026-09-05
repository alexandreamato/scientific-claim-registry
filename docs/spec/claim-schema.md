# SCR — Especificação do Modelo de Dados da Claim (v0.1)

> O ativo mais importante do projeto. Define o que é uma claim registrada no SCR.
> Curadoria humana primeiro; GRADE reusado; três dimensões sempre separadas.

## 1. Princípio

Uma **claim** é uma *afirmação científica significativa expressa dentro de um contexto
claramente definido*. Claims **não** são frases livres de contexto — toda claim deve
especificar população, condição, exposição/intervenção, comparador, desfecho e escopo
metodológico. Despida do contexto, a frase perde significado estável (crítica central
do conselho de IAs).

## 2. Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | sim | Identificador persistente `SCR-<DOMÍNIO>-<6 dígitos>`, ex. `SCR-LIP-000001`. Imutável. |
| `version` | string (semver) | sim | Versão da claim, ex. `3.0`. |
| `statement` | string | sim | Texto canônico da afirmação (1 frase, contexto explícito). |
| `statement_pt` | string | não | Tradução PT (piloto bilíngue). |
| `claim_type` | enum | sim | `clinical_association` · `causal` · `diagnostic` · `therapeutic` · `prognostic` · `mechanistic` · `epidemiologic` · `definitional`. |
| `context` | objeto | sim | Ver §3 (PECO-like). |
| `knowledge_state` | enum | sim | `speculative` 🔴 · `emerging` 🟠 · `probable` 🟡 · `established` 🟢 · `foundational` 🔵. |
| `evidence_confidence` | enum (GRADE) | sim | `high` · `moderate` · `low` · `very_low`. **Reusa GRADE.** |
| `consensus` | objeto | não | Ver §5 (concordância de especialistas). Opcional na v1 (registro pode existir sem painel). |
| `evidence` | array | sim | Lista de itens de evidência (suporte/contra). Ver §4. |
| `relations` | array | não | Conexões a outras claims. Ver §6. |
| `gaps` | string | não | Principal lacuna ("falta ECR estratificado por HLA"). |
| `history` | array | sim | Histórico de versões imutável. Ver §7. |
| `curators` | array | sim | Curadores responsáveis (nome + ORCID + papel). |
| `coi` | string | não | Conflitos de interesse declarados relevantes à claim. |
| `created` / `updated` | date | sim | ISO 8601. |
| `license` | string | sim | `CC-BY-4.0` (default). |

## 3. `context` (PECO-like)

```json
{
  "population": "adult women meeting Consensus Definition X for lipedema",
  "condition": "lipedema",
  "exposure": "—",
  "comparator": "age-matched female controls",
  "outcome": "prevalence of joint hypermobility",
  "scope": "cross-sectional, observational"
}
```

## 4. `evidence[]` (item de evidência)

| Campo | Descrição |
|---|---|
| `ref` | Identificador da fonte: `PMID:…`, `DOI:…`, `NCT:…`. |
| `stance` | `supporting` · `contradicting` · `mentioning`. |
| `study_design` | `RCT` · `cohort` · `case_control` · `cross_sectional` · `case_series` · `systematic_review` · `meta_analysis` · `expert_opinion`. |
| `n` | Tamanho amostral (se aplicável). |
| `risk_of_bias` | `low` · `moderate` · `high` · `unclear`. |
| `year` | Ano. |
| `note` | Observação do curador. |

## 5. `consensus` (opcional)

```json
{
  "agreement_pct": 71,
  "trend": "increasing",
  "history": [{"date":"2022-01","pct":51},{"date":"2026-05","pct":71}],
  "by_specialty": {"angiology":82,"rheumatology":74,"dermatology":61},
  "by_region": {"europe":68,"north_america":74,"brazil":70},
  "controversy": "low",
  "votes_weighting": "by declared expertise + publication record + COI transparency"
}
```
> **Regra de ouro:** `evidence_confidence` (força da evidência), `consensus.agreement_pct`
> (concordância humana) e `knowledge_state` (síntese interpretativa) são **independentes**.
> Nunca colapsar num número só. Expor discrepâncias (ex.: alta concordância + evidência fraca).

## 6. `relations[]`

| Campo | Valores |
|---|---|
| `type` | `causes` · `associates` · `hypothesizes` · `contradicts` · `treats` · `contextualizes` · `co_occurs` · `depends_on` |
| `target` | `id` de outra claim, ex. `SCR-LIP-000089` |
| `strength` | 0.0–1.0 (opcional) |

## 7. `history[]` (imutável)

```json
[
  {"version":"1.0","date":"2021","change":"Initial hypothesis (1 study, n=34)","confidence":"very_low","by":"ORCID:…","rationale":"…"},
  {"version":"2.0","date":"2023","change":"Systematic review published","confidence":"low","by":"ORCID:…"},
  {"version":"3.0","date":"2025","change":"European multicenter study, n=412","confidence":"moderate","by":"ORCID:…"}
]
```

## 8. Exemplo completo (registro mínimo viável)

```json
{
  "id": "SCR-LIP-000001",
  "version": "3.0",
  "statement": "Among adult women meeting a consensus definition of lipedema, the prevalence of joint hypermobility is higher than in age-matched female controls.",
  "statement_pt": "Mulheres adultas com lipedema apresentam maior prevalência de hipermobilidade articular do que controles femininos pareados por idade.",
  "claim_type": "clinical_association",
  "context": {
    "population": "adult women meeting Consensus Definition X for lipedema",
    "condition": "lipedema", "exposure": "—",
    "comparator": "age-matched female controls",
    "outcome": "prevalence of joint hypermobility",
    "scope": "cross-sectional, observational"
  },
  "knowledge_state": "probable",
  "evidence_confidence": "low",
  "consensus": {"agreement_pct": 71, "trend": "increasing", "controversy": "low"},
  "evidence": [
    {"ref":"PMID:00000000","stance":"supporting","study_design":"systematic_review","risk_of_bias":"moderate","year":2023},
    {"ref":"DOI:10.0000/xxxx","stance":"contradicting","study_design":"cross_sectional","n":120,"risk_of_bias":"high","year":2024}
  ],
  "relations": [
    {"type":"co_occurs","target":"SCR-LIP-000089","strength":0.7},
    {"type":"contradicts","target":"SCR-LIP-000091"}
  ],
  "gaps": "No HLA-stratified RCT.",
  "history": [
    {"version":"1.0","date":"2021","change":"Initial hypothesis (1 study, n=34)","confidence":"very_low"},
    {"version":"3.0","date":"2025","change":"European multicenter study, n=412","confidence":"moderate"}
  ],
  "curators": [{"name":"Alexandre C. M. Amato","orcid":"0000-0003-4008-4029","role":"lead_curator"}],
  "created":"2026-05-30","updated":"2026-05-30","license":"CC-BY-4.0"
}
```

## 9. Notas de implementação (v1 = simples)

- **v1 pode ser uma planilha** (1 linha = 1 claim; campos aninhados achatados) **ou JSON**.
  Sem banco de grafos, sem IA. O grafo (`relations`) começa como colunas de referência.
- Interoperabilidade futura: mapear para **nanopublication** (assertion+provenance+pubinfo)
  e expor `evidence_confidence` em GRADE — facilita adoção e cumpre o reuso de padrões.
- IDs nunca são reciclados; claims "retiradas" recebem `knowledge_state` + nota no `history`,
  não são apagadas.
