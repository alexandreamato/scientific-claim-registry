# Estratégia de criação de Perguntas e Claims

> Como o registro **cresce**: de onde vêm as perguntas (SQ-) e os claims (SCR-). Regra canônica
> resumida em `RULES.md` (R-Q-4); detalhamento aqui.

## Princípio

> **Pergunta = unidade de DEMANDA** (o que cientistas/clínicos/pacientes perguntam).
> **Claim = unidade de EVIDÊNCIA** (o que os artigos dizem).

A criação de **perguntas** é dirigida por **demanda + cobertura + literatura**; a de **claims**, pelo **loop**
de vigilância. São dois motores distintos.

### Princípio mestre: FOCO (R-Q-6)

> **Quanto mais objetiva a pergunta, mais alta a qualidade dos claims.**

Perguntas e claims são **propositadamente focados, restritos, direcionados, objetivos**. Uma pergunta tem
**uma única relação** (uma exposição/intervenção × um desfecho), **população e contexto delimitados**, e é
**empiricamente respondível** por uma busca focada. É **proibido** criar perguntas **amplas, abertas,
guarda-chuva ou subjetivas** — elas diluem a recuperação e produzem claims confusos. Lacuna ampla → **decompor**
em várias perguntas estreitas, ligadas por `related` (R-Q-5).

| ❌ Ampla / aberta / subjetiva | ✅ Estreita / objetiva / respondível |
|---|---|
| O que causa o lipedema? | O lipedema está associado a doença da tireoide? |
| Como tratar o lipedema? | A terapia descongestiva completa reduz dor no lipedema? |
| Qual a melhor dieta? | Uma dieta cetogênica reduz o volume dos membros no lipedema? |

Por que importa (evidência prática): a SQ-LIP-000021 ("TDC reduz dor/volume **em lipedema**?") permitiu ao
classify **descartar limpo 7 artigos de linfedema** de uma reading list e manter só os 2 de lipedema — porque
o alvo era nítido. Uma pergunta ampla ("como tratar lipedema?") teria misturado tudo. **Claims** seguem o mesmo:
**atômicos**, uma afirmação verificável cada (R-CLM-1). Este é o princípio que rege planejamento, estrutura e
estratégia do registro inteiro.

---

## A. Claims — `registry/loop.py` (Layer 1, maduro)

Automático e reprodutível: **retrieval** (biblioteca `bib` semântica + Europe PMC + reading lists) →
**classify** (LLM forte, relevância à pergunta específica, prioriza análise ajustada) → **promove** claim
novo **ou corrobora** existente (merge conservador: achado distinto = novo; restatement = evidência anexada)
→ **recompila/versiona** a resposta. Salvaguardas: `verify_ref`, peso por qualidade (R-CLM-11), dedup
**por-pergunta** (grafo — um artigo gera claims em várias perguntas), sempre os artigos do autor (R-CLM-12),
banimento/retratação (R-CLM-10), datas (R-VER-5). **Claims só nascem sob uma pergunta existente.**

## B. Perguntas — `registry/propose_questions.py` (4 fontes)

O loop **não** cria perguntas. Estas vêm de 4 fontes, sob um **ciclo de vida** comum:

1. **Cobertura taxonômica** (`propose_questions.py coverage`). Mapeia as perguntas existentes sobre os
   **eixos** (as tags: Definition, Epidemiology, Diagnosis, Imaging, Comorbidities, Pain, Pathophysiology,
   Treatment, Surgery, Diet, Management, Progression, Vascular, History…). Mostra eixos vazios/finos.
2. **Descoberta pela literatura** (o "loop inverso"). Um LLM forte propõe perguntas **novas e neutras** nas
   lacunas; cada uma é **aterrada** na biblioteca do autor (`bib /semantic`) — só conta se houver ≥1–2
   artigos relevantes. Literatura-dirigida, não inventada. Saída → `proposed_questions.json`.
3. **Proposta humana** — inbox (`site/submit.php`, R-MR-5) + curadoria.
4. **Ferramentas externas** — cada saída do Consensus/PubMed É uma pergunta; importável.

### Ciclo de vida (governança, docs/spec/id-allocation)

```
proposta → TEMP id (SQ-LIP-D######) em proposed_questions.json
         → curadoria humana:  promote → FINAL (SQ-LIP-######, knowledge_state=speculative, claims:[])
                              merge   → aponta a uma pergunta existente
                              reject  → tombstone
         → loop.py <FINAL> --source library --commit   (popula os claims, recompila a resposta)
```
Validar = **identidade** (bem-formada, neutra, não-duplicada, aterrada), **não verdade** (R-ALLOC-4).
Perguntas nascem `speculative` com resposta "nenhuma evidência indexada ainda" até o loop rodar.

### Comandos
```bash
python3 propose_questions.py            # cobertura + descoberta → proposed_questions.json
python3 propose_questions.py list
python3 propose_questions.py promote SQ-LIP-D000001   # → SQ-LIP-###### em questions.json
python3 propose_questions.py reject  SQ-LIP-D000001
```

## Critérios de qualidade de uma boa pergunta
- **Neutra** (não embute conclusão) — R-Q-1.
- **Navegável e única** (uma relação por pergunta; sem sobreposição com perguntas existentes).
- **Respondível pela evidência** (empírica, não filosófica) e **aterrada** (≥ alguns artigos).
- **No eixo certo** (tags), para a cobertura se manter mapeável.

## Estado
Cobertura atual: **25 perguntas / 392 claims**, 22/22 eixos com ≥1 pergunta. `propose_questions.py`
implementado (cobertura + descoberta Opus + ciclo temp→final).
