# Estrutura do projeto OSF

> Como organizar o projeto no OSF (osf.io). Componentes (subprojetos) + arquivos.
> Mapeia os documentos de `docs/` para o registro público. **SCR à frente.**

## Nome do projeto OSF

**Scientific Claim Registry (SCR)**
*Subtítulo:* A public, versioned, expert-curated registry of biomedical scientific claims — operated by the BIO method.

## Componentes e arquivos a subir

```
📁 Scientific Claim Registry (SCR)            ← projeto raiz (descrição = osf/00_README-OSF.md)
│
├── 📁 01_Foundations
│     ├── Editorial — Why Scientific Claims Deserve Persistent Identifiers   (docs/04_editorial-SCR-draft → PDF)
│     ├── SCR/BIO Framework v0.2                                             (docs/BIO_v0.2_Framework → PDF)
│     ├── Manifesto v0.1                                                     (docs/BIO_v0.1_Manifesto → PDF)
│     ├── Manifesto completo (PT)                                           (docs/BIO_manifesto_completo_PT → PDF)
│     └── Timeline.md                                                        (criar: marcos datados)
│
├── 📁 02_Prior_Art
│     └── Prior-Art Review                                                   (docs/02_prior-art-review → PDF)
│
├── 📁 03_Specification
│     ├── Claim Schema (data model)                                          (docs/spec/claim-schema → PDF)
│     ├── Governance Model                                                   (docs/spec/governance-model → PDF)
│     └── Glossary                                                           (docs/glossary → PDF)
│
├── 📁 04_Lipedema_Pilot
│     ├── Pilot Protocol            (a criar)
│     ├── Initial_Claims.xlsx/json  (a criar — registro-piloto)
│     └── Expert_Panel.md           (a criar)
│
├── 📁 05_Feedback
│     ├── AI Council — Review Prompt                                         (docs/AI_Council_Prompt → PDF)
│     └── AI Council — Critical Review                                       (docs/AI_Council_Review → PDF)
│
└── 📁 06_Future_Implementations
      └── Roadmap (Lymphedema, EDS, MCAS, …)                                 (docs/roadmap → PDF)
```

## O que sobe AGORA (mínimo viável de registro)

Não subir tudo. Para plantar a bandeira hoje, basta:
- Descrição do projeto (`00_README-OSF.md`)
- **01_Foundations:** Editorial + Framework v0.2
- **02_Prior_Art:** Prior-Art Review
- **05_Feedback:** AI Council Review

O resto cresce organicamente. (Conselho da conversa de origem: "levaria menos de uma hora".)

## Documento que recebe o DOI (Zenodo)

O **Framework v0.2** é o registro-âncora do DOI (ver `osf/02_ZENODO-metadata.md`).
Opcionalmente, o **Editorial** recebe um segundo DOI próprio.
