# SCR-LIP v0.1 — Revisão crítica dos 50 claims (2026-05-30)

Revisão de qualidade do registro-piloto. Curador-revisor: Claude (assistente), para
validação posterior do Dr. Amato. Objetivo: caçar erros, escopo indevido, calibração
GRADE exagerada e duplicação — não elogiar.

## 1. Verificação de DOIs (amostragem)

DOIs foram **extraídos dos PDFs originais** pelos agentes. Spot-check resolvido:
- `10.1590/1677-5449.202101981` (pt) e `…202101982` (en) → **mesmo artigo** SciELO (prevalência 2022). Sem erro; são variantes de idioma. Registro usa o `…981`.
- `10.64898/2025.12.02.25341445` → preprint **real do medRxiv** (NHANES câncer). Prefixo `10.64898` é do medRxiv.
- `10.7759/cureus.35570` (TDAH) → plausível/consistente.
> ⚠️ **Ação do autor:** antes de qualquer publicação externa, conferir cada DOI contra
> a versão publicada (alguns são preprints e podem ter ganho DOI de revista — ex.: o
> NHANES celíaca tem preprint `10.64898/…` **e** versão Cureus `10.7759/cureus.104222`).

## 2. Correção de ESCOPO (aplicada)

Dois claims **não eram sobre lipedema** — ligavam-se a ele apenas por inferência:
- ~~`018` caso nutcracker+EDS (Amato 2020)~~ → **substituído** por **lipolinfedema**
  (complicação do lipedema avançado; consenso). Mais relevante e lipedema-cêntrico.
- ~~`019` tríade hEDS-MCAS-IgG (Brock 2021, coorte de EDS)~~ → **substituído** por
  **impacto funcional / limitação de AVDs** (consenso).
A comorbidade hipermobilidade segue coberta pelo `017` (Fiengo, 44% — lipedema-cêntrico).
> Princípio reforçado: preferir artigos do autor **quando forem sobre lipedema**. O
> artigo nutcracker+EDS é dele, mas não é um claim de lipedema.

## 3. Calibração GRADE (avaliação — sólida no geral)

Amostragem confere com as regras de honestidade:
- Transversal único / série de casos → `emerging`/`low` ou `speculative`/`very_low`. ✔
- Meta-análises (lipoaspiração `030`, cetogênica `035`) → `probable`/`moderate`. ✔
- Revisão sistemática sem estudos (gestrinona `040`) → `established` de **ausência de evidência**. ✔
- Consenso Delphi (`044`–`050`, `018`, `019`) → marcado `study_design: consensus`,
  `evidence_confidence: low` (concordância ≠ evidência primária). ✔
- Achados externos fortes (M2/CD163 Wolf `042`) → `probable`/`moderate`. ✔

Pontos para o autor confirmar (números marcantes, mantidos com baixa confiança):
- `027` perfil imunometabólico favorável: **HOMA-IR 44,2% menor** (p<0,001) — número
  grande; confirmar no artigo. Mantido `emerging`/`low`.
- `028` câncer OR 0,795 e `029` OR 0,67 (não-obesas) — confirmar IC/E-values.

## 4. Duplicação / sobreposição (avaliada — aceitável)

- `001` (entidade distinta) · `003` (sem relação causal com obesidade / IMC limitado) ·
  `044` (gordura desproporcional e resistente a perda de peso): **três facetas** da
  diferenciação vs obesidade. Sobreposição parcial, mas cada uma é um claim distinto e
  citável. Mantidos. (Candidatos a *merge* numa versão futura, se o autor preferir.)
- `015`/`016` (TDAH: prevalência vs correlação dose-resposta) — granularidade desejável
  num registro de claims. Mantidos.
- `025`/`026` (celíaca: bruto vs estratificado por IMC) e `028`/`029` (câncer: geral vs
  não-obesas) — granularidade legítima. Mantidos.

## 5. Qualidade dos enunciados

- Todos têm contexto explícito (PECO-like), `gaps` honesto e `statement_pt`. ✔
- `relations` está **semeado** (target_hint) mas ainda não resolvido para IDs reais —
  é o próximo passo (montar o grafo conectando, ex., TDAH/fibromialgia/hipermobilidade).

## 6. Fronteira com a teoria IIT2 (conferida)

Nenhum claim do registro afirma a teoria IIT2/gfWAT. Os achados empíricos que a
inspiraram permanecem como observações independentes, atribuídas às fontes primárias:
- `041` histamina elevada (Bonetti), `042` assinatura M2/CD163 (Wolf), `043` padrão QST
  (Dinnendahl), e as associações HLA/celíaca/câncer/IgG (`023`–`029`, estudos do autor).
A teoria continua em `_held_out_theory.json` (13 itens), fora do registro.

## 7. Resultado pós-revisão

- **50 claims** · 44/50 ancorados em artigos do autor · 100% lipedema-cêntricos.
- Estado: 4 established · 13 probable · 31 emerging · 2 speculative.
- Tipos: 19 associação clínica · 10 terapêuticos · 8 diagnósticos · 5 epidemiológicos ·
  4 definicionais · 3 causais · 1 prognóstico.

## 8. Recomendações para a v0.2 do piloto

1. Autor valida texto/GRADE de cada claim (planilha `claims.csv`).
2. Resolver `relations` → IDs reais (montar o grafo de conhecimento).
3. Adicionar camada `consensus` (painel de especialistas votando cada claim).
4. Conferir DOIs preprint→publicado; padronizar versão citada.
5. (Opcional) decidir *merge* dos três claims de diferenciação vs obesidade.
