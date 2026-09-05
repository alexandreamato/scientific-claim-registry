#!/usr/bin/env python3
"""One-time (idempotent) seed of Brazilian-Portuguese translations for the 18 questions.
Adds text_pt / current_answer_pt / major_uncertainty_pt to questions.json, in a clean key
order, only where missing. Future questions are auto-translated by translate.py (OpenAI).
Run from registry/: python3 seed_pt_questions.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")

PT = {
 "SQ-LIP-000001": ("O lipedema é uma doença distinta, separada da obesidade e do linfedema?",
  "Com base nas evidências atualmente indexadas e no consenso de especialistas, o lipedema é tratado como uma entidade clínica distinta, caracterizada por acúmulo de gordura desproporcional, simétrico e que poupa os pés, resistente à perda de peso convencional. Não é o mesmo que obesidade ou linfedema, embora os três possam coexistir. Não existe um teste diagnóstico padrão-ouro objetivo; a distinção apoia-se em critérios clínicos e no consenso de especialistas.",
  "Não há biomarcador validado; o limite com a obesidade é definido clinicamente, não biologicamente."),
 "SQ-LIP-000002": ("Qual a frequência do lipedema e quem ele afeta?",
  "Estimativas baseadas em rastreamento sugerem que o lipedema pode afetar cerca de 12% das mulheres adultas em um estudo brasileiro, mas isso se baseia em questionários autorrelatados e não em confirmação clínica, provavelmente superestimando a doença diagnosticada clinicamente. Afeta predominantemente mulheres; a ocorrência em homens é rara, porém documentada.",
  "As cifras de prevalência vêm de rastreamento por questionário com viés de seleção; a verdadeira prevalência confirmada clinicamente é desconhecida."),
 "SQ-LIP-000003": ("A ultrassonografia pode diagnosticar ou classificar o lipedema?",
  "Vários estudos unicêntricos propõem pontos de corte de espessura à ultrassonografia e padrões qualitativos que distinguem o tecido do lipedema de controles, e estes foram reutilizados como referência por trabalhos posteriores. O diagnóstico permanece primariamente clínico; a ultrassonografia é auxiliar, ainda não um teste diagnóstico isolado validado.",
  "Os pontos de corte e classificações vêm de coortes brasileiras unicêntricas, sem validação prospectiva multicêntrica de sensibilidade/especificidade."),
 "SQ-LIP-000004": ("O lipedema é subdiagnosticado, e ferramentas de rastreamento podem ajudar a identificá-lo?",
  "Como a obesidade é comumente definida apenas pelo IMC (que ignora a distribuição da gordura), o lipedema é frequentemente perdido quando a investigação para no diagnóstico de obesidade. Questionários de rastreamento autoaplicáveis alcançam alta acurácia de classificação em coortes de desenvolvimento e podem aumentar a suspeição clínica, mas não são diagnósticos por si sós.",
  "As ferramentas de rastreamento foram validadas em pequenas amostras de clínicas especializadas apenas contra o diagnóstico clínico, não contra imagem ou na atenção primária."),
 "SQ-LIP-000005": ("O lipedema aumenta a prevalência de hipermobilidade articular?",
  "Provavelmente, mas a evidência é majoritariamente observacional. Uma coorte transversal relatou hipermobilidade articular em cerca de 44% das pacientes adultas com lipedema. Nenhuma evidência randomizada ou longitudinal estabelece um vínculo causal, e os critérios diagnósticos tanto para o lipedema quanto para a hipermobilidade são heterogêneos entre os estudos.",
  "Os pontos de corte de hipermobilidade e as definições de lipedema variam entre estudos; desenho transversal único."),
 "SQ-LIP-000006": ("O lipedema está associado ao TDAH?",
  "Um único estudo transversal relatou maior prevalência de rastreamento positivo para TDAH (autorrelato) entre mulheres com rastreamento positivo para lipedema (76,9% vs 54%), com correlação positiva entre os escores de sintomas. A associação baseia-se em rastreamento autorrelatado em amostra de conveniência e não foi replicada.",
  "Rastreamento autorrelatado, sem ajuste para fatores de confusão, estudo único não replicado."),
 "SQ-LIP-000007": ("O lipedema está associado a doença da tireoide?",
  "Uma coorte transversal relatou distúrbios tireoidianos com mais frequência no lipedema do que em pacientes com linfedema (24,4% vs 14,9%). A evidência limita-se a uma única coorte sem ajuste, e a condição tireoidiana não é especificada como autoimune.",
  "Coorte única, sem ajuste para idade/IMC, distúrbio tireoidiano não caracterizado."),
 "SQ-LIP-000008": ("O lipedema está associado à fibromialgia e a outras condições de dor crônica?",
  "Estudos observacionais relatam coocorrência frequente: o lipedema foi encontrado em cerca de metade das mulheres que preenchiam critérios de fibromialgia em um estudo, e dor no joelho é comumente relatada por mulheres com rastreamento positivo para lipedema. A direção da relação é incerta e a maioria dos dados é autorrelatada ou unicêntrica.",
  "Sem controles sem a comorbidade; direcionalidade incerta; sintomas autorrelatados."),
 "SQ-LIP-000009": ("O lipedema está ligado à sensibilidade ao glúten, à doença celíaca ou ao HLA-DQ2/DQ8?",
  "Uma coorte clínica relatou maior prevalência dos haplótipos HLA-DQ2/DQ8 associados à doença celíaca no lipedema, e análises populacionais (NHANES) encontraram menor gordura ginoide em mulheres celíacas e um padrão incomum de IgG alimentar. São análises transversais isoladas, com pequeno número de casos e sem mecanismo causal demonstrado.",
  "Sem controles concomitantes, poucos casos de celíaca, causa reversa não excluída; mecanismo não comprovado."),
 "SQ-LIP-000010": ("Uma distribuição de gordura semelhante à do lipedema (periférica/ginoide) protege contra câncer ou doença metabólica?",
  "Análises transversais do NHANES encontraram que uma maior razão de gordura perna-tronco associou-se a menor prevalência de câncer e a um perfil imunometabólico mais favorável. Por serem dados de prevalência (não de incidência), a causa reversa (a doença reduzindo a gordura periférica) não pode ser excluída; a associação protetora é sugestiva, não estabelecida.",
  "Prevalência transversal, desfechos autorrelatados, possível causa reversa e viés de sobrevivência."),
 "SQ-LIP-000011": ("O que se sabe sobre o mecanismo de inflamação e dor no tecido do lipedema?",
  "Estudos teciduais relatam histamina elevada e uma assinatura predominante de macrófagos M2 na gordura gluteofemoral acometida, e o teste sensitivo quantitativo mostra um padrão de dor distintivo no membro. São observações independentes de estudos pequenos; descrevem correlatos da doença, não um mecanismo causal comprovado.",
  "Estudos teciduais pequenos e majoritariamente não replicados; correlacionais, mecanismo não estabelecido."),
 "SQ-LIP-000012": ("Hormônios e hereditariedade influenciam o surgimento do lipedema?",
  "O lipedema é amplamente descrito como multifatorial, com início e agravamento ligados às transições hormonais femininas e a uma predisposição hereditária. Um estudo observacional relatou piora dos sintomas na maioria das usuárias de contraceptivos hormonais. Genes e mediadores hormonais específicos são hipotetizados, não demonstrados.",
  "Os vínculos hormonais/genéticos apoiam-se em autorrelato e consenso; mecanismos específicos não comprovados."),
 "SQ-LIP-000013": ("A lipoaspiração é eficaz e segura para o lipedema?",
  "Uma metanálise de séries antes-depois relata reduções significativas em dor, edema, hematomas e prejuízo da qualidade de vida após a lipoaspiração, e uma coorte unicêntrica relata baixa taxa de complicações maiores. Contudo, não há ensaios clínicos randomizados, cerca de metade das pacientes ainda necessita de terapia conservadora depois, e o seroma é uma complicação menor relativamente frequente.",
  "Sem comparação randomizada/controlada; os dados agrupados são séries antes-depois não controladas, com alta heterogeneidade."),
 "SQ-LIP-000014": ("Uma dieta cetogênica ou de baixo carboidrato ajuda no lipedema?",
  "Uma metanálise relata que uma dieta de baixo carboidrato/cetogênica reduz significativamente o peso corporal, o IMC e as circunferências dos membros, com redução menor na dor. Os estudos são poucos e curtos, em sua maioria não controlados, e não separam a perda de gordura específica do lipedema da perda de peso geral.",
  "Poucos estudos curtos, sem seguimento de longo prazo; mecanismo da dor não comprovado."),
 "SQ-LIP-000015": ("Qual é o manejo global recomendado do lipedema?",
  "O consenso de especialistas e a evidência de casos favorecem um cuidado individualizado e multidisciplinar: manejo conservador (estilo de vida, dieta, compressão, exercício de baixo impacto) como primeira linha, com a cirurgia considerada apenas após cerca de um ano de tratamento clínico e priorizando mobilidade e alívio de sintomas em vez da estética. O impacto na saúde mental e o atraso diagnóstico são reconhecidos como importantes.",
  "A sequência de manejo é baseada em consenso, não derivada de comparações controladas de estratégias."),
 "SQ-LIP-000016": ("A gestrinona é um tratamento eficaz para o lipedema?",
  "Não. Uma revisão sistemática não encontrou ensaios clínicos, estudos observacionais ou relatos de caso avaliando a gestrinona para o lipedema, e não há evidência científica que apoie seu uso off-label, particularmente como implantes subcutâneos. Isso reflete ausência de estudos, não uma falta de efeito demonstrada.",
  "Ausência de evidência, e não evidência de ausência; a segurança da via de implante não foi estudada."),
 "SQ-LIP-000017": ("O lipedema progride para linfedema e causa incapacidade funcional?",
  "O consenso de especialistas sustenta que o lipedema avançado pode desenvolver linfedema secundário (lipolinfedema) por sobrecarga linfática crônica, e que o aumento da adiposidade do membro pode prejudicar a mobilidade e as atividades diárias. São afirmações de nível de consenso, e não achados de estudos longitudinais de imagem.",
  "A disfunção linfática no lipedema inicial é debatida; a progressão é descrita por consenso, não por dados longitudinais."),
 "SQ-LIP-000018": ("Como o lipedema se relaciona com varizes e doença venosa?",
  "O lipedema e as varizes coexistem com frequência, de modo que a ultrassonografia venosa realizada para varizes é uma oportunidade de rastrear o lipedema. As frequências de coexistência vêm em parte de literatura externa e de uma única amostra de clínica vascular, que superestima a sobreposição.",
  "Viés de seleção pelo recrutamento em clínica vascular; coexistência é associação, não causa."),
}

ORDER = ["id", "text", "text_pt", "knowledge_state",
         "current_answer", "current_answer_pt",
         "major_uncertainty", "major_uncertainty_pt", "claims"]

data = json.load(open(QF))
added = 0
for q in data["questions"]:
    tr = PT.get(q["id"])
    if tr and not q.get("text_pt"):
        q["text_pt"], q["current_answer_pt"], q["major_uncertainty_pt"] = tr
        added += 1
    # reorder keys for readability (keep any extras at the end)
    extras = {k: v for k, v in q.items() if k not in ORDER}
    new = {k: q[k] for k in ORDER if k in q}
    new.update(extras)
    q.clear(); q.update(new)

json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
print(f"questions.json: PT seeded for {added} question(s); {sum(1 for q in data['questions'] if q.get('text_pt'))}/{len(data['questions'])} now bilingual.")
