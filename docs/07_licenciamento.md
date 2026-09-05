# SCR / BIO — Estratégia de Licenciamento e Controle

> Como manter a rédea, aceitar ajuda de qualquer um, evitar que cópias/forks
> enfraqueçam o projeto, e ganhar dinheiro (mesmo que indiretamente). Rascunho v0.1.
> ⚠️ Não é aconselhamento jurídico — marca/contratos exigem advogado de PI (INPI no Brasil).

## A ideia-chave: não existe "uma licença". Existem 4 ativos diferentes.

O erro fatal é licenciar tudo igual. Cada ativo tem uma licença ótima diferente —
e é a **combinação** que dá abertura + controle + receita.

| Ativo | Licença recomendada | Por quê |
|---|---|---|
| **Documentos** (papers, editorial, framework, specs) | **CC BY 4.0** | Você *quer* que copiem e citem — citação = seu crédito e sua prioridade. Espalhar fortalece, não enfraquece. |
| **Dados do registro** (as claims) | **CC BY-SA 4.0** (ou **ODbL** p/ o banco) | *Share-alike*: qualquer um usa, mas derivados ficam **abertos e atribuídos a você**. Um fork **não pode fechar** o que pegou, e você pode reabsorver as melhorias dele. |
| **Software/plataforma** (quando existir) | **AGPL-3.0 + licença comercial dupla** | AGPL fecha a "brecha SaaS" (quem rodar como serviço tem de abrir o código). A licença dupla vende isenção a empresas → **receita**. |
| **Nome/marca** ("SCR", "Scientific Claim Registry", "BIO") | **Marca registrada** (INPI; depois USPTO/EUIPO) | **A rédea de verdade.** Abra tudo, mas seja dono do *nome*. Um fork não pode se chamar "SCR". |

E mais um instrumento, sobre as contribuições:

- **CLA (Contributor License Agreement):** quem contribui cede à Fundação o direito de
  *também* licenciar comercialmente. É o que permite aceitar ajuda de todos **e** vender
  licença comercial depois (modelo MySQL/MongoDB). Sem CLA, você não pode relicenciar o
  que outros contribuíram.

## Por que isso resolve cada uma das suas preocupações

**"Todo mundo copiando perde força."**
→ Para os *documentos*, cópia = força (mais citação, mais prioridade sua). Para os
*dados/código*, o **share-alike (SA/AGPL)** garante que cópias permaneçam abertas e
atribuídas — ninguém transforma o seu commons em produto fechado.

**"Algum fork acaba desenvolvendo mais."**
→ Três defesas: (1) **marca** — o fork não pode usar o nome confiável "SCR";
(2) **share-alike** — as melhorias do fork voltam ao commons e você as reabsorve;
(3) o **fosso real** não é o código, é a **adoção + confiança + autoridade de convener +
seu dado único de lipedema**. Ninguém "forka" a ClinicalTrials.gov porque ela *é* a
referência. Licença evita o cercamento; o fosso é ser o registro padrão.

**"Quero manter a rédea."**
→ A **marca** + a **Fundação que detém a PI** + o **CLA** + o veto metodológico do
founder-steward. Você abre o conhecimento e mantém o leme.

**"Quero ajuda de quem quiser ajudar."**
→ Licenças abertas (CC BY / CC BY-SA / AGPL) + CLA tornam a contribuição fácil e legal,
sem abrir mão do controle nem da via comercial.

**"Quero ganhar dinheiro, mesmo indiretamente."**
→ Ver abaixo. Tudo compatível com manter o núcleo aberto.

## Como ganhar dinheiro mantendo aberto (modelo "open core")

1. **Serviço gerenciado / API premium** — versão hospedada do SCR, SLAs de API para
   hospitais, indústria (farma, planos), com acesso público/acadêmico sempre gratuito.
2. **Licença comercial dupla** — empresas que não querem as obrigações do AGPL/SA pagam
   por uma licença comercial (só possível com CLA).
3. **Certificação e formação** — "SCR-Certified Curator", cursos, CME, acreditação.
4. **Consultoria/implementação** — levar o método a outras doenças e sociedades médicas.
5. **Patrocínio e fomento** — fundações e indústria patrocinam a *infraestrutura* (com
   firewall de conflito de interesse: curadoria nunca à venda; scores com e sem COI).
6. **Indireto (provavelmente o maior no curto prazo)** — autoridade de marca →
   reputação, palestras, encaminhamentos e pacientes ao Amato Duo / ABL;
   liderança intelectual que valoriza tudo o que você já faz.

## O que NÃO fazer (e por quê)

- **Não use licença permissiva pura (MIT / CC BY) para dados e código.** Um concorrente
  (ou uma big tech de IA) pega, melhora em segredo e te ultrapassa sem devolver nada.
  Share-alike/AGPL impedem isso.
- **Cuidado com "NonCommercial" (NC) como alavanca principal.** Parece proteger a receita,
  mas: bloqueia usos legítimos, é incompatível com o ecossistema aberto (Wikidata,
  Wikipedia não podem reusar), mancha a credibilidade de "infraestrutura pública" e
  **você não precisa dela** — marca + licença dupla + SA já dão controle e receita.
  (Só considerar NC se quiser ser deliberadamente mais comercial — ver postura C abaixo.)

## Três posturas possíveis (a decisão é sua)

| | **A — Infra aberta** | **B — Commons protegido (recomendada)** | **C — Comercial** |
|---|---|---|---|
| Dados | CC BY 4.0 | **CC BY-SA 4.0 / ODbL** | CC BY-NC-SA |
| Código | Apache-2.0 / AGPL | **AGPL + comercial** | Source-available (BSL) |
| Marca | registrada | **registrada** | registrada |
| Adoção/credibilidade | máxima | alta | menor |
| Controle/receita direta | menor | **equilibrado** | máxima |
| Risco "virar produto privado" | nenhum | baixo | alto |

### ✅ DECISÃO (jun/2026): Postura **B — Commons protegido**

- **Documentos:** CC BY 4.0 · **Dados:** CC BY-SA 4.0 (ou ODbL) · **Código:** AGPL-3.0 +
  licença comercial dupla · **Marca:** registrada (INPI) · **Contribuições:** sob CLA.
- Mantém a rédea (marca + CLA + Fundação), protege o commons contra cercamento e forks
  (share-alike + AGPL), permite receita (licença dupla + serviços) e preserva a
  credibilidade de "infraestrutura científica pública" — sem a qual o projeto não atrai
  curadores nem adoção.

## Coerência com o que já está registrado

- Os **documentos fundadores** (OSF/Zenodo) ficam em **CC BY 4.0** — correto na postura B
  (você quer espalhar e ser citado). Nada a mudar lá.
- A licença **de dados e de software** é decidida **quando o registro/plataforma nascer** —
  por ora, só declarar a intenção (postura B) na governança e no site.

## Próximos passos de PI (quando houver tração)

1. **Registrar a marca** "Scientific Claim Registry" / "SCR" / "BIO" no **INPI** (Brasil);
   depois internacional (Madrid Protocol / USPTO / EUIPO).
2. Constituir a **Fundação/associação** que detém marca + PI (ver `05_estrategia-macro.md`).
3. Adotar um **CLA** padrão (ex.: Apache iCLA adaptado) para contribuições.
4. Publicar uma página **/license** e **/governance** declarando o modelo (transparência).
5. Consultar **advogado de PI** antes de registrar marca e assinar CLAs.

> Resumo de uma frase: **abra o conhecimento (CC BY nos papers, share-alike nos dados,
> AGPL no código), seja dono do nome (marca) e do leme (Fundação + CLA), e monetize por
> serviços, licença dupla e autoridade — não fechando o commons.**
