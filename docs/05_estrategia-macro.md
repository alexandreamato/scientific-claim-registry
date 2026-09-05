# BIO / SCR — Estratégia Macro

> Como tornar o sonho concreto **mantendo o Dr. Alexandre Amato como figura central
> e legítima do núcleo** — sem que o projeto pareça vaidade pessoal (o que mataria a
> credibilidade de uma "infraestrutura pública"). Rascunho v0.1, 2026-05-30.

---

## 0. A tensão central (e como resolvê-la)

O conselho de IAs avisou: infraestrutura pública precisa parecer *neutra e governada*,
não o projeto de uma pessoa. Mas você **quer e deve** permanecer central. Esses dois
objetivos só são compatíveis sob um modelo específico: o **founder-steward** (fundador-
guardião), o mesmo de Linus Torvalds (Git), Barend Mons (nanopublications/FAIR),
ORCID e da Wikimedia.

A centralidade do Amato é **legítima** por três razões objetivas — e a estratégia
inteira se apoia nelas:

1. **Origem intelectual.** Você concebeu o framework. Prioridade documentada (OSF/
   Zenodo/DOI + este editorial) torna isso permanente e citável.
2. **O ativo único é seu.** O piloto de lipedema roda sobre a base da ABL/Instituto
   Amato (pacientes, consenso brasileiro, produção própria: HLA, TDAH, ferritina,
   hipotireoidismo, hipermobilidade). **Ninguém no mundo pode fazer o piloto de
   lipedema melhor que você.** Esse é o seu fosso.
3. **Papel de convener.** Quem reúne os especialistas, preside o conselho e define a
   metodologia detém a autoridade de fato — sem precisar "ser dono".

> **Princípio de design:** abrir o conhecimento (acesso, dados, claims) e manter
> fechado o *leme* (direção fundacional, metodologia, presidência do conselho).
> Aberto no produto, centralizado na governança fundadora.

---

## 1. Os dois ativos, separados (SCR vs BIO)

| | **SCR — Scientific Claim Registry** | **BIO — Biological Intelligence Observatory** |
|---|---|---|
| O que é | A instituição: registro público + IDs persistentes | O motor: metodologia, governança, camada viva |
| Analogia | ClinicalTrials.gov / CrossRef / GenBank | Quem *opera* o registro |
| Papel do Amato | **Founding Director** | **Principal Architect / Scientific Lead** |
| Estratégia | Aberto, neutro, "burocrático" (gera confiança) | Onde mora a sua marca metodológica |

Você opera o SCR através do BIO — exatamente como o CrossRef opera os DOIs.

---

## 2. Os papéis do Amato (centralidade explícita e defensável)

- **Founding Director do SCR** / **Chair do Steering Committee** — autoridade de direção.
- **Principal Investigator do BIO-Lipedema Pilot** — o caso concreto é seu.
- **Primeiro autor** dos documentos fundacionais (editorial SCR, framework v0.2,
  artigo do piloto). Prioridade intelectual citável: *"Amato (2026) first proposed…"*.
- **Convener** do conselho de especialistas e do painel de lipedema.
- **Guardião da metodologia** (a "constituição" do registro leva sua assinatura).

Mecanismos que protegem a centralidade sem comprometer a credibilidade:
- **Carta fundacional** que nomeia o Founding Director e descreve a sucessão (você
  define as regras desde o início).
- **Veto metodológico** do fundador na fase inicial (some gradualmente conforme o
  conselho amadurece — modelo "BDFL", *benevolent dictator for life*, com transição planejada).
- **Autoria perpétua**: o registro sempre cita seus documentos fundadores.

---

## 3. Veículo institucional

Para parecer infraestrutura (e captar recursos/parcerias), o projeto precisa de um
"corpo". Opções, da mais leve à mais robusta:

1. **Agora (custo ~zero):** projeto no **OSF** + **Zenodo com DOI** sob o guarda-chuva
   do *Amato Duo* / ABL. Estabelece prioridade e dá um lar institucional imediato.
2. **6–12 meses:** uma **iniciativa nomeada** ("BIO Initiative" / "SCR Initiative")
   com site próprio, conselho consultivo e identidade visual — ainda dentro do
   Amato Duo, mas com marca própria.
3. **12–24 meses (se vingar):** **associação/fundação sem fins lucrativos** ("BIO
   Foundation") com você como **fundador e diretor**, conselho científico e estatuto.
   É o modelo Cochrane/Epistemonikos/MAGIC — credível e elegível a fomento.

> Recomendação: comece em (1) já; só formalize (3) quando houver tração e gente
> externa querendo entrar. Não crie burocracia antes de existir demanda.

---

## 4. Roadmap em ondas (cada onda mantém você no centro)

### Onda 0 — Plantar a bandeira (agora → 30 dias)
- Publicar **framework v0.2 no OSF + Zenodo com DOI** (prioridade intelectual).
- Finalizar e submeter o **editorial do SCR** (este `docs/04_…`) — entrega fácil, comunica a ideia.
- Registrar 1 domínio âncora (ver `06_dominios.md`) e um landing page de 1 página.
- *Resultado: a ideia existe publicamente, datada, com seu nome.*

### Onda 1 — O registro-piloto (1–3 meses)
- **50 claims fundamentais de lipedema** com IDs `SCR-LIP-0000xx`, em planilha/JSON.
- Cada claim: statement canônico + contexto + evidências (suporte/contra) + GRADE +
  histórico + curador. **Curadoria 100% humana, sem IA, sem grafo.**
- Você é o curador-chefe; convida 3–5 especialistas como co-curadores fundadores.
- *Resultado: prova de execução — algo para mostrar a um pesquisador.*

### Onda 2 — Validação e rede (3–9 meses)
- **Artigo do piloto** (você 1º autor) descrevendo método e os 50 claims.
- Convidar 10–20 especialistas internacionais como "Founding Curators" (Herbst,
  Gianesini, grupos alemães/britânicos) — você os *convoca*, ficando central.
- Primeira tabela de diferenciação (vs Cochrane, vs IAs) vira material de palestra
  no seu próprio congresso/eventos da ABL ("From Static Consensus to Living Consensus").
- *Resultado: legitimidade externa sem perder o leme.*

### Onda 3 — A instituição (9–24 meses)
- Formalizar a **BIO Foundation** (se houver tração); estatuto com você como Diretor.
- Site do SCR como registro consultável; API mínima; primeiros IDs citados por terceiros.
- Buscar fomento (ver §6) e 1–2 doenças afins (linfedema, EDS) como segundos registros.
- *Resultado: deixa de ser ideia e vira infraestrutura nascente.*

---

## 5. Estratégia de publicação (3 camadas, você 1º autor em todas)

1. **Editorial SCR** (agora) → JMIR / PLOS Digital Health / Learned Publishing / BMJ H&CI.
2. **Position paper BIO v0.2** (3–6 meses) → Patterns / npj Digital Medicine / JMIR.
3. **BIO-Lipedema Pilot** (após 12 meses de piloto, com métricas) → npj Digital
   Medicine / Lancet Digital Health / JAMIA.

Cada paper cita os anteriores → você constrói uma trilha de prioridade que ancora
seu nome ao conceito de forma permanente.

---

## 6. Sustentabilidade / fomento (o problema que mata projetos assim)

A revisão de prior art mostrou: living reviews e living guidelines **morrem por falta
de financiamento**, não por falta de tecnologia. Planejar isso cedo:
- **Fase inicial:** autofinanciado pelo Amato Duo/ABL (baixo custo — é planilha + texto).
- **Parcerias:** Lipedema Foundation (EUA), sociedades médicas, indústria (GLP-1,
  compressão, diagnóstico) como patrocínio *sem* conflito na curadoria (scores com e
  sem conflito declarado — princípio do framework).
- **Fomento:** agências (CNPq/FAPESP no Brasil; Wellcome/abertura internacional depois).
- **Modelo de longo prazo:** acesso aberto por princípio + serviços premium
  (hospitais, indústria) — como já previsto na Fase 4 do framework.

---

## 7. Riscos e mitigação (resumo)

| Risco | Mitigação |
|---|---|
| Parecer "vaidade pessoal" | Modelo founder-steward + conselho externo + acesso aberto |
| Alguém publicar a tese antes (já há ClaimRxiv, abr/2026) | Publicar editorial **agora**; seu diferencial é execução + domínio, não conceito |
| Virar "mais um Cochrane" | Ancorar em claim+versionamento+grafo (tabela de diferenciação) |
| IA tornar obsoleto | Reposicionar como "a camada que as IAs consultam"; foco em governança |
| Morrer por falta de verba | Começar barato (planilha); só escalar com tração e parceria |
| Não-adoção dos IDs | Começar onde você controla a comunidade (lipedema/ABL) e expandir |

---

## 8. O sonho, em uma frase

> Criar a **ClinicalTrials.gov das afirmações científicas** — um registro público,
> versionado e governado de claims, nascido no lipedema e operado pelo método BIO —
> tendo o Dr. Alexandre Amato como fundador, arquiteto e guardião da metodologia.
