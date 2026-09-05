# Metodologia do SCR — fluxogramas

Visão de processo do **Scientific Claim Registry**. Fonte canônica das regras citadas (`R-…`):
[`RULES.md`](./RULES.md). Em caso de conflito, o RULES.md prevalece (R-DOC-1).

> *"PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to scientific questions."*
> O SCR **registra, não arbitra.**

---

## 1 · Modelo de objeto e camadas

A **pergunta** é o objeto central navegável; **claims** são evidência versionada ligada a ela com um
*papel*; **artigos** são as fontes. Um artigo pode informar claims sob várias perguntas → é um **grafo**,
não uma árvore. Só a **Layer 1** precisa existir; Consensus e Recommendation são camadas opcionais acima.

```mermaid
flowchart TD
    U(["Usuário · LLM · agente"]) --> SQ
    subgraph L1["Layer 1 · Registry — o produto (automatizável). Registra, não arbitra"]
        direction TB
        SQ["❓ Pergunta — SQ-LIP-000001<br/>objeto central · navegável · neutro · versionado"]
        SQ --> C1["📄 Claim SCR-LIP-…<br/>role: Consistent"]
        SQ --> C2["📄 Claim SCR-LIP-…<br/>role: Conflicting"]
        SQ --> C3["📄 Claim SCR-LIP-…<br/>role: Refining / Contextual"]
        C1 --> A1["🔬 Artigo · DOI/PMID"]
        C2 --> A2["🔬 Artigo · DOI/PMID"]
        C3 --> A1
    end
    SQ2["❓ Outra pergunta"] --> A1
    L1 -. opcional .-> L2["Layer 2 · Consensus<br/>especialistas endossam / discordam / qualificam"]
    L2 -. opcional .-> L3["Layer 3 · Recommendation<br/>sociedades médicas → conduta clínica"]

    SQ -. expõe .-> JSON[/"/q/&lt;id&gt;.json · machine-first<br/>resposta = renderização versionada (R-OBJ-6):<br/>Bottom line → Resumo executivo → outcomes por desfecho → claims<br/>3 dimensões SEMPRE separadas: Evidence Confidence · Consensus · Knowledge State"/]

    style SQ fill:#13315c,color:#fff
    style L1 fill:#eef4ff
```

---

## 2 · Loop de vigilância da Layer 1 (o coração da metodologia)

Ciclo automático e fechado: **retrieval → classify → verify/ban/ceiling → merge → recompile → version →
deploy**, que se realimenta quando nova literatura aparece.

```mermaid
flowchart TD
    subgraph SRC["1 · Retrieval semântico (R-AI-7)"]
        BIB["bib /semantic<br/>biblioteca curada do autor<br/>embeddings + ficha estruturada"]
        EPMC["Europe PMC"]
        DOIL["Reading lists de DOIs<br/>--doi-file"]
        CONTRA["gather_contra · SEMPRE (R-AI-12)<br/>Europe PMC null/negativo +<br/>semântica contrária → anti-viés"]
    end
    SRC --> CAND["Candidatos<br/>título · abstract/ficha · DOI · grau curado"]

    CAND --> CLS{"2 · Classify — LLM Opus 4.8 (R-AI-6)<br/>relevante? stance? study design? grade?"}
    CLS -->|não relevante| D1["descarta"]
    CLS -->|relevante| VER{"verify_ref<br/>DOI resolve em doi.org?"}
    VER -->|não| D2["descarta · não verificável"]
    VER -->|sim| BAN{"está em exclude.json?<br/>retratado / baixa qualidade"}
    BAN -->|sim| D3["bloqueia · R-CLM-10"]
    BAN -->|não| CEIL["cap_grade · grau curado do bib = TETO<br/>N6 nunca entra como moderate · R-CLM-13<br/>+ PECO e título gravados na ingestão · R-CLM-15/16"]

    CEIL --> MATCH{"3 · match_existing<br/>dedup CROSS-pergunta · R-OBJ-7<br/>1 achado = 1 claim ligado a N perguntas (grafo)"}
    MATCH -->|"mesmo achado, outra pergunta"| LINK["liga claim existente<br/>(novo papel, sem duplicar)"]
    MATCH -->|"restatement (mesma coisa)"| CORR["corrobora<br/>add_evidence ao claim existente"]
    MATCH -->|"achado distinto"| NEW["promove<br/>make_claim · novo SCR-LIP"]

    LINK --> BASE[("Base de evidência da pergunta<br/>claims.json + scr.db<br/>evidência é PERMANENTE · R-CLM-9")]
    CORR --> BASE
    NEW --> BASE

    BASE --> RECOMP["4 · recompile — Opus<br/>compila a resposta sobre TODA a base acumulada<br/>ponderada por qualidade · R-CLM-11 · evidence-bounded<br/>+ outcomes por desfecho (sintoma≠doença) · R-Q-7<br/>+ bottom_line de 2 frases · R-SITE-14"]
    RECOMP --> VERS["5 · versiona<br/>snapshot imutável v1.x<br/>created / updated / history · R-VER-5<br/>Knowledge Freshness recalculada"]
    VERS --> BUILD["build_questions.py + build_site.py<br/>HTML + JSON · EN + PT"]
    BUILD --> DEP["rsync deploy + purge Cloudflare"]
    DEP --> SITE(["scientificclaims.org<br/>página SQ-LIP + /q/&lt;id&gt;.json"])

    SITE -.->|nova literatura ao longo do tempo| SRC

    style BASE fill:#0f1b2d,color:#fff
    style CEIL fill:#1f4e3d,color:#fff
    style SITE fill:#13315c,color:#fff
```

---

## 3 · Estratégia de criação de perguntas (R-Q-4 · `propose_questions.py`)

A outra metade do loop: como novas **perguntas** nascem, com lastro na literatura, antes de virarem
oficiais. Ciclo de ID temp → final (R-ALLOC).

```mermaid
flowchart TD
    COV["coverage()<br/>tally por eixos/tags<br/>onde há lacuna?"] --> DISC["discover() — Opus<br/>propõe perguntas para as lacunas"]
    DISC --> GATE{"portão de canonicalização · R-Q-5<br/>judge_same vs text+phrasings existentes<br/>same / related / novel?"}
    GATE -->|"same (conf ≥ 0.85)"| MERGEQ["funde como PHRASING<br/>na pergunta canônica<br/>(NÃO cria SQ novo)"]
    GATE -->|"related"| RELQ["cria SQ + link related<br/>(veja-também)"]
    GATE -->|"novel"| GND{"grounding<br/>bib_search ≥ N hits<br/>tem literatura?"}
    RELQ --> GND
    GND -->|não| REJ["reject (sem lastro)"]
    GND -->|sim| STAGE[/"proposed_questions.json<br/>ID temporário SQ-LIP-D######"/]
    STAGE --> REV{"revisão humana<br/>(opcional)"}
    REV -->|promove| PROMO["promote()<br/>→ SQ-LIP-###### final<br/>knowledge_state: speculative · claims: []"]
    REV -->|descarta| REJ
    PROMO --> LOOP(["entra no loop de vigilância<br/>(diagrama 2) para acumular claims"])

    style STAGE fill:#eef4ff
    style MERGEQ fill:#1f4e3d,color:#fff
    style LOOP fill:#13315c,color:#fff
```

> **R-Q-5 — pergunta canônica + frases alternativas.** O `text` canônico é estável; `phrasings`/`phrasings_pt`
> são formas alternativas de fazer a MESMA pergunta. O portão acima impede duplicar perguntas semanticamente
> iguais (paráfrase → vira phrasing). As phrasings alimentam a **busca** do site, o **JSON/API** (roteamento
> machine-first de qualquer formulação → SQ canônico) e aparecem como *"Também perguntada como"* na página.

---

## 4 · Higiene e qualidade contínua (rede de segurança)

Controles que rodam **fora** do fluxo de ingestão para garantir que a base não degrade. Semanal via
`launchd` (`cron_retractions.sh`).

```mermaid
flowchart TD
    CRON(["cron semanal · launchd<br/>cron_retractions.sh"]) --> RETR["1 · curate.py check-retractions --ban<br/>varre DOIs no Crossref (retraction) → auto-ban R-CLM-10"]
    RETR --> TITLE["1b · enrich_evidence.py<br/>auto-cura títulos faltantes + guard --check<br/>(hover sem DOI cru · R-CLM-16)"]
    TITLE --> SWEEP["2 · varredura de contradição ROTATIVA<br/>2 perguntas/semana · loop --source all<br/>caça evidência contrária SEMPRE · R-AI-12"]
    SWEEP --> LANG["2b · lang_check.py<br/>guard de vazamento de idioma PT/EN/ES · R-SITE-16"]
    LANG --> CHG{"3 · seeds mudaram?"}
    CHG -->|sim| BUILD["build + deploy + purge Cloudflare<br/>(SCR_CF_TOKEN)"]
    CHG -->|não| AUD
    BUILD --> AUD["4 · audit_quality.py (relatório)<br/>evidence.grade × grau curado do bib"]
    AUD --> ACH{"algum guard/super-avaliação alertou?"}
    ACH -->|sim| WARN["⚠ log alerta<br/>(grade>teto → --fix · idioma/título → corrigir)"]
    ACH -->|não| OK["base limpa"]

    MAN(["curadoria humana manual<br/>(opcional, R-MR)"]) -.-> BANMAN["curate.py ban &lt;doi&gt;<br/>baixa qualidade por avaliação humana"]
    BANMAN -.-> RETR

    style WARN fill:#5c1a1a,color:#fff
    style OK fill:#1f4e3d,color:#fff
    style TITLE fill:#1f4e3d,color:#fff
    style LANG fill:#1f4e3d,color:#fff
```

---

### Três camadas que garantem a qualidade do grade (R-CLM-13)

1. **Entrada** — teto na ingestão (`cap_grade`): o grau curado da biblioteca limita o grade do LLM.
   *Não entra errado.*
2. **Vigilância** — `audit_quality.py` no cron: detecta qualquer super-avaliação que escape.
   *Se entrar, é detectado.*
3. **Passado** — migração já aplicada (45 rebaixados + 161 preenchidos). *O que estava errado, corrigido.*

*Limite honesto:* a garantia de teto cobre artigos **na biblioteca curada**. Fontes só do Europe PMC não
têm grau curado — para esses sobra a heurística (tipo fraco + grade alto). Curar no `bib` antes de promover
a evidência forte fecha 100%.

**Guards automáticos no cron (rede de segurança da automação):** além do teto de grade (R-CLM-13), o ciclo
semanal roda três guards que **falham alto** se algo regredir — **título** em toda evidência (`enrich_evidence
--check`, R-CLM-16), **idioma** correto em todo campo PT/EN (`lang_check`, R-SITE-16), e a **busca de
contradição** rotativa (R-AI-12). São o que torna a compilação não supervisionada confiável (pré-requisito do
trilho server-side da Fase 2 — ver `decentralization.md`).

---

## 5 · Porta de contribuição (R-CONTRIB · `submit.py`)

Como um terceiro alimenta o registro **sem o fundador no caminho** e **sem risco às seeds**. Invariante de
segurança: o intake **nunca escreve no registro publicado** — só na fila; o conteúdo entra **apenas** pelo
compilador neutro (o loop do diagrama 2).

```mermaid
flowchart TD
    EXT(["Contribuidor externo<br/>atribuído por ORCID · R-CONTRIB-3"]) --> KIND{"submit.py"}
    KIND -->|"question"| JUDGE{"portão de identidade<br/>judge_same · R-Q-5/R-ALLOC-4<br/>(identidade, NÃO verdade)"}
    JUDGE -->|"same"| LINKQ["liga à pergunta existente"]
    JUDGE -->|"novel"| TEMP["cunha TEMP<br/>SQ-&lt;DOM&gt;-D######"]
    KIND -->|"suggest (DOI/PMID)"| VRES{"verify · DOI resolve?<br/>R-AI-4"}
    VRES -->|não| REJ["recusa (não verificável)"]
    VRES -->|sim| Q

    LINKQ --> Q[("FILA · submissions.json<br/>NUNCA escreve no registro<br/>R-CONTRIB-2")]
    TEMP --> Q

    Q --> PROC{"submit.py process<br/>BYO-compute · R-CONTRIB-4"}
    PROC -->|"pergunta"| PROMO["promove TEMP → SQ final"]
    PROC -->|"sugestão"| LOOP(["entrega o DOI ao LOOP NEUTRO<br/>(diagrama 2) — classify+merge+recompile<br/>evidence-bounded + busca de contradição"])
    PROMO --> LOOP
    LOOP --> REG[("Registro · seeds + scr.db")]

    style Q fill:#5c4a1a,color:#fff
    style LOOP fill:#13315c,color:#fff
    style REG fill:#0f1b2d,color:#fff
```

> **Por que é seguro abrir:** a superfície é estreita — um contribuidor só **sugere artigo** ou **propõe
> pergunta**, nunca escreve claim/resposta. Pior caso de abuso = *compute desperdiçado*, não corrupção (modelo
> *pull-request*). Na Fase 3 (server-side) some-se a isto uma **fila isolada + aprovação humana** antes do build
> (anti prompt-injection/spam) — ver `decentralization.md`.
