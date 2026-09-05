#!/usr/bin/env python3
"""Add the historical milestone question (SQ-LIP-000019) and its founding claims
(SCR-LIP-000051..054) to the seeds. Idempotent: skips if SCR-LIP-000051 already present.
References verified via PubMed (Pitanguy 1964, Schmeller 2011, Baumgartner 2020);
Allen&Hines 1940 and Wold 1951 are pre-MEDLINE (cited bibliographically, no DOI/PMID).
Run from registry/: python3 add_history.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
CF, QF = os.path.join(HERE, "claims.json"), os.path.join(HERE, "questions.json")
CURATOR = [{"name": "Alexandre C. M. Amato", "orcid": "0000-0003-4008-4029", "role": "lead_curator"}]

def claim(cid, stmt, stmt_pt, ev, gaps, ctx_exposure):
    return {"id": cid, "statement": stmt, "statement_pt": stmt_pt, "claim_type": "historical",
            "context": {"population": "patients with lipedema / disproportionate gynoid fat (historical)",
                        "condition": "lipedema", "exposure": ctx_exposure,
                        "comparator": "n/a (historical landmark)", "outcome": "description / surgical treatment",
                        "scope": "historical record"},
            "knowledge_state": "established", "evidence_confidence": "low",
            "evidence": ev, "relations": [], "gaps": gaps, "primary_amato_source": None,
            "curators": CURATOR, "created": "2026-05-30", "updated": "2026-05-30", "license": "CC-BY-4.0"}

NEW_CLAIMS = [
 claim("SCR-LIP-000051",
   "Lipedema was first delineated as a distinct clinical syndrome by Allen and Hines at the Mayo Clinic in 1940, who coined the term and described the disproportionate, bilateral, foot-sparing leg fat with edema that defines it.",
   "O lipedema foi delineado pela primeira vez como síndrome clínica distinta por Allen e Hines, na Mayo Clinic, em 1940, que cunharam o termo e descreveram a gordura desproporcional, bilateral e poupadora dos pés, com edema, que o define.",
   [{"ref": "Allen EV, Hines EA Jr. Lipedema of the legs: a syndrome characterized by fat legs and edema. Proc Staff Meet Mayo Clin 1940;15:184-7",
     "stance": "supporting", "study_design": "clinical_description", "n": None, "risk_of_bias": "high",
     "year": 1940, "amato_authored": False, "note": "Original description; coined the term 'lipedema'. Pre-MEDLINE (no DOI/PMID)."}],
   "Historical descriptive report predating modern diagnostic criteria and imaging.",
   "first clinical description (1940)"),
 claim("SCR-LIP-000052",
   "The clinical syndrome was consolidated in 1951 when Wold, Hines and Allen reported a large case series (about 119 patients) detailing lipedema's orthostatic edema, pain and strong predominance in women.",
   "A síndrome clínica foi consolidada em 1951, quando Wold, Hines e Allen relataram uma grande série de casos (cerca de 119 pacientes), detalhando o edema ortostático, a dor e a forte predominância no sexo feminino do lipedema.",
   [{"ref": "Wold LE, Hines EA Jr, Allen EV. Lipedema of the legs: a syndrome characterized by fat legs and orthostatic edema. Ann Intern Med 1951;34(5):1243-50",
     "stance": "supporting", "study_design": "case_series", "n": 119, "risk_of_bias": "high",
     "year": 1951, "amato_authored": False, "note": "First large clinical series (~119 patients). Early-MEDLINE; cited bibliographically."}],
   "Uncontrolled historical case series; predates modern criteria.",
   "first large case series (1951)"),
 claim("SCR-LIP-000053",
   "The first surgical approach to the disproportionate gynoid/trochanteric fat deposits characteristic of lipedema is attributed to Ivo Pitanguy's 1964 description of the surgical correction of 'trochanteric lipodystrophy' (the 'saddlebag' deformity).",
   "A primeira abordagem cirúrgica dos depósitos de gordura ginoide/trocantérica desproporcionais característicos do lipedema é atribuída à descrição, por Ivo Pitanguy em 1964, da correção cirúrgica da 'lipodistrofia trocantérica' (a deformidade em 'culote').",
   [{"ref": "DOI:10.1097/00006534-196409000-00010", "stance": "supporting", "study_design": "surgical_technique",
     "n": None, "risk_of_bias": "high", "year": 1964, "amato_authored": False,
     "note": "Pitanguy I. Trochanteric lipodystrophy. Plast Reconstr Surg 1964;34:280-6 (PMID 14209176). Excisional correction of trochanteric fat — an early landmark in the surgical lineage later refined by liposuction."}],
   "'First surgery' is an interpretive attribution: the 1964 report addresses trochanteric lipodystrophy (disproportionate gynoid fat), predates modern lipedema criteria, and was excisional rather than liposuction.",
   "first surgical correction — Pitanguy (1964)"),
 claim("SCR-LIP-000054",
   "Modern surgical treatment of lipedema is lymph-sparing tumescent liposuction, established from the 2000s; single-centre cohorts report sustained reductions in pain, edema and need for conservative therapy at up to 12 years of follow-up.",
   "O tratamento cirúrgico moderno do lipedema é a lipoaspiração tumescente poupadora de linfáticos, estabelecida a partir dos anos 2000; coortes unicêntricas relatam reduções sustentadas de dor, edema e necessidade de terapia conservadora em seguimento de até 12 anos.",
   [{"ref": "DOI:10.1111/j.1365-2133.2011.10566.x", "stance": "supporting", "study_design": "cohort", "n": 112,
     "risk_of_bias": "moderate", "year": 2011, "amato_authored": False,
     "note": "Schmeller W, Hueppe M, Meier-Vollrath I. Tumescent liposuction in lipoedema yields good long-term results. Br J Dermatol 2011;166(1):161-8 (PMID 21824127)."},
    {"ref": "DOI:10.1177/0268355520949775", "stance": "supporting", "study_design": "cohort", "n": 60,
     "risk_of_bias": "moderate", "year": 2020, "amato_authored": False,
     "note": "Baumgartner A, Hueppe M, Meier-Vollrath I, Schmeller W. Improvements 4, 8 and 12 years after liposuction. Phlebology 2020;36(2):152-9 (PMID 32847472)."}],
   "Uncontrolled single-centre before-after cohorts; no randomized comparison (see SQ-LIP-000013).",
   "lymph-sparing tumescent liposuction (2000s–)"),
]

NEW_Q = {
  "id": "SQ-LIP-000019",
  "text": "What are the historical milestones in the description and surgical treatment of lipedema?",
  "text_pt": "Quais são os marcos históricos na descrição e no tratamento cirúrgico do lipedema?",
  "knowledge_state": "established",
  "current_answer": "Lipedema was first described as a distinct syndrome by Allen and Hines at the Mayo Clinic in 1940, and consolidated in a large case series by Wold, Hines and Allen in 1951. On the surgical side, Ivo Pitanguy's 1964 paper on 'trochanteric lipodystrophy' is an early landmark in operating on the disproportionate gynoid fat that characterizes the condition — predating the development of liposuction (Fischer, 1970s; Illouz, 1980s). The modern, lipedema-specific surgical treatment is lymph-sparing tumescent liposuction, with single-centre cohorts reporting durable symptom relief at up to 12 years. These entries record how the field developed; they are historical landmarks, not head-to-head effectiveness comparisons.",
  "current_answer_pt": "O lipedema foi descrito pela primeira vez como síndrome distinta por Allen e Hines, na Mayo Clinic, em 1940, e consolidado em uma grande série de casos por Wold, Hines e Allen em 1951. No campo cirúrgico, o artigo de Ivo Pitanguy de 1964 sobre a 'lipodistrofia trocantérica' é um marco inicial na operação da gordura ginoide desproporcional que caracteriza a condição — anterior ao desenvolvimento da lipoaspiração (Fischer, anos 1970; Illouz, anos 1980). O tratamento cirúrgico moderno, específico para o lipedema, é a lipoaspiração tumescente poupadora de linfáticos, com coortes unicêntricas relatando alívio sintomático durável em até 12 anos. Estes registros documentam como o campo evoluiu; são marcos históricos, não comparações diretas de eficácia.",
  "major_uncertainty": "Historical 'firsts' are attributions, not settled facts: early reports predate modern lipedema criteria, and the boundary with adjacent fat-distribution disorders (e.g. trochanteric lipodystrophy) is blurred.",
  "major_uncertainty_pt": "Os 'pioneirismos' históricos são atribuições, não fatos consolidados: relatos antigos antecedem os critérios modernos de lipedema, e o limite com distúrbios adjacentes de distribuição de gordura (p.ex., lipodistrofia trocantérica) é impreciso.",
  "claims": [
    {"id": "SCR-LIP-000051", "role": "supporting"},
    {"id": "SCR-LIP-000052", "role": "supporting"},
    {"id": "SCR-LIP-000053", "role": "supporting"},
    {"id": "SCR-LIP-000054", "role": "supporting"},
    {"id": "SCR-LIP-000030", "role": "context"}
  ]
}

cd = json.load(open(CF))
if any(c["id"] == "SCR-LIP-000051" for c in cd["claims"]):
    print("Already added — skipping."); raise SystemExit
cd["claims"].extend(NEW_CLAIMS)
cd["count"] = len(cd["claims"])
json.dump(cd, open(CF, "w"), ensure_ascii=False, indent=2)

qd = json.load(open(QF))
qd["questions"].append(NEW_Q)
json.dump(qd, open(QF, "w"), ensure_ascii=False, indent=2)
print(f"Added {len(NEW_CLAIMS)} historical claims (now {cd['count']}) and 1 question (now {len(qd['questions'])}).")
