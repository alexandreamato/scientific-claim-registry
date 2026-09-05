# SCR — Scientific Claim Registry

> **"PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to
> scientific questions."** O *sistema operacional da memória científica* — não da verdade,
> não do consenso, da **memória**. Ele **registra, não arbitra**.

**No ar:** https://scientificclaims.org · **Piloto:** lipedema (disease-agnostic por design)
**Fundador:** Dr. Alexandre Campos Moraes Amato (Amato Duo / ABL · ORCID 0000-0003-4008-4029)

## Modelo

- **Pergunta científica** (`SQ-LIP-000001`) = objeto central navegável (estável, neutra).
- **Claim** (`SCR-LIP-000001`) = evidência estruturada e versionada que é *consistent / conflicting /
  refining / contextual* em relação à pergunta. É um **grafo** (um claim ↔ várias perguntas).
- **Resposta = renderização versionada**, não verdade armazenada. Cada versão tem snapshot imutável e citável.
- **Camadas:** L1 Registry (automatizável, o produto) · L2 Consensus (opcional) · L3 Recomendação (opcional).
- **Knowledge Freshness:** mede o envelhecimento da evidência por pergunta (*Evidence Decay*).
- **Machine-first:** cada pergunta e claim expõe JSON (`/q/<id>.json`, `/c/<id>.json`) para LLMs/agentes.

## O protocolo (a "constituição")

O SCR é, antes de tudo, um **protocolo aberto**: um núcleo rígido mínimo (modelo de objeto, identificadores,
contrato de claim, versionamento, freshness, machine-first, neutralidade) cercado de uma **periferia aberta**
(qual domínio, qual IA, qual fonte, quem paga o compute). Qualquer pessoa/grupo pode adotá-lo em qualquer área.

- **SCR Protocol v1** (spec autônoma, disease-agnostic, citável): `docs/spec/PROTOCOL.md` ·
  **DOI 10.5281/zenodo.20517114** · https://zenodo.org/record/20517114
- **Porta de contribuição** (protótipo): `registry/submit.py` — criação aberta de perguntas (portão de
  identidade) e **sugestão de artigos** (DOI/PMID "a considerar"), atribuída por ORCID. Nunca escreve no
  registro: o conteúdo entra só pelo compilador neutro (*pull-request model*; BYO-compute).

## Estado atual (2026-06-02)

- **345 claims sob 42 perguntas** (`SQ-LIP-…`), site **bilíngue** (EN raiz + PT `/pt/`), cada claim com página
  própria e JSON, back-links às perguntas, Knowledge Freshness, busca/paginação client-side.
- **Loop de vigilância da Layer 1 — FECHADO** (`registry/loop.py` + `ingest.py`): retrieval semântico →
  classify (LLM) → verify → corrobora/promove (merge conservador) → **busca de contradição sempre** →
  recompila → versiona. Higiene: 0 órfãos · 0 evidências sem grade · 100% PECO · título em toda evidência.
- **Página da pergunta:** *Bottom line* (10 s) → *Resumo executivo* → tabela **por desfecho** (sintoma ≠
  modificação de doença) → síntese → claims; dois gráficos temporais (*Evidence over time* e *Answer over time*).

## Prioridade intelectual e DOIs (Zenodo, CC BY 4.0)

- **SCR Protocol v1:** 10.5281/zenodo.20517114
- **Concept DOI** (sempre a última versão): 10.5281/zenodo.20466195
- **v0.4 (ATUAL)** (verificação adversarial por dois modelos + proveniência ao nível da frase; piloto auditado: 42 perguntas/347 claims, 416/423 verificadas): 10.5281/zenodo.20665788
- **v0.3** (framework + dataset do piloto): 10.5281/zenodo.20476673 · **v0.2:** 10.5281/zenodo.20466196
- **OSF:** https://osf.io/n97ez/ · Pacote de registro em `osf/`.

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `docs/` | Pensamento estratégico, material fundador e **`spec/`** (RULES.md = rulebook canônico · PROTOCOL.md) |
| `registry/` | **Banco canônico** `scr.db` + seeds (`questions.json`, `claims.json`) + `schema.sql` + `db.py` + loop + `submit.py` |
| `site/` | O site estático no ar (gerado por `build_questions.py` + `build_site.py`; deploy em `site/deploy.md`) |
| `osf/` | Pacote de registro de prioridade (OSF + Zenodo + PDFs) |
| `CLAUDE.md` | Guia operacional completo (objeto, convenções, pipeline, infra, DOIs, mapa de docs) |

## Licença

Multi-componente, **Postura B (commons protegido)** — ver [`LICENSE`](LICENSE) e `docs/07_licenciamento.md`:

| Componente | Licença |
|---|---|
| **Documentos** (`docs/`, incl. a spec do protocolo) | **CC BY 4.0** |
| **Dados do registro** (perguntas e claims, JSON, `scr.db`) | **CC BY-SA 4.0** (ODbL para o banco) |
| **Software** (pipeline Python) | **AGPL-3.0-or-later** + licença comercial dupla |
| **Nome/marca** ("SCR", "Scientific Claim Registry", "BIO") | Marca reservada — as licenças acima não dão direito ao nome |

Share-alike/AGPL garantem que cópias de dados/código permaneçam **abertas e atribuídas**. Contribuições sob CLA.
O SCR **registra, não arbitra**, e **não é aconselhamento médico** — claims não substituem julgamento clínico.

## Como citar

Use o [`CITATION.cff`](CITATION.cff) (o GitHub renderiza "Cite this repository") ou:

> Amato ACM. *Scientific Claim Registry (SCR) — a versioned memory of how scientific answers evolve.*
> Amato Duo, ORCID 0000-0003-4008-4029. https://scientificclaims.org. DOI: 10.5281/zenodo.20466195.

Para citar **o protocolo**: DOI 10.5281/zenodo.20517114. Para citar **uma resposta específica**, cite a
**versão** da pergunta (cada `/q/<id>` oferece Vancouver/APA/Chicago/BibTeX prontos, capturando o estado da
evidência naquela data).

## Princípio (honestidade sobre prior art)

O SCR **não inventa** "scientific claims" nem a identidade persistente (nanopublications/Trusty URIs já
existem; ClaimRxiv propôs a tese; Epistemonikos/PICO organiza evidência por pergunta; SciFact é o campo de
verificação). A contribuição é **adoção + organização por domínio + acumulação versionada + freshness +
machine-first**, **construída sobre** o que existe — não reinventando identificadores.
