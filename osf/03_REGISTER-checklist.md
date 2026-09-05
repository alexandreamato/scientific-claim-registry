# Checklist de registro (OSF + Zenodo + DOI)

> Passo a passo para o Dr. Amato executar. Eu (Claude) preparo os arquivos/PDFs;
> os passos que exigem login você faz. Tempo estimado: ~1 hora.

## Pré-requisitos (uma vez)

- [ ] Conta no **OSF** (osf.io) — pode logar com ORCID.
- [ ] Conta no **Zenodo** (zenodo.org) — pode logar com ORCID/GitHub.
- [ ] **ORCID** em mãos (preencher nos metadados — ancora autoria e prioridade).
- [ ] PDFs dos documentos fundadores gerados (peça ao Claude: "gere os PDFs").

## Parte A — OSF (o lar público e datado)

1. [ ] Criar projeto novo: **"Scientific Claim Registry (SCR)"**.
2. [ ] Colar a descrição de `osf/00_README-OSF.md` no campo *Description*.
3. [ ] Adicionar **Tags** (lista de keywords em `osf/02_ZENODO-metadata.md`).
4. [ ] Criar os componentes/pastas conforme `osf/01_STRUCTURE.md` (mínimo: 01_Foundations,
       02_Prior_Art, 05_Feedback).
5. [ ] Subir os PDFs do "mínimo viável": Editorial, Framework v0.2, Prior-Art Review, AI Council Review.
6. [ ] Definir o projeto como **Public**.
7. [ ] (Opcional) Adicionar coautores/colaboradores.

## Parte B — Zenodo (o DOI / prioridade)

**Caminho recomendado — integração OSF→Zenodo:**
1. [ ] No OSF: *Add-ons* → conectar **Zenodo**.
2. [ ] Criar um *Zenodo registration* do componente **01_Foundations** (ou do Framework v0.2).
3. [ ] Preencher os metadados de `osf/02_ZENODO-metadata.md` (Title, Authors+ORCID,
       License CC BY 4.0, Description, Keywords).
4. [ ] **Publicar** → o Zenodo emite o **DOI**. Anotar o DOI.

**Caminho alternativo — depósito direto no Zenodo:**
1. [ ] zenodo.org → *New upload* → subir o PDF do Framework v0.2.
2. [ ] Preencher os mesmos metadados → *Publish* → DOI.

## Parte C — Pós-registro

- [ ] Anotar o(s) DOI(s) em `README.md` (seção "Prioridade intelectual").
- [ ] Atualizar o "Related identifiers" no Zenodo com a URL do OSF.
- [ ] Citar o DOI em apresentações e no rodapé do site/landing.
- [ ] Frase de prioridade para uso futuro:
      *"Amato ACM. Scientific Claim Registry (SCR): A Framework for Persistent,
      Versioned, Expert-Curated Biomedical Claims. v0.2; 2026. DOI: ⟨…⟩."*

## Sugestão de execução interativa

Para logins, digite no prompt do Claude Code com prefixo `!` para rodar na sessão
(ex.: abrir as URLs). Mas a criação do projeto/depósito é feita por você no navegador —
o Claude não tem suas credenciais do OSF/Zenodo.
