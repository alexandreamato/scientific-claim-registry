# BIO: Biological Intelligence Observatory
## Um Framework para Conhecimento Científico Vivo

> Versão rica em português (a mais detalhada produzida na conversa de origem).
> Contém a analogia Git, anatomia da claim, arquitetura, métricas e roadmap.

## Sobre o Nome

BIO é a escolha certa. Curto, memorável, universal e biologicamente evocativo
(βίος = vida em grego). Funciona identicamente em português e inglês.

**BIO: Biological Intelligence Observatory** — o observatório de inteligência
biológica para conhecimento científico vivo. (Alternativa justificável:
"Biomedical" no lugar de "Biological".)

Tagline: *"O Git do conhecimento médico"* — intuitivo, memorável, comunica a
disrupção em uma frase. (Nota do conselho/refino: usar como metáfora pública,
não como descrição técnica.)

## O Problema que o BIO Resolve

A medicina moderna vive um paradoxo: nunca produzimos tanta ciência (um artigo
indexado a cada poucos segundos no PubMed) e nunca foi tão difícil saber o que é
verdade hoje. Artigos são fotografias. Revisões sistemáticas são fotografias que
envelhecem. Diretrizes são fotografias votadas por um comitê, publicadas anos
depois. O conhecimento existe em fragmentos desconectados, fossilizados,
impossíveis de auditar. O Git resolveu problema análogo no software.

## A Tese Central: A Afirmação como Unidade Fundamental

O mundo organiza ciência em torno de artigos. O BIO organiza em torno de
**afirmações científicas (claims)**. A afirmação se torna o objeto central; o
artigo vira uma fonte de evidência — um commit no histórico daquela afirmação.

## Analogia com Git → Medicina

| Conceito Git | Equivalente BIO | Significado prático |
|---|---|---|
| Repositório | Grafo de conhecimento de uma doença | Mapa vivo do lipedema |
| Commit | Atualização de uma afirmação | Novo estudo incorporado |
| Branch | Hipótese divergente / controvérsia | Duas escolas coexistindo |
| Pull Request | Proposta de revisão científica | Especialista sugere alterar claim |
| Merge | Convergência de consenso | Evidências resolvem controvérsia |
| Merge Conflict | Conflito de evidências ativo | Dois ECRs com conclusões opostas |
| Blame / Log | Proveniência completa | Quem disse o quê, quando, com que evidência |
| Tag / Release | Snapshot oficial | "BIO-LIP Consenso v2025.1" |
| Fork | Linha divergente institucional | Escola cirúrgica com protocolo próprio |

## Os Cinco Princípios Fundamentais

1. **Afirmações são mais importantes que artigos.** Artigos são fontes de evidência.
2. **Conhecimento deve ser versionado.** Histórico completo, imutável, auditável.
3. **Conhecimento deve ser conectado.** Grafo semântico, não documentos isolados.
4. **Consenso é processo, não evento.** Revisão contínua, transparente, rastreável.
5. **IA assiste, humano decide.** A autoridade final é sempre humana.

## Anatomia de uma Afirmação BIO

```
BIO-LIP-000001

Afirmação:
"Mulheres com lipedema apresentam maior prevalência de
hipermobilidade articular em comparação com a população feminina geral."

Tipo: Associação clínica
Domínio: Comorbidades / Tecido conjuntivo
Status: Provável
Score de confiança: 67/100
Score de consenso: 71% (crescente — era 51% em 2022)
Especialidades: Angiologia 82%, Reumatologia 74%, Dermatologia 61%
Distribuição geográfica: Europa 68%, América do Norte 74%, Brasil 70%
Qualidade da evidência: Observacional, risco de viés moderado
Evidências de suporte: 8 estudos observacionais, 1 revisão sistemática
Evidências contrárias: 1 estudo (2024), heterogeneidade metodológica

Histórico de versões:
├── v1.0 (2021): Hipótese inicial — 1 estudo, n=34 — confiança: 23%
├── v2.0 (2023): Revisão sistemática publicada — confiança: 61%
└── v3.0 (2025): Estudo multicêntrico europeu, n=412 — confiança: 67%

Conexões no grafo:
→ Síndrome de Ehlers-Danlos Hipermóvel (BIO-LIP-0089)
→ Frouxidão de colágeno / Matriz extracelular (BIO-LIP-0103)
→ Controvérsia ativa com BIO-LIP-0091
```

## Arquitetura em Quatro Camadas

```
CAMADA 4 — INTERFACE         Clínicos, pesquisadores, pacientes consultam o "estado atual da verdade"
CAMADA 3 — CONSENSO VIVO     Especialistas validam, contestam, qualificam (IA sugere, humano decide)
CAMADA 2 — GRAFO             Claims conectados por relações semânticas com pesos de evidência
CAMADA 1 — VIGILÂNCIA        IA monitora literatura, extrai claims, sinaliza atualizações
```

**Camada 1 — Vigilância:** monitora PubMed, Embase, Cochrane, bioRxiv, medRxiv,
ClinicalTrials.gov. Nova publicação → extração de claims (NLP+LLM) → matching com
claims existentes → notifica painel (existente) ou cria/classifica (novo).

**Camada 2 — Grafo:** nós (doenças, fenótipos, sintomas, biomarcadores,
mecanismos, intervenções, desfechos). Arestas com força e proveniência: CAUSA,
ASSOCIA, HIPÓTESE, CONTRADIZ, TRATA, CONTEXTUALIZA, COOCORRE.

**Camada 3 — Consenso Vivo:** especialistas verificados endossam / discordam (com
justificativa) / qualificam / propõem PR / sinalizam conflito. Voto ponderado por
expertise, histórico de publicações e COI declarado. Conflitos mapeados como "Conflito Ativo".

**Camada 4 — Interface e Produtos:** Diretrizes vivas (snapshots versionados),
Mapa de controvérsias, Atlas de lacunas, Alertas de atualização, Ferramentas clínicas.

## Métricas Próprias do BIO

| Métrica | Descrição |
|---|---|
| Evidence Confidence Score (ECS) | Desenho, n, consistência, viés, magnitude do efeito (0–100) |
| Consensus Agreement Score (CAS) | % ponderado de concordância entre especialistas |
| Knowledge Stability Index (KSI) | Se a afirmação está estável ou mudando rápido |
| Controversy Index | Divergência + evidências conflitantes + heterogeneidade |
| Clinical Actionability Score | O quanto muda diagnóstico ou conduta |
| **Knowledge Contribution Score (KCS)** | "Impact Factor 2.0" — reputação por curadoria de claims |

## Por Que o Lipedema é o Caso-Piloto Perfeito

Campo emergente com literatura em explosão; ausência de fonte única confiável;
comunidade de pacientes engajada; alta multidisciplinaridade; controvérsias ativas
bem definidas; lacunas identificáveis; atraso diagnóstico de 10–15 anos.
> "Se o BIO funcionar no lipedema — campo caótico, fragmentado e em disputa — ele
> funciona em qualquer área da medicina."

## Modelo de Governança

Usuários públicos (veem tudo) · Colaboradores (sugerem) · Revisores especializados
· Editores (aprovam/gerenciam conflitos) · Conselho científico (regras, disputas,
auditoria). Transparência obrigatória: COI de todo contribuidor; scores com e sem
especialistas com conflito; todo commit registrado; reversões auditáveis.

## Roadmap de Implementação

- **Fase 0 — Manifesto (imediato):** publicar framework como position paper (Lancet
  Digital Health, npj Digital Medicine, JMIR). Planta a bandeira intelectual.
- **Fase 1 — Prova de Conceito (M1–6):** 50–100 claims de lipedema; formato BIO
  completo; primeiro grafo; 10–20 "Core Maintainers"; interface web (Neo4j + web simples).
- **Fase 2 — Validação (M7–12):** motor de vigilância; painel de consenso;
  "BIO-Lipedema Consenso v1.0"; coletar dados de uso. Meta: 3 centros de referência;
  incorporação de nova evidência < 30 dias.
- **Fase 3 — Expansão (M13–24):** documentar replicação; 2–3 condições afins
  (linfedema, EDS, endometriose); APIs para prontuário; parcerias.
- **Fase 4 — Ecossistema (M25+):** plataforma multi-especialidade; educação médica;
  código aberto; modelo financeiro sustentável (gratuito + premium hospitais/indústria).

## A Visão em Uma Frase

O BIO transforma o conhecimento médico de documentos estáticos em um organismo
vivo, versionado e auditável — onde afirmações científicas substituem artigos como
unidade central da ciência, e o consenso deixa de ser um evento para se tornar um
processo contínuo, transparente e colaborativo.
