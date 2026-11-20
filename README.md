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
- **Resposta versionada** registra a síntese e seu fundamento em uma data de corte. O protocolo prevê um snapshot imutável e citável por versão.
- **Camadas:** L1 Registry (automatizável, o produto) · L2 Consensus (opcional) · L3 Recomendação (opcional).
- **Knowledge Freshness:** indica a recência das fontes associadas à pergunta.
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

## Estado do piloto (2026-11-20)

- **42 perguntas, 216 proposições ativas e 841 achados** no registro de trabalho. Os 514 claims substituídos ou retirados continuam preservados sob seus IDs. O depósito v0.6 abaixo é um recorte anterior.
- Site bilíngue (EN na raiz e PT em `/pt/`), com páginas e JSON de perguntas e claims, síntese por desfecho e histórico da resposta.
- A vigilância automatizada (`registry/loop.py`) ainda usa o fluxo anterior à consolidação. O fluxo de incorporação por achado (`registry/attach_findings.py`) já existe e a recompilação ocorre em etapa separada.

A próxima entrega vai demonstrar como citar uma versão da resposta, identificar o achado que a modificou e conferir sua origem. O [roadmap](docs/roadmap.md) descreve o piloto de três perguntas e os critérios para validar a publicação.

## Prioridade intelectual e DOIs (Zenodo, CC BY 4.0)

- **SCR Protocol v1:** 10.5281/zenodo.20517114
- **Concept DOI** (sempre a última versão): 10.5281/zenodo.20466195
- **v0.6 (ATUAL)** (claims viram proposições gerais com o achado de cada estudo, R-CLM-19: 42 perguntas, 215 claims ativos, 837 achados; os 514 antigos mantidos como superseded/retired): 10.5281/zenodo.24396402
- **v0.5.2** (substituída pela v0.6) (correção da v0.5.1: retira o último resíduo de autoria banida, no `first_mention` da SQ-LIP-000004; mesmos 514 claims): 10.5281/zenodo.24325901
- **v0.5.1** (substituída pela v0.5.2) (correção da v0.5: curadoria por autoria `author_ban`, risco de viés por leitura do texto integral R-CLM-18; 42 perguntas/514 claims): 10.5281/zenodo.24325390
- **v0.5** (substituída pela v0.5.1 no mesmo dia; não usar) (vigilância da Layer 1 sem supervisão, em escala de biblioteca; 42 perguntas/526 claims, 614/626 verificadas; modos de falha documentados): 10.5281/zenodo.24324283
- **v0.4** (verificação adversarial por dois modelos + proveniência ao nível da frase; piloto auditado: 42 perguntas/347 claims, 416/423 verificadas): 10.5281/zenodo.20665788
- **v0.3** (framework + dataset do piloto): 10.5281/zenodo.20476673 · **v0.2:** 10.5281/zenodo.20466196
- **OSF:** https://osf.io/n97ez/ · Pacote de registro em `osf/`.

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `docs/` | Pensamento estratégico, material fundador e **`spec/`** (RULES.md = rulebook canônico · PROTOCOL.md) |
| `registry/` | JSON versionados (`questions.json`, `claims.json`) + projeção SQLite `scr.db` + `schema.sql` + `db.py` + loop + `submit.py` |
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
