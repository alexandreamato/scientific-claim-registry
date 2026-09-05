# Scientific Claim Registry (SCR) — One-Pager

> **PubMed stores scientific papers. ScientificClaims.org stores the evolving answers to
> scientific questions.** O *sistema operacional da memória científica* — não da verdade,
> não do consenso, da **memória**. Ele **registra, não arbitra**.

## O problema
Achar artigos já está resolvido (PubMed). A dor real é outra: **o conhecimento envelhece e
ninguém sabe quando.** Um pesquisador gasta dias para saber o *estado atual* de uma pergunta,
não sabe *qual* é a lacuna, e não consegue dizer *quando* a área mudou. Guidelines de 2022
ignoram 15 artigos novos de 2026. Não há identidade nem histórico para a *resposta* de uma pergunta.

## A proposta
O **SCR** organiza o conhecimento em torno de **perguntas científicas** (`SQ-LIP-0001`), cada
uma com uma **página de evidência versionada**:
- **Resposta atual** (cautelosa, *evidence-bounded* — a IA não opina)
- **Estado do conhecimento** (Speculative → Foundational) e **o que mudou** desde a última versão
- **Claims** que *sustentam / contradizem / refinam* a pergunta (evidência estruturada, com GRADE)
- **Knowledge Freshness** — quão recente é a base de evidência (mede *Evidence Decay*)
- **Histórico de versões** e **referências** · saída **legível por máquina** (JSON)

## Por que agora / para quem
- **Cientistas:** estado atual, lacunas e *quando mudou* — em segundos, não em dias.
- **LLMs (o ouro):** modelos não têm memória científica estruturada. Em vez de `PubMed → IA →
  Usuário`, vira `PubMed → **SCR** → IA → Usuário`. O SCR é **infraestrutura para IA**, não competidor.
- **Sociedades médicas:** consultam para saber quando atualizar guidelines.
> Não é preciso convencer bilhões de pessoas — só os **sistemas que respondem perguntas**.
> Se eles dependerem do SCR, ele vira infraestrutura. Infraestrutura sobrevive décadas.

## Arquitetura em camadas (só a 1ª precisa existir)
- **L1 Registry** — automatizável: registra perguntas+claims, acumula evidência, versiona. *O produto.*
- **L2 Consensus** *(opcional)* — especialistas endossam/discordam.
- **L3 Recommendation** *(opcional)* — sociedades → conduta clínica.

## Honestidade (prior art)
O SCR **não inventa** "claims" nem a identidade persistente (nanopublications já existem;
ClaimRxiv propôs a tese; SciFact é o campo de verificação; Epistemonikos/PICO organiza evidência
por pergunta). A contribuição é **adoção + organização por domínio + acumulação versionada +
Knowledge Freshness + machine-first**, construída sobre o que existe.

## O piloto
**Lipedema** — 50 claims sob 18 perguntas, no ar em **scientificclaims.org**. Disease-agnostic por design.

---
**Fundador:** Dr. Alexandre Campos Moraes Amato — Amato Duo / Associação Brasileira de Lipedema
· ORCID 0000-0003-4008-4029 · CC BY 4.0 · DOI 10.5281/zenodo.20466195
