#!/usr/bin/env python3
"""Add category tags + searchable keywords to every question (idempotent: only fills if absent).
Tags are canonical English keys (PT labels rendered at build time); keywords are bilingual to
power the static client-side search. Run from registry/: python3 add_tags.py
"""
import json, os
QF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")

TAGS = {
 "SQ-LIP-000001": (["Definition", "Diagnosis"],
   ["lipedema", "obesity", "lymphedema", "distinct disease", "differential diagnosis", "obesidade", "linfedema", "entidade clínica", "diagnóstico diferencial"]),
 "SQ-LIP-000002": (["Epidemiology"],
   ["prevalence", "epidemiology", "women", "how common", "prevalência", "epidemiologia", "mulheres", "frequência"]),
 "SQ-LIP-000003": (["Diagnosis", "Imaging"],
   ["ultrasound", "ultrasonography", "imaging", "subcutaneous thickness", "ultrassom", "ultrassonografia", "imagem", "espessura subcutânea"]),
 "SQ-LIP-000004": (["Diagnosis", "Screening"],
   ["screening", "underdiagnosed", "questionnaire", "BMI", "rastreamento", "subdiagnóstico", "questionário", "IMC"]),
 "SQ-LIP-000005": (["Comorbidities"],
   ["joint hypermobility", "hypermobility", "Ehlers-Danlos", "joints", "hipermobilidade articular", "frouxidão", "articulações"]),
 "SQ-LIP-000006": (["Comorbidities", "Mental health"],
   ["ADHD", "attention deficit", "neurodevelopment", "TDAH", "déficit de atenção", "neurodesenvolvimento"]),
 "SQ-LIP-000007": (["Comorbidities"],
   ["thyroid", "hypothyroidism", "autoimmune", "tireoide", "hipotireoidismo", "autoimune"]),
 "SQ-LIP-000008": (["Comorbidities", "Pain"],
   ["fibromyalgia", "chronic pain", "knee pain", "fibromialgia", "dor crônica", "dor no joelho"]),
 "SQ-LIP-000009": (["Comorbidities", "Genetics"],
   ["gluten", "celiac disease", "HLA-DQ2", "HLA-DQ8", "food IgG", "glúten", "doença celíaca", "IgG alimentar"]),
 "SQ-LIP-000010": (["Pathophysiology", "Metabolism"],
   ["gynoid fat", "peripheral fat", "cancer", "metabolic", "leg-to-trunk ratio", "NHANES", "gordura ginoide", "câncer", "metabólico"]),
 "SQ-LIP-000011": (["Pathophysiology", "Pain"],
   ["inflammation", "histamine", "macrophage", "M2", "pain mechanism", "inflamação", "histamina", "macrófagos", "mecanismo da dor"]),
 "SQ-LIP-000012": (["Etiology", "Genetics", "Hormones"],
   ["hormones", "heredity", "genetics", "contraceptives", "estrogen", "hormônios", "hereditariedade", "genética", "anticoncepcional", "estrogênio"]),
 "SQ-LIP-000013": (["Treatment", "Surgery"],
   ["liposuction", "surgery", "tumescent", "seroma", "lipoaspiração", "cirurgia", "tumescente"]),
 "SQ-LIP-000014": (["Treatment", "Diet"],
   ["ketogenic", "low-carb", "diet", "weight loss", "cetogênica", "baixo carboidrato", "dieta", "perda de peso"]),
 "SQ-LIP-000015": (["Treatment", "Management"],
   ["management", "multidisciplinary", "compression", "conservative", "manejo", "multidisciplinar", "compressão", "conservador"]),
 "SQ-LIP-000016": (["Treatment", "Pharmacology"],
   ["gestrinone", "off-label", "implant", "hormone", "gestrinona", "implante", "hormônio"]),
 "SQ-LIP-000017": (["Progression", "Complications"],
   ["lymphedema", "lipolymphedema", "disability", "mobility", "progression", "linfedema", "lipolinfedema", "incapacidade", "mobilidade", "progressão"]),
 "SQ-LIP-000018": (["Comorbidities", "Vascular"],
   ["varicose veins", "venous disease", "duplex", "venous ultrasound", "varizes", "doença venosa", "ultrassom venoso"]),
 "SQ-LIP-000019": (["History", "Treatment", "Surgery"],
   ["history", "Pitanguy", "Pitanguy 1964", "Allen Hines", "Wold", "Mayo Clinic", "milestones", "first surgery", "liposuction history", "história", "marcos históricos", "primeira cirurgia"]),
}

ORDER = ["id", "text", "text_pt", "knowledge_state", "tags", "keywords",
         "current_answer", "current_answer_pt", "major_uncertainty", "major_uncertainty_pt", "claims"]

data = json.load(open(QF))
added = 0
for q in data["questions"]:
    t = TAGS.get(q["id"])
    if t and not q.get("tags"):
        q["tags"], q["keywords"] = t
        added += 1
    extras = {k: v for k, v in q.items() if k not in ORDER}
    new = {k: q[k] for k in ORDER if k in q}
    new.update(extras)
    q.clear(); q.update(new)

json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
print(f"Tagged {added} question(s); {sum(1 for q in data['questions'] if q.get('tags'))}/{len(data['questions'])} now have tags+keywords.")
