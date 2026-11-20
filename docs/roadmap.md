# SCR — Roadmap

## Próxima entrega · respostas citáveis e mudanças rastreáveis

O piloto de lipedema já tem perguntas estáveis, proposições gerais e achados por estudo. A próxima entrega deve demonstrar o que o SCR oferece ao leitor ao longo do tempo. O recorte proposto são **três perguntas, com duas versões recuperáveis por pergunta**, escolhidas por terem material histórico suficiente e mudanças que possam ser explicadas pelos achados registrados.

1. **Preservar as versões publicadas.** Guardar um artefato por ID de pergunta e versão com a síntese bilíngue, data de corte, proposições e respectivos estados ou versões, achados e referências usados na síntese. Preservar as URLs já publicadas e manter os artefatos em armazenamento durável, acessível ao build. Uma alteração no conteúdo citável exige nova versão. Recuperar versões antigas a partir dos artefatos preservados e identificar no histórico aquelas cujo conteúdo completo está indisponível.
2. **Unificar a atualização no modelo da v0.6.** Integrar a vigilância à incorporação por achados. Validar a fonte, o trecho, a interpretação e o vínculo com a proposição. Identificar todas as perguntas ligadas, recompilar as sínteses afetadas e revisar o diff antes de publicar o conjunto. Registrar a incorporação mesmo quando a conclusão é mantida e explicar a decisão. Reprocessar uma entrada sem duplicar achados.
3. **Checar a integridade em CI.** A partir de um checkout limpo, validar o build bilíngue, a recuperação de versões e a estabilidade de seus artefatos. Checar vínculos, contagens de claims ativos e arquivados entre banco, site e exportação, e projeção dos achados no SQLite. Usar os dados do registro para gerar as contagens exibidas na documentação.
4. **Mostrar o que mudou na página da pergunta.** Logo abaixo da resposta curta, exibir a versão anterior, o achado novo, sua população e seu desfecho, e a mudança introduzida na síntese. Mostrar separadamente a última busca, a última mudança da resposta e a certeza por desfecho. Usar *Knowledge Freshness* para indicar a recência das fontes. Documentar a cobertura das fontes e submeter mudanças de maior impacto a revisão independente, conforme o [plano metodológico](spec/methodology.md#6--atualização-planejada-do-piloto).

**Critério de aceite.** Em cada uma das três perguntas, um leitor consegue abrir a URL de qualquer uma das duas versões, identificar a mudança na resposta e seguir a referência até o trecho que a sustenta. Um build limpo recupera as duas versões a partir dos artefatos preservados e confirma que seus conteúdos permanecem iguais.

O primeiro recorte arquivado reúne **SQ-LIP-000010** (1.7 e 1.8), **SQ-LIP-000031** (1.4 e 1.5) e **SQ-LIP-000039** (1.3 e 1.4). Os [registros recuperados do Git](../registry/question_versions) têm HTML bilíngue, JSON e links da mudança editorial para as evidências arquivadas. A integração com a vigilância e a validação contínua em CI seguem planejadas.

Expansão para outros domínios e formatos adicionais de interoperabilidade ficam para depois da validação do piloto. O cronograma abaixo registra o plano original.

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
