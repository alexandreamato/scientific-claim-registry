# Auditoria estrutural dos claims — 2026-06-02 (392 claims)

> ⚠️ **DOCUMENTO HISTÓRICO — JÁ REMEDIADO (2026-06-02).** Snapshot da auditoria quando havia 392 claims.
> As falhas listadas abaixo **foram corrigidas**: PECO 100% preenchido (R-CLM-15), grade×desenho capeado
> (R-CLM-13), dedup cross-pergunta 392→347 (R-OBJ-7), títulos em toda evidência (R-CLM-16), 0 órfãos,
> 0 evidências sem grade. Estado atual: **345 claims / 42 perguntas** (ver `README.md`). Mantido como registro.

Revisão por 8 subagentes (49 claims cada) + verificação programática. Critérios: PECO fraco,
grade×desenho, claim amplo, pergunta errada, linguagem forte sobre evidência fraca, duplicação.

## Achados sistêmicos (números duros)
- **PECO vazio: 338/392 (86%)** — `population/exposure/comparator/outcome` todos `—`. Causa: `make_claim`
  insere placeholders e nada preenche PECO depois. **É o problema nº 1.**
- **grade × desenho incompatível: 27 claims / 29 evidências** — 22 `review` com grade high/moderate,
  5 `case_series` moderate, 1 `case_report` moderate, 1 `basic_science` high. O `audit_quality.py` só checa
  contra o grau curado do `bib`; o desenho-do-estudo não é teto. **Gap a fechar (R-CLM-13 estende para desenho).**
- **grafo subutilizado:** só **1** claim sob >1 pergunta (de 392). O modelo é grafo, a prática é árvore.
- **0 claims órfãos.**

## Lista de trabalho (claims a curar, por tipo)

### Pergunta errada (relink/unlink) — prioridade alta
- **SCR-LIP-000103** (alta): scoping review "social problem" ligado à pergunta de **ADHD** (SQ-006) — não trata ADHD.
- **SCR-LIP-000377** (alta): estudo de **BCRL/MRI** ligado à pergunta de diferenciar lipedema×linfedema — não trata.
- **SCR-LIP-000384** (média): liposucção de **linfedema** sob diferenciação lipedema×linfedema.
- **SCR-LIP-000390** (média): auto-declara que **não avaliou** bariátrica/perda de peso, mas está sob SQ-024.
- **SCR-LIP-000058, 061, 166, 298** (média): statements que **explicitamente dizem não tratar** a pergunta à qual estão ligados.
- **SCR-LIP-000133** (média): VTE-outcomes (título) sob varizes/doença venosa.
- Menores (low, role=context aceitável): 162, 179, 182, 205, 244, 272, 273, 296, 299, 337, 339.

### grade × desenho (rebaixar) — 27 claims
Altos: **030** (scoping review→high), **041** (basic_science preliminar→high), **058/067** (case_series/SR→high),
**085** (revisão narrativa→moderate), **109** (review→high), **122** (case_report→moderate), **251** (case_series→moderate).
Médios: 036, 050, 095, 115, 250, 270, 285, 317. Menores: 001, 215, 227, 233, 307, 316, 318, 321, 361, 373.

### Claim amplo / não atômico (R-Q-6) — candidatos a split
Genética (umbrella de muitos loci/genes): **220, 223, 228, 235, 238**, e 216, 217, 219, 226, 231, 240.
Imagem (múltiplas modalidades num claim): **378, 383**, 195, 197, 363, 375, 360, 362.
Manejo: 050, 163, 165. Mecanismo: 149, 154, 302, 303, 304, 311. Outros: 037, 100, 108, 350, 346, 371, 388.

### Linguagem forte sobre evidência fraca (suavizar)
**098** ("causally linked" em revisão narrativa), 097, 209, 212, 314, 383 (alta/média); 071, 088, 181, 182 (baixa).

### Duplicados / quase-iguais (dedup) — pendente de passe próprio
Cluster de **genética** re-ingere os mesmos papers (obr.13953, s44324, eurrev_18292, lrb.2023.0065) em
216/235, 217, 220, 223, 228, 235, 238, 240. Imagem: 195≈197. Comorbidade: 127≈144. Diagnóstico: 272/285 (mesmo DOI, grade divergente).

## Remediação recomendada (em ordem)
1. **grade×desenho** (auto): estender o teto p/ desenho-do-estudo + re-cap + recompilar afetadas. ~Barato/médio.
2. **wrong_question** (curado): unlink/relink os ~8 de alta/média. Recompilar as perguntas tocadas.
3. **PECO** (sistêmico): preencher PECO real (derivado do statement+evidência por LLM) — 338 claims, maior esforço;
   ou gerar PECO na recompilação. Decidir custo.
4. **dedup genética/imagem** (passe próprio, como o de perguntas R-Q-5, na camada de claim).
5. **broad/split** e **overconfident**: curadoria mais fina, por último.
