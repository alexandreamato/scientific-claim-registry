# SCR — Modelo de Governança (v0.1)

> ⚠️ **Reposicionado (ver `docs/09_arquitetura-em-camadas.md`):** após o pivô "registra, não
> arbitra", a governança deixa de ser o núcleo. Ela descreve a **Layer 2 (Consenso) — opcional**.
> A **Layer 1 (Registro)** é automatizada e precisa só de regras mínimas (o que entra como claim;
> como se liga evidência Supports/Contradicts/Refines), **não** de conselho científico. O conteúdo
> abaixo aplica-se a quem optar por operar a camada de consenso por cima do registro.

## 1. Por que governança primeiro

A revisão de prior art mostrou que sistemas de claims morrem por problemas **sociais e
de sustentabilidade**, não técnicos: disputa entre especialistas, conflito de interesse,
falta de incentivo e perda de financiamento. Definir as regras antes evita reescrever a
"constituição" sob pressão depois.

## 2. Papéis e elegibilidade

| Papel | Quem | Pode |
|---|---|---|
| **Público** | qualquer pessoa | Ver tudo (acesso aberto por princípio) |
| **Colaborador** | cadastrado + ORCID | Sugerir claims/evidências (pull request) |
| **Curador / Revisor** | especialista verificado na área | Avaliar, aprovar e versionar claims da sua área |
| **Editor** | curador sênior designado | Resolver conflitos, aprovar versões, mediar disputas |
| **Conselho Científico** | painel multidisciplinar | Define regras, audita, resolve disputas escaladas |
| **Founding Director** | **Dr. Alexandre Amato** | Direção fundacional, guarda da metodologia, presidência (ver §6) |

**Verificação de especialista:** ORCID + evidência de expertise na subárea (publicações,
titulação, prática clínica). Registro público de quem é curador de quê.

## 3. Regras de curadoria (espelham o modelo CIViC, que funciona)

- Uma claim só muda de versão com **≥2 curadores independentes**, sendo **≥1 Editor**.
- **Curador não aprova a própria submissão.**
- Toda mudança gera registro imutável no `history` (autor, data, justificativa, evidência add/removida).
- Discordância → registrada como **Conflito Ativo** na claim, não escondida.

## 4. Conflito de interesse (COI)

- Declaração obrigatória de COI para **todo** colaborador/curador.
- Scores calculados **com e sem** especialistas com COI declarado (transparência dupla).
- COI relevante por claim fica visível no campo `coi`.
- Patrocínio (indústria, fundações) é permitido para *sustentar a infraestrutura*, nunca
  para influenciar curadoria — separação explícita e auditável.

## 5. Resolução de disputas e apelação

1. **Nível 1:** curadores tentam consenso; persistindo, marca-se Conflito Ativo.
2. **Nível 2:** um Editor media; pode solicitar evidência adicional ou parecer externo.
3. **Nível 3:** escalada ao Conselho Científico (decisão documentada e pública).
4. **Apelação:** colaborador pode apelar de uma decisão ao Conselho; o resultado é registrado.

> Princípio: o sistema **mapeia** o desacordo (quem discorda e por quê) em vez de forçar
> uma "verdade" única. Consenso ≠ verdade.

## 6. Modelo founder-steward (BDFL com transição)

- O **Founding Director** detém, na fase inicial, **veto metodológico** (garante coerência
  da "constituição" do registro). É o modelo *benevolent dictator* com **transição planejada**:
  o veto se dilui conforme o Conselho amadurece.
- A **carta fundacional** nomeia o Founding Director, descreve a sucessão e fixa os
  princípios imutáveis (acesso aberto, consenso≠verdade, governança>automação, humano decide).
- **Autoria perpétua:** o registro sempre cita os documentos fundadores (prioridade do Amato).
- Legitimidade da centralidade: origem intelectual + ativo do lipedema (ABL/Amato Duo)
  + papel de convener. Ver `docs/05_estrategia-macro.md`.

## 7. Incentivos e crédito (o problema que mata projetos assim)

- Toda contribuição é **citável** (claim com ID + curador com ORCID) → crédito acadêmico rastreável.
- Meta de longo prazo: **Knowledge Contribution Score (KCS)** reconhecido como métrica
  complementar ao H-index (curadoria de qualidade conta).
- Buscar reconhecimento institucional (sociedades, agências) da curadoria como produção científica.

## 8. IA na governança

- IA **assiste**: vigilância da literatura, detecção de candidatos a claim, deduplicação,
  ligação semântica. **Não aprova nem altera claims.**
- Expansão do papel da IA depende de **validação empírica publicada** (sensibilidade/
  especificidade) — nunca por antecipação de capacidade.

## 9. Licenciamento (Postura B — Commons protegido)

Documentos **CC BY 4.0**; dados do registro **CC BY-SA 4.0** (ou ODbL); software futuro
**AGPL-3.0 + licença comercial dupla**; **marca registrada** (SCR/BIO) detida pela
Fundação; contribuições sob **CLA**. Abrir o conhecimento, ser dono do nome e do leme,
monetizar por serviços/licença dupla/autoridade — sem fechar o commons. Detalhes em
`docs/07_licenciamento.md`.

## 10. Transparência radical (não-negociável)

Todo histórico, toda proveniência, todo voto — visíveis e auditáveis. Reversões
documentadas. Scores com e sem COI. Acesso aberto por padrão.
