#!/usr/bin/env python3
"""Generate the question-centric pages of scientificclaims.org from the registry — BILINGUAL.
Reads ../registry/questions.json + ../registry/claims.json and writes, for EN (root) and PT (/pt/):
  [pt/]questions.html          — registry index (questions as the primary object)
  [pt/]q/<id>.html             — the CURRENT versioned evidence page per question
  [pt/]q/<id>/v<ver>.html      — frozen, citable SNAPSHOT of each version
  q/<id>.json                  — machine-readable (EN canonical; linked from both languages)
  sitemap.xml                  — full sitemap with hreflang (both languages)
PT content comes from *_pt fields in the JSON (seeded / auto-filled by translate.py).
Run from site/: python3 build_questions.py
"""
import json, os, html, hashlib
from collections import Counter
from scrlib import timeline_svg, ref_link, ref_url, ev_label, cite_link, ANALYTICS
SITE = os.path.dirname(os.path.abspath(__file__))
# cache-bust the stylesheet: static assets are served with a 10-yr max-age, so a content hash in the
# query string is the only way a CSS change reaches users (no Cloudflare purge token anymore).
CSSVER = hashlib.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"), "rb").read()).hexdigest()[:8]
REG = os.path.join(SITE, "..", "registry")
Q = json.load(open(os.path.join(REG, "questions.json")))
C = {c["id"]: c for c in json.load(open(os.path.join(REG, "claims.json")))["claims"]}
QMAP = {q["id"]: q for q in Q["questions"]}
# Registry-wide verification rollup (R-AI-14) — every evidence source's independent-verification verdict.
_ALLV = [(ev.get("verification") or {}).get("verdict") or "unverified"
         for c in C.values() for ev in c.get("evidence", [])]
GLOBAL_VERIFY = {"verified": _ALLV.count("verified"), "disputed": _ALLV.count("disputed"),
                 "unverified": len(_ALLV) - _ALLV.count("verified") - _ALLV.count("disputed"),
                 "total": len(_ALLV), "pct_verified": round(100 * _ALLV.count("verified") / max(1, len(_ALLV)))}
def e(s): return html.escape(str(s if s is not None else ""))
DATE = Q.get("date", "2026-05-30"); YEAR = int(DATE[:4]); RECENT = YEAR - 5
BASE = "https://scientificclaims.org"
CUR_VER = "1.0"  # current/only version of the founding index

STATE_L = {
  "en": {"speculative":"Speculative","emerging":"Emerging","probable":"Probable","established":"Established","foundational":"Foundational","no_evidence":"Evidence gap"},
  "pt": {"speculative":"Especulativo","emerging":"Emergente","probable":"Provável","established":"Estabelecido","foundational":"Fundacional","no_evidence":"Lacuna de evidência"},
}
# UI strings per language
T = {
 "en": {
  "nav_q":"Questions","nav_c":"Claims","lang":"PT","lang_href_prefix":"/pt",
  "json":"machine-readable JSON →","current":"current","archived":"archived",
  "cur_answer":"Current answer","k_state":"Knowledge state","k_fresh":"Knowledge freshness",
  "k_verify":"Evidence verification","verify_sources":"sources independently verified","verify_review":"need review","verify_nosrc":"source not retrievable",
  "verify_note":"Each evidence source is independently re-read by a second AI model that must confirm its stance and a verbatim quote from the source; only then is it marked verified (R-AI-13/14).",
  "recent":"recent","created_l":"Created","last_upd":"Last updated","hreview":"Human review","not_rev":"not yet reviewed",
  "supporting":"consistent","contradicting":"conflicting","refctx":"refining / contextual",
  "ev_time":"Evidence over time","ans_time":"Answer over time",
  "ans_time_note":"Each node is a published version of the answer — open one to read the answer exactly as it stood then.",
  "ver_noarch":"snapshot not archived",
  "cite_h":"How to cite this version",
  "what_changed":"What changed in this version","sup_claims":"Consistent claims",
  "con_claims":"Conflicting claims","refctx_h":"Refining / contextual","major_unc":"Major uncertainty",
  "verhist":"Version history","keyrefs":"Key references","allq":"← All questions",
  "none_idx":"None indexed yet.","view_ver":"view this version","cur_ver_link":"View current version →",
  "founding":"founding index","claims_word":"claims","updated":"updated",
  "cite_help":"Choose a format (Vancouver default). Citing a version captures the evidence state on that date; this page shows the current version — see ",
  "vhist_anchor":"version history",
  "fresh_note_a":"Knowledge freshness = share of the","fresh_note_b":"indexed evidence sources from the last 5 years (newest",
  "fresh_note_c":"oldest","fresh_note_d":") . Low freshness flags an","fresh_ageing":"ageing evidence base","fresh_note_e":"— not that the answer is wrong.",
  "small_base":"small evidence base","small_base_t":"High freshness on very few sources — reflects recency, not robustness. Read with caution.",
  "tl_note":"Each dot is a study, placed by year and coloured by whether the linked claim supports or contradicts the answer. As the surveillance loop runs, claim revisions and new evidence will extend this timeline.",
  "first_mention_l":"First literature mention","origin_note":"The hollow ring marks the first time this topic appears in the literature.",
  "changed_txt":lambda n:f"Initial version (v{CUR_VER}): {n} founding claims indexed from the lipedema pilot. The automated surveillance loop (new-article ingestion → supports / contradicts / refines) has not yet run.",
  "archived_banner":lambda v,d:f'📌 Archived version <strong>v{v}</strong> ({d}) — a fixed snapshot for citation.',
  "idx_title":"Scientific questions — Scientific Claim Registry","idx_h1":"Scientific questions",
  "idx_sub":lambda n:f'SCR creates versioned, AI-assisted evidence pages for scientific questions — tracking how the answer changes over time, and how fresh the underlying evidence is. {n} questions in the lipedema pilot. Each answer is bounded by the currently indexed evidence; it does not give an opinion. Every version is citable, and every page has a machine-readable JSON for LLMs and agents.',
  "idx_desc":lambda n:f"{n} scientific questions about lipedema, each with a current evidence-bounded answer, knowledge state, knowledge-freshness, supporting and contradicting claims, citable version history, and machine-readable JSON.",
  "idx_verify":lambda gv:f'<strong>{gv["verified"]} of {gv["total"]}</strong> evidence sources independently AI-verified · {gv["disputed"]} need review',
  "all":"All","fresh_short":"fresh","supporting_n":"consistent","contradicting_n":"conflicting",
  "search_ph":"Search questions, keywords, tags…","no_results":"No questions match your search.",
  "also_asked":"Also asked as",
  "ai_consol":"AI consolidation","ai_consol_note":"evidence-bounded; the AI does not opine",
  "answer_cap":"A synthesis rendered from the currently indexed evidence — versioned, not a verdict.",
  "glance_h":"Answer at a glance","evidence_l":"Evidence","confidence_l":"Evidence confidence","whatsnew":"What’s new in","aver":"Answer version",
  "synthesis_h":"Current synthesis","ai_compiled":"AI-compiled — not a verdict",
  "bl_h":"Bottom line","exec_h":"Executive synthesis","limitation_l":"Main limitation","recent_l":"Latest change","stability_l":"Stability",
  "contested":"contested","contra_none":"none indexed yet — the registry may under-detect disconfirming evidence (a known limitation)",
  "stab_new":"New","stab_evolving":"Evolving","stab_stabilizing":"Stabilizing","stab_settled":"Settled",
  "related_h":"Related questions",
  "outcomes_h":"By outcome","disease_mod":"disease-modifying","symptom_only":"symptom-only",
  "dir_improved":"improved","dir_reduced":"reduced","dir_increased":"increased","dir_no_effect":"no effect","dir_not_demonstrated":"not demonstrated","dir_mixed":"mixed",
  "prev":"‹ Prev","next":"Next ›","showing":"showing","of":"of","results":"results",
  "foot_tag":"PubMed stores scientific papers. SCR stores the evolving answers to scientific questions.",
  "foot_dis":"The goal is not to determine truth, but to make the evolution of knowledge traceable. Not medical advice.",
 },
 "pt": {
  "nav_q":"Perguntas","nav_c":"Claims","lang":"EN","lang_href_prefix":"",
  "json":"JSON legível por máquina →","current":"atual","archived":"arquivado",
  "cur_answer":"Resposta atual","k_state":"Estado do conhecimento","k_fresh":"Atualidade da evidência",
  "k_verify":"Verificação da evidência","verify_sources":"fontes verificadas de forma independente","verify_review":"requerem revisão","verify_nosrc":"fonte não recuperável",
  "verify_note":"Cada fonte de evidência é relida por um segundo modelo de IA, que precisa confirmar o stance e uma citação verbatim da fonte; só então é marcada como verificada (R-AI-13/14).",
  "recent":"recentes","created_l":"Criado","last_upd":"Última atualização","hreview":"Revisão humana","not_rev":"ainda não revisado",
  "supporting":"consistentes","contradicting":"conflitantes","refctx":"refinam / contextuais",
  "ev_time":"Evidência ao longo do tempo","ans_time":"Resposta ao longo do tempo",
  "ans_time_note":"Cada nó é uma versão publicada da resposta — abra uma para ler a resposta como estava naquele momento.",
  "ver_noarch":"snapshot não arquivado",
  "cite_h":"Como citar esta versão",
  "what_changed":"O que mudou nesta versão","sup_claims":"Claims consistentes",
  "con_claims":"Claims conflitantes","refctx_h":"Refinam / contextuais","major_unc":"Maior incerteza",
  "verhist":"Histórico de versões","keyrefs":"Referências principais","allq":"← Todas as perguntas",
  "none_idx":"Nenhum indexado ainda.","view_ver":"ver esta versão","cur_ver_link":"Ver a versão atual →",
  "founding":"índice fundador","claims_word":"claims","updated":"atualizado",
  "cite_help":"Escolha um formato (Vancouver é o padrão). Citar uma versão captura o estado da evidência naquela data; esta página mostra a versão atual — veja o ",
  "vhist_anchor":"histórico de versões",
  "fresh_note_a":"Atualidade da evidência = proporção das","fresh_note_b":"fontes de evidência indexadas dos últimos 5 anos (mais nova",
  "fresh_note_c":"mais antiga","fresh_note_d":") . Baixa atualidade sinaliza uma","fresh_ageing":"base de evidência envelhecendo","fresh_note_e":"— não que a resposta esteja errada.",
  "small_base":"base de evidência pequena","small_base_t":"Atualidade alta com pouquíssimas fontes — reflete recência, não robustez. Leia com cautela.",
  "tl_note":"Cada ponto é um estudo, posicionado pelo ano e colorido conforme o claim vinculado apoie ou contrarie a resposta. À medida que o laço de vigilância roda, revisões de claims e novas evidências estendem esta linha do tempo.",
  "first_mention_l":"Primeira menção na literatura","origin_note":"O anel vazado marca a primeira vez que o tema aparece na literatura.",
  "changed_txt":lambda n:f"Versão inicial (v{CUR_VER}): {n} claims fundadores indexados do piloto de lipedema. O laço de vigilância automatizado (ingestão de novos artigos → apoia / contraria / refina) ainda não rodou.",
  "archived_banner":lambda v,d:f'📌 Versão arquivada <strong>v{v}</strong> ({d}) — um instantâneo fixo para citação.',
  "idx_title":"Perguntas científicas — Scientific Claim Registry","idx_h1":"Perguntas científicas",
  "idx_sub":lambda n:f'O SCR cria páginas de evidência versionadas e assistidas por IA para perguntas científicas — registrando como a resposta muda ao longo do tempo e quão atual é a evidência subjacente. {n} perguntas no piloto de lipedema. Cada resposta é limitada pela evidência atualmente indexada; não dá opinião. Toda versão é citável, e cada página tem um JSON legível por máquina para LLMs e agentes.',
  "idx_verify":lambda gv:f'<strong>{gv["verified"]} de {gv["total"]}</strong> fontes de evidência verificadas de forma independente por IA · {gv["disputed"]} em revisão',
  "idx_desc":lambda n:f"{n} perguntas científicas sobre lipedema, cada uma com uma resposta atual limitada pela evidência, estado do conhecimento, atualidade da evidência, claims favoráveis e contrários, histórico de versões citável e JSON legível por máquina.",
  "all":"Todas","fresh_short":"atual","supporting_n":"consistentes","contradicting_n":"conflitantes",
  "search_ph":"Buscar perguntas, palavras-chave, tags…","no_results":"Nenhuma pergunta corresponde à busca.",
  "also_asked":"Também perguntada como",
  "ai_consol":"Consolidação por IA","ai_consol_note":"limitada à evidência; a IA não opina",
  "answer_cap":"Uma síntese renderizada da evidência atualmente indexada — versionada, não um veredito.",
  "glance_h":"Resposta em resumo","evidence_l":"Evidência","confidence_l":"Confiança da evidência","whatsnew":"Novidades na","aver":"Versão da resposta",
  "synthesis_h":"Síntese atual","ai_compiled":"Compilada por IA — não é um veredito",
  "bl_h":"Conclusão","exec_h":"Resumo executivo","limitation_l":"Limitação principal","recent_l":"Mudança recente","stability_l":"Estabilidade",
  "contested":"contestada","contra_none":"nenhuma indexada ainda — o registro pode sub-detectar evidência discordante (limitação conhecida)",
  "stab_new":"Nova","stab_evolving":"Em evolução","stab_stabilizing":"Estabilizando","stab_settled":"Assentada",
  "related_h":"Perguntas relacionadas",
  "outcomes_h":"Por desfecho","disease_mod":"modifica a doença","symptom_only":"só sintomático",
  "dir_improved":"melhora","dir_reduced":"reduz","dir_increased":"aumenta","dir_no_effect":"sem efeito","dir_not_demonstrated":"não demonstrado","dir_mixed":"misto",
  "prev":"‹ Anterior","next":"Próxima ›","showing":"mostrando","of":"de","results":"resultados",
  "foot_tag":"O PubMed guarda artigos científicos. O SCR guarda as respostas em evolução às perguntas científicas.",
  "foot_dis":"O objetivo não é determinar a verdade, mas tornar rastreável a evolução do conhecimento. Não é orientação médica.",
 },
}

TAG_PT = {"Definition":"Definição","Diagnosis":"Diagnóstico","Epidemiology":"Epidemiologia","Imaging":"Imagem",
  "Screening":"Rastreamento","Comorbidities":"Comorbidades","Mental health":"Saúde mental","Pain":"Dor",
  "Genetics":"Genética","Pathophysiology":"Fisiopatologia","Metabolism":"Metabolismo","Etiology":"Etiologia",
  "Hormones":"Hormônios","Treatment":"Tratamento","Surgery":"Cirurgia","Diet":"Dieta","Management":"Manejo",
  "Pharmacology":"Farmacologia","Progression":"Progressão","Complications":"Complicações","Vascular":"Vascular",
  "History":"História"}

def tag_label(tag, lang):
    return TAG_PT.get(tag, tag) if lang == "pt" else tag

def fresh_label(pct, lang):
    if lang == "pt":
        return "base de evidência atual" if pct >= 70 else ("mista" if pct >= 40 else "base de evidência envelhecendo")
    return "current evidence base" if pct >= 70 else ("mixed" if pct >= 40 else "ageing evidence base")

def small_base_badge(fr, lang):
    # High freshness can mislead when the base is tiny: flag pct>=90 & sources<6 (R-FRESH-4).
    if not fr or fr["pct"] < 90 or fr["sources"] >= 6:
        return ""
    t = T[lang]
    return (f' <span class="sbadge" title="{e(t["small_base_t"])}">⚠ {t["small_base"]} '
            f'(n={fr["sources"]})</span>')

def field(q, key, lang):
    return (q.get(key + "_pt") or q.get(key)) if lang == "pt" else q.get(key)

def claim_text(cid, lang):
    c = C.get(cid, {})
    return (c.get("statement_pt") or c.get("statement")) if lang == "pt" else c.get("statement", "")

def head(lang, title, desc, page_path, robots="index,follow", keywords=""):
    """page_path is the EN-relative path, e.g. '/q/SQ-LIP-000005.html'."""
    t = T[lang]; prefix = "/pt" if lang == "pt" else ""
    canon = f"{BASE}{prefix}{page_path}"
    kw = f'<meta name="keywords" content="{e(keywords)}">\n' if keywords else ""
    alts = (f'<link rel="alternate" hreflang="en" href="{BASE}{page_path}">\n'
            f'<link rel="alternate" hreflang="pt-BR" href="{BASE}/pt{page_path}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{BASE}{page_path}">')
    lang_href = f'{t["lang_href_prefix"]}{page_path}'
    htmllang = "pt-BR" if lang == "pt" else "en"
    return f'''<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{kw}<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
{alts}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/style.css?v={CSSVER}">
{ANALYTICS}
</head>
<body>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{prefix}/"><span class="mono">SCR</span> <span class="brand-full">Scientific Claim Registry</span></a>
    <nav><a href="{prefix}/questions.html" class="active">{t["nav_q"]}</a><a href="{prefix}/claims.html">{t["nav_c"]}</a><a class="lang" href="{lang_href}">{t["lang"]}</a></nav>
  </div>
</header>'''

def foot(lang):
    t = T[lang]
    return f'''<footer class="site"><div class="wrap foot">
  <div><p class="brand"><span class="mono">SCR</span> Scientific Claim Registry</p>
  <p class="muted">{t["foot_tag"]}</p></div>
  <div class="muted small"><p>CC BY 4.0 · DOI <a href="https://doi.org/10.5281/zenodo.20466195">10.5281/zenodo.20466195</a></p>
  <p>{t["foot_dis"]}</p></div>
</div></footer></body></html>'''

def counts(links):
    sup = sum(1 for l in links if l["role"] == "supporting")
    con = sum(1 for l in links if l["role"] == "contradicting")
    return sup, con, len(links) - sup - con

_GRANK = {"very_low": 0, "low": 1, "moderate": 2, "high": 3}
_GLBL = {"en": {"very_low": "very low", "low": "low", "moderate": "moderate", "high": "high"},
         "pt": {"very_low": "muito baixa", "low": "baixa", "moderate": "moderada", "high": "alta"}}

def grade_summary(links, lang):
    """Question-level GRADE: the PREDOMINANT per-source grade across the linked claims (R-CLM-11),
    widened to an adjacent grade only when that neighbour is also common (→ e.g. 'low–moderate').
    Avoids the uninformative full span (almost every multi-source question spans very low–high)."""
    grs = [ev.get("grade") for l in links for ev in C.get(l["id"], {}).get("evidence", []) if ev.get("grade") in _GRANK]
    if not grs:
        return "—"
    cnt = {g: grs.count(g) for g in set(grs)}
    lbl = _GLBL[lang]
    ranked = sorted(cnt.items(), key=lambda kv: (-kv[1], -_GRANK[kv[0]]))  # count desc, then quality desc
    top, top_n = ranked[0]
    nbr = [g for g, c in ranked[1:] if abs(_GRANK[g] - _GRANK[top]) == 1 and c >= top_n / 2]
    if nbr:
        lo, hi = sorted([top, nbr[0]], key=lambda g: _GRANK[g])
        return f"{lbl[lo]}–{lbl[hi]}"
    return lbl[top]

def first_sentence(text, maxlen=180):
    """One-line gist: drop the evidence-bounded boilerplate prefix, take the first sentence, truncate."""
    s = (text or "").strip()
    for pre in ("Based on currently indexed evidence, ", "Com base nas evidências atualmente indexadas, "):
        if s.startswith(pre):
            s = s[len(pre):]; s = s[:1].upper() + s[1:]
    cut = s.split(". ")[0]
    if len(cut) > maxlen:
        cut = cut[:maxlen].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
    elif len(cut) < len(s):
        cut += "."
    return cut

# Answer Stability — a TRANSPARENT, rule-based label (R-SITE-13), not an invented score.
_STAB_BASE = {"foundational": "settled", "established": "settled", "probable": "stabilizing",
              "emerging": "evolving", "speculative": "new", "no_evidence": "new"}

def stability(q, con):
    """(label_key, contested) from visible signals: knowledge state, revision count, contradiction presence."""
    nver = len(q.get("history") or [])
    lab = _STAB_BASE.get(q.get("knowledge_state"), "evolving")
    if nver <= 1:
        lab = "new"
    return lab, con > 0

def render_outcomes(q, t, lang):
    """R-Q-7: per-outcome breakdown (effective for WHAT?), separating symptom relief from disease modification."""
    outs = q.get("outcomes") or []
    if not outs:
        return ""
    rows = ""
    for o in outs:
        label = o.get("outcome_pt" if lang == "pt" else "outcome") or o.get("outcome") or ""
        d = (o.get("direction") or "").lower()
        conf = o.get("confidence") or "—"
        note = o.get("note_pt" if lang == "pt" else "note") or o.get("note") or ""
        dm = o.get("disease_modifying")
        tag = (f'<span class="dmtag dm-yes">{t["disease_mod"]}</span>' if dm is True else
               (f'<span class="dmtag dm-no">{t["symptom_only"]}</span>' if dm is False else ""))
        rows += (f'<tr><td class="oc-name">{e(label)}</td>'
                 f'<td><span class="oc-dir d-{e(d)}">{e(t.get("dir_" + d, d))}</span></td>'
                 f'<td class="oc-conf">{e(conf)} <span class="muted">(GRADE)</span></td>'
                 f'<td class="oc-tag">{tag}</td></tr>')
        if note:
            rows += f'<tr class="oc-note"><td></td><td colspan="3">{e(note)}</td></tr>'
    return f'<div class="outcomes"><span class="glance-h">{t["outcomes_h"]}</span><table>{rows}</table></div>'

def freshness(links):
    years = [ev["year"] for l in links for ev in C.get(l["id"], {}).get("evidence", []) if isinstance(ev.get("year"), int)]
    if not years: return None
    pct = round(100 * sum(1 for y in years if y >= RECENT) / len(years))
    return {"pct": pct, "sources": len(years), "newest": max(years), "oldest": min(years),
            "small_base": pct >= 90 and len(years) < 6,
            "label": "current evidence base" if pct >= 70 else ("mixed" if pct >= 40 else "ageing evidence base")}

def verification_rollup(links):
    """Question-level verification rollup (R-AI-14): how many of the answer's evidence sources had their
    stance + sentence-level provenance independently confirmed by a second model (verified), vs needing
    review (disputed) or unverifiable (no recoverable source text)."""
    vd = [(ev.get("verification") or {}).get("verdict") or "unverified"
          for l in links for ev in C.get(l["id"], {}).get("evidence", [])]
    n = len(vd)
    if not n:
        return None
    ver = vd.count("verified"); dis = vd.count("disputed")
    return {"verified": ver, "disputed": dis, "unverified": n - ver - dis, "total": n,
            "pct_verified": round(100 * ver / n)}

def refs_of(links):
    out = []
    for l in links:
        for ev in C.get(l["id"], {}).get("evidence", []):
            r = ev.get("ref", "")
            if r and r.startswith(("DOI:", "PMID:")) and r not in out: out.append(r)
    return out

def legend(lang):
    t = T[lang]
    dot = lambda k, lab: f'<span class="tldot" style="background:{k}"></span>{lab}'
    return (f'<span class="tllg">{dot("#1d7a4f", t["supporting"])} &nbsp; '
            f'{dot("#a23b52", t["contradicting"])} &nbsp; {dot("#1f6a93", t["refctx"])}</span>')

def version_track(hist, qid, prefix, hchange, founding_label, archived, noarch_note):
    """Second timeline: the published VERSIONS of the answer over time (the answer's own evolution),
    distinct from 'Evidence over time' (the studies). A version node links to its frozen snapshot ONLY
    when that snapshot exists on disk (`archived`); older versions whose snapshot was never captured
    render as non-links (their past answer text is not reconstructable from the seeds)."""
    if not hist:
        return ""
    def vkey(h):
        try: return tuple(int(x) for x in str(h.get("version", "0")).split("."))
        except Exception: return (0,)
    hist = sorted(hist, key=lambda h: (h.get("date", ""), vkey(h)))  # chronological: oldest → newest
    n = len(hist)
    nodes = []
    for i, h in enumerate(hist):
        ver = h.get("version", "1.0"); date = h.get("date", "")
        change = hchange(h) or founding_label
        cur = " cur" if i == n - 1 else ""
        body = (f'<span class="vdot"></span><span class="vver">v{ver}</span>'
                f'<span class="vdate">{e(date)}</span>')
        if ver in archived:
            nodes.append(f'<a class="vnode{cur}" href="{prefix}/q/{qid}/v{ver}.html" title="{e(change)}">{body}</a>')
        else:
            nodes.append(f'<span class="vnode{cur} noarch" title="{e(change)} · {e(noarch_note)}">{body}</span>')
    return f'<div class="vtrack">{"".join(nodes)}</div>'

def build_lang(lang):
    t = T[lang]; STATE = STATE_L[lang]
    out_root = os.path.join(SITE, "pt") if lang == "pt" else SITE
    prefix = "/pt" if lang == "pt" else ""
    os.makedirs(os.path.join(out_root, "q"), exist_ok=True)

    def claim_li(l):
        cc = C.get(l["id"], {})
        ev_refs = " · ".join(cite_link(x) for x in cc.get("evidence", []))
        refs_line = f'<br><span class="ctext-refs mono">{ev_refs}</span>' if ev_refs else ""
        return (f'<li><a class="cid mono" href="{prefix}/c/{l["id"]}.html">{e(l["id"])}</a> '
                f'<span class="role role-{l["role"]}">{e(t.get(l["role"], l["role"]))}</span><br>'
                f'<span class="ctext">{e(claim_text(l["id"], lang))}</span>{refs_line}</li>')

    for q in Q["questions"]:
        qid = q["id"]; links = q.get("claims", [])
        qtext = field(q, "text", lang); qans = field(q, "current_answer", lang)
        qunc = field(q, "major_uncertainty", lang)
        sup, con, oth = counts(links); fr = freshness(links); refs = refs_of(links)
        vr = verification_rollup(links)
        grade_sum = grade_summary(links, lang)
        stab_key, contested = stability(q, con)
        tags = q.get("tags", []); keywords = q.get("keywords", [])
        qtags_html = ('<div class="qtags">' + "".join(
            f'<a class="qtag" href="{prefix}/questions.html?tag={e(tg)}">{e(tag_label(tg, lang))}</a>' for tg in tags)
            + '</div>') if tags else ""
        kw_meta = ", ".join(tags + keywords)
        ver = q.get("version", CUR_VER)
        updated = q.get("updated", DATE)
        created = q.get("created", DATE)
        hist = q.get("history") or [{"version": ver, "date": updated, "change": None}]
        hchange = lambda h: ((h.get("change_pt") or h.get("change")) if lang == "pt" else h.get("change"))
        last_change = hchange(hist[0]) or t["changed_txt"](sup + con + oth)
        phr_l = (q.get("phrasings_pt") if lang == "pt" else q.get("phrasings")) or []
        phr_html = (f'<details class="qphr"><summary>{t["also_asked"]}</summary><ul>'
                    + "".join(f"<li>{e(p)}</li>" for p in phr_l) + "</ul></details>") if phr_l else ""
        outcomes_html = render_outcomes(q, t, lang)
        bl = field(q, "bottom_line", lang)
        bottom_html = (f'<div class="bottomline"><span class="bl-h">{t["bl_h"]}</span>'
                       f'<p>{e(bl)}</p></div>') if bl else ""
        rel_ids = [r for r in (q.get("related") or []) if r in QMAP]
        related_html = (f'<div class="related"><span class="qf-lbl">{t["related_h"]}</span><ul>'
                        + "".join(f'<li><a href="{prefix}/q/{r}.html">'
                                  f'{e(QMAP[r].get("text_pt") if (lang=="pt" and QMAP[r].get("text_pt")) else QMAP[r]["text"])}</a></li>'
                                  for r in rel_ids) + "</ul></div>") if rel_ids else ""
        cb = q.get("compiled_by") or {}
        ai_prov = (f'<p class="ai-prov" title="{t["ai_consol_note"]}">⚙ {t["ai_consol"]}: '
                   f'<strong>{e(cb.get("label") or cb.get("model"))}</strong>'
                   f'{" · " + e(cb.get("date")) if cb.get("date") else ""} '
                   f'<span class="muted">— {t["ai_consol_note"]}</span></p>') if cb else ""
        page_path = f"/q/{qid}.html"
        ver_path = f"/q/{qid}/v{ver}.html"
        ver_url = f"{BASE}{prefix}{ver_path}"

        # machine-readable JSON — generated once, in the EN pass (canonical), linked from both langs
        if lang == "en":
            cite = f'Scientific Claim Registry. {qtext}. {qid} v{ver}; {updated}. {ver_url}'
            mj = {"id": qid, "question": qtext, "question_pt": q.get("text_pt"),
                  "phrasings": q.get("phrasings", []), "phrasings_pt": q.get("phrasings_pt", []),
                  "knowledge_state": q["knowledge_state"], "tags": tags, "keywords": keywords,
                  "current_answer": qans, "current_answer_pt": q.get("current_answer_pt"),
                  "bottom_line": field(q, "bottom_line", lang), "bottom_line_pt": q.get("bottom_line_pt"),
                  "major_uncertainty": qunc, "version": ver, "created": created, "updated": updated,
                  "compiled_by": q.get("compiled_by"), "outcomes": q.get("outcomes") or [],
                  "evidence_direction": {"supporting": sup, "contradicting": con, "other": oth},
                  "knowledge_freshness": fr, "evidence_verification": vr,
                  "claims": [{"id": l["id"], "role": l["role"], "statement": C.get(l["id"], {}).get("statement")} for l in links],
                  "references": refs, "cite": cite,
                  "versions": [{"version": h["version"], "date": h["date"],
                                "url": f"{BASE}{prefix}/q/{qid}/v{h['version']}.html"} for h in hist],
                  "url": f"{BASE}{page_path}", "url_pt": f"{BASE}/pt{page_path}", "version_url": ver_url,
                  "license": "CC-BY-4.0", "disclaimer": "Evidence-bounded summary; not medical advice."}
            json.dump(mj, open(os.path.join(SITE, "q", f"{qid}.json"), "w"), ensure_ascii=False, indent=2)

        sup_li = "".join(claim_li(l) for l in links if l["role"] == "supporting") or f"<li class='muted'>{t['none_idx']}</li>"
        con_li = "".join(claim_li(l) for l in links if l["role"] == "contradicting") or f"<li class='muted'>{t['none_idx']}</li>"
        oth_li = "".join(claim_li(l) for l in links if l["role"] in ("refines", "context"))
        refs_html = " · ".join(f'<span class="mono">{ref_link(r)}</span>' for r in refs[:30]) or "<span class='muted'>—</span>"
        sb = small_base_badge(fr, lang)
        fr_tile = (f'<div><span class="mk">{t["k_fresh"]}</span><strong>{fr["pct"]}% {t["recent"]}</strong> '
                   f'<span class="muted">· {fresh_label(fr["pct"], lang)}</span>{sb}</div>' if fr else "")
        g_fresh = (f'<div class="g-row"><dt>{t["k_fresh"]}</dt><dd>{fr["pct"]}% {t["recent"]} '
                   f'<span class="muted">· {fresh_label(fr["pct"], lang)}</span>{sb}</dd></div>' if fr else "")
        g_verify = (f'<div class="g-row"><dt title="{e(t["verify_note"])}">{t["k_verify"]}</dt>'
                    f'<dd><strong>{vr["verified"]}/{vr["total"]}</strong> {t["verify_sources"]}'
                    + (f' <span class="muted">· {vr["disputed"]} {t["verify_review"]}</span>' if vr["disputed"] else '')
                    + (f' <span class="muted">· {vr["unverified"]} {t["verify_nosrc"]}</span>' if vr["unverified"] else '')
                    + '</dd></div>') if vr else ""
        fr_note = (f'<p class="frnote">{t["fresh_note_a"]} {fr["sources"]} {t["fresh_note_b"]} {fr["newest"]}, '
                   f'{t["fresh_note_c"]} {fr["oldest"]}{t["fresh_note_d"]} <strong>{t["fresh_ageing"]}</strong> {t["fresh_note_e"]}</p>' if fr else "")
        tl_items = [{"year": ev.get("year"), "kind": l["role"],
                     "label": ev_label(ev), "url": ref_url(ev.get("ref"))}
                    for l in links for ev in C.get(l["id"], {}).get("evidence", [])]
        ev_years = [it["year"] for it in tl_items if isinstance(it.get("year"), int)]
        fm = q.get("first_mention")
        show_origin = bool(fm and isinstance(fm.get("year"), int) and (not ev_years or fm["year"] < min(ev_years)))
        if show_origin:
            tl_items = [{"year": fm["year"], "kind": "origin", "url": ref_url(fm.get("ref")),
                         "label": f'{t["first_mention_l"]}: {fm.get("title") or fm.get("ref", "")}'}] + tl_items
        tl = timeline_svg(tl_items, w=680, h=56)
        origin_note = f' {t["origin_note"]}' if show_origin else ""
        tl_section = (f'<h2>{t["ev_time"]}</h2>\n  <div class="qtl">{tl}</div>\n'
                      f'  <p class="small muted">{legend(lang)} {t["tl_note"]}{origin_note}</p>' if tl else "")
        founding_label = t["founding"] + f" ({sup+con+oth} " + t["claims_word"] + ")"
        # a prior version is linkable only if its frozen snapshot exists on disk; the current
        # version is always written this build, so it is always linkable.
        archived = {ver} | {h.get("version") for h in hist
                            if os.path.exists(os.path.join(out_root, "q", qid, f"v{h.get('version')}.html"))}
        vtrack = version_track(hist, qid, prefix, hchange, founding_label, archived, t["ver_noarch"])
        ver_section = (f'<h2>{t["ans_time"]}</h2>\n  {vtrack}\n'
                       f'  <p class="small muted">{t["ans_time_note"]}</p>' if vtrack else "")
        yr = updated[:4]
        fmts = {
          "Vancouver": f'Scientific Claim Registry. {qtext} [Internet]. {qid} v{ver}; {t["updated"]} {updated}. Available from: {ver_url}',
          "APA": f'Scientific Claim Registry. ({yr}). {qtext} (Version {ver}) [Registry entry]. https://scientificclaims.org. {ver_url}',
          "Chicago": f'Scientific Claim Registry. "{qtext}" {qid}, v{ver}. {yr}. {ver_url}.',
          "BibTeX": "@misc{scr_" + qid.replace('-', '_') + ",\n  author = {{Scientific Claim Registry}},\n  title  = {{" + qtext + "}},\n  year   = {" + yr + "},\n  note   = {" + qid + " v" + ver + "},\n  howpublished = {\\url{" + ver_url + "}}\n}",
        }
        tabs = "".join(f'<button class="ctab{" active" if i==0 else ""}" data-f="{e(k)}">{e(k)}</button>' for i, k in enumerate(fmts))
        cite_block = f'''<div class="cite">
    <span class="alabel">{t["cite_h"]}</span>
    <div class="cite-tabs">{tabs}<button class="copybtn" id="citecopy">Copy</button></div>
    <pre class="cite-out" id="citeout"></pre>
    <script type="application/json" id="cfmt">{json.dumps(fmts, ensure_ascii=False)}</script>
    <p class="small muted">{t["cite_help"]}<a href="#vh">{t["vhist_anchor"]}</a>.</p>
    <script>(function(){{var el=document.getElementById('cfmt');if(!el)return;var d=JSON.parse(el.textContent);var out=document.getElementById('citeout');var ks=Object.keys(d);function show(f){{out.textContent=d[f];}}document.querySelectorAll('.ctab').forEach(function(b){{b.addEventListener('click',function(){{document.querySelectorAll('.ctab').forEach(function(x){{x.classList.remove('active');}});b.classList.add('active');show(b.getAttribute('data-f'));}});}});var cp=document.getElementById('citecopy');if(cp)cp.addEventListener('click',function(){{navigator.clipboard.writeText(out.textContent).then(function(){{cp.textContent='Copied';setTimeout(function(){{cp.textContent='Copy';}},1500);}});}});show(ks[0]);}})();</script>
  </div>'''
        vh_items = "".join(
            f'<li><span class="mono">{e(qid)} · v{h["version"]}</span> — {e(h["date"])} — '
            f'{e(hchange(h) or (t["founding"] + f" ({sup+con+oth} " + t["claims_word"] + ")"))} · '
            + (f'<a href="{prefix}/q/{qid}/v{h["version"]}.html">{t["view_ver"]}</a>'
               if h.get("version") in archived else f'<span class="muted">{t["ver_noarch"]}</span>')
            + '</li>' for h in hist)
        verhist = f'<h2 id="vh">{t["verhist"]}</h2>\n  <ul class="verhist">{vh_items}</ul>'
        inner = f'''
  <h1 class="qtitle">{e(qtext)}</h1>
  {qtags_html}
  {phr_html}
  {bottom_html}
  {related_html}
  <div class="glance">
    <span class="glance-h">{t["exec_h"]}</span>
    <dl>
      <div class="g-row g-answer"><dt>{t["cur_answer"]}</dt><dd>{e(first_sentence(qans))}</dd></div>
      <div class="g-row"><dt>{t["k_state"]}</dt><dd><span class="badge st-{q['knowledge_state']}">{e(STATE.get(q['knowledge_state']))}</span> <span class="muted">· {t["confidence_l"]}:</span> {e(grade_sum)} <span class="muted">(GRADE) · {t["stability_l"]}:</span> {t["stab_"+stab_key]}{(" · " + t["contested"]) if contested else ""}</dd></div>
      <div class="g-row"><dt>{t["evidence_l"]}</dt><dd><a class="evlink sup" href="#ev-sup">{sup} {t["supporting"]}</a> · <a class="evlink con" href="#ev-con">{con} {t["contradicting"]}</a> · <a class="evlink oth" href="#ev-oth">{oth} {t["refctx"]}</a></dd></div>
      {f'<div class="g-row"><dt></dt><dd class="contra-caveat">⚠ {t["contra_none"]}</dd></div>' if con == 0 else ''}
      {g_verify}
      <div class="g-row"><dt>{t["limitation_l"]}</dt><dd>{e(first_sentence(qunc))}</dd></div>
      <div class="g-row"><dt>{t["recent_l"]}</dt><dd>{e(first_sentence(last_change, 160))} <span class="muted">· v{ver}</span></dd></div>
      {g_fresh}
      <div class="g-row"><dt>{t["last_upd"]}</dt><dd>{e(updated)} <span class="muted">· v{ver}</span></dd></div>
    </dl>
    <p class="gmeta">{t["created_l"]} {e(created)} · {t["hreview"]}: {t["not_rev"]}</p>
  </div>
  {outcomes_html}
  <div class="answer"><span class="alabel">{t["synthesis_h"]} · v{ver} <span class="amut">· {t["ai_compiled"]}</span></span><p>{e(qans)}</p><p class="answer-cap">{t["answer_cap"]}</p>{ai_prov}</div>
  <div class="whatsnew"><span class="wn-h">{t["whatsnew"]} v{ver}</span><p>{e(last_change)}</p></div>
  {fr_note}
  {tl_section}
  {ver_section}
  {cite_block}
  <h2 id="ev-sup">{t["sup_claims"]}</h2>
  <ul class="qclaims">{sup_li}</ul>
  <h2 id="ev-con">{t["con_claims"]}</h2>
  <ul class="qclaims">{con_li}</ul>
  {"<h2 id='ev-oth'>"+t["refctx_h"]+"</h2><ul class='qclaims'>"+oth_li+"</ul>" if oth_li else "<span id='ev-oth'></span>"}
  <h2>{t["major_unc"]}</h2>
  <p class="uncert">{e(qunc)}</p>
  {verhist}
  <h2>{t["keyrefs"]}</h2>
  <p class="refs">{refs_html}</p>
  <p class="backlink"><a href="{prefix}/questions.html">{t["allq"]}</a></p>'''

        desc = (qans or "")[:155]
        # CURRENT page (indexable)
        top_cur = f'<p class="qid mono">{e(qid)} · v{ver} ({t["current"]}) · <a href="/q/{qid}.json">{t["json"]}</a></p>'
        main = head(lang, f"{qtext} — SCR", desc, page_path, keywords=kw_meta) + f'<main class="qpage wrap">{top_cur}{inner}</main>' + foot(lang)
        open(os.path.join(out_root, "q", f"{qid}.html"), "w").write(main)
        # FROZEN snapshot of the CURRENT version (past versions stay frozen on disk; build never rewrites them)
        os.makedirs(os.path.join(out_root, "q", qid), exist_ok=True)
        banner = f'<div class="archived">{t["archived_banner"](ver, e(updated))} <a href="{prefix}/q/{qid}.html">{t["cur_ver_link"]}</a></div>'
        top_arc = f'<p class="qid mono">{e(qid)} · v{ver} ({t["archived"]}) · <a href="{prefix}/q/{qid}.html">{t["cur_ver_link"]}</a></p>'
        snap = head(lang, f"{qtext} — SCR {qid} v{ver} ({t['archived']})", desc, ver_path, robots="noindex,follow", keywords=kw_meta) + f'<main class="qpage wrap">{banner}{top_arc}{inner}</main>' + foot(lang)
        open(os.path.join(out_root, "q", qid, f"v{ver}.html"), "w").write(snap)

    # ---- index ----
    cbs = Counter(q["knowledge_state"] for q in Q["questions"])
    filters = "".join(f'<button class="fbtn" data-f="{k}">{STATE[k]} <span class="fct">{cbs.get(k,0)}</span></button>'
                      for k in ["established", "probable", "emerging", "speculative", "no_evidence"] if cbs.get(k))
    cards = []
    for q in Q["questions"]:
        sup, con, oth = counts(q.get("claims", [])); fr = freshness(q.get("claims", []))
        frtxt = f' · <span class="fresh">{fr["pct"]}% {t["fresh_short"]}</span>' if fr else ""
        tags = q.get("tags", []); kws = q.get("keywords", [])
        qtext_l = field(q, 'text', lang) or ''; qans_l = field(q, 'current_answer', lang) or ''
        phr = (q.get("phrasings_pt") if lang == "pt" else q.get("phrasings")) or []
        search_blob = " ".join([q['id'], qtext_l, qans_l] + tags + kws + phr + [tag_label(x, lang) for x in tags]).lower()
        chips = "".join(f'<span class="qc-tag" data-tag="{e(tg)}">{e(tag_label(tg, lang))}</span>' for tg in tags)
        cards.append(f'''<a class="qcard" href="{prefix}/q/{q['id']}.html" data-state="{q['knowledge_state']}" data-search="{e(search_blob)}">
  <div class="qc-head"><span class="qid mono">{e(q['id'])}</span><span class="badge st-{q['knowledge_state']}">{e(STATE.get(q['knowledge_state']))}</span></div>
  <h3>{e(qtext_l)}</h3>
  <p class="qc-ans">{e(qans_l[:160])}…</p>
  <div class="qc-tags">{chips}</div>
  <p class="qc-ev"><span class="sup">{sup} {t["supporting_n"]}</span> · <span class="con">{con} {t["contradicting_n"]}</span>{frtxt}</p>
</a>''')
    n = len(Q["questions"])
    idx = head(lang, t["idx_title"], t["idx_desc"](n), "/questions.html")
    idx += f'''
<section class="claims-hero wrap">
  <h1>{t["idx_h1"]}</h1>
  <p class="sub">{t["idx_sub"](n)}</p>
  <p class="verseal" title="{e(t["verify_note"])}">✓ {t["idx_verify"](GLOBAL_VERIFY)}</p>
  <div class="qsearch"><input id="qsearch" type="search" placeholder="{e(t["search_ph"])}" autocomplete="off" aria-label="{e(t["search_ph"])}"></div>
  <div class="filters"><button class="fbtn active" data-f="all">{t["all"]} <span class="fct">{n}</span></button>{filters}</div>
  <p class="qcount-line muted small"><span id="qcount">{n}</span> {t["results"]}</p>
</section>
<main class="claims-bg"><section class="wrap qgrid" id="qgrid">
{''.join(cards)}
</section>
<p class="noresults muted" id="noresults" style="display:none">{t["no_results"]}</p>
<nav class="pager" id="pager" data-prev="{e(t["prev"])}" data-next="{e(t["next"])}"></nav>
</main>'''
    idx += foot(lang) + '''
<script>
(function(){
  var PAGE=12;
  var grid=document.getElementById('qgrid');
  var cards=[].slice.call(grid.querySelectorAll('.qcard'));
  var inp=document.getElementById('qsearch');
  var cnt=document.getElementById('qcount');
  var nores=document.getElementById('noresults');
  var pager=document.getElementById('pager');
  var L_PREV=pager.getAttribute('data-prev'),L_NEXT=pager.getAttribute('data-next');
  var state='all',page=1;
  function matches(){
    var qv=(inp.value||'').trim().toLowerCase();
    return cards.filter(function(c){
      var okS=(state==='all'||c.getAttribute('data-state')===state);
      var okQ=(!qv||c.getAttribute('data-search').indexOf(qv)>=0);
      return okS&&okQ;
    });
  }
  function render(){
    var m=matches();
    cards.forEach(function(c){c.style.display='none';});
    var pages=Math.max(1,Math.ceil(m.length/PAGE));
    if(page>pages)page=pages;
    m.slice((page-1)*PAGE,page*PAGE).forEach(function(c){c.style.display='';});
    cnt.textContent=m.length;
    nores.style.display=m.length?'none':'';
    pager.innerHTML='';
    if(pages>1){
      var mk=function(label,p,dis,act){var b=document.createElement('button');b.textContent=label;b.className='pgbtn'+(act?' active':'');if(dis){b.disabled=true;}else{b.addEventListener('click',function(){page=p;render();window.scrollTo({top:0,behavior:'smooth'});});}pager.appendChild(b);};
      mk(L_PREV,page-1,page===1,false);
      for(var i=1;i<=pages;i++){(function(i){mk(String(i),i,false,i===page);})(i);}
      mk(L_NEXT,page+1,page===pages,false);
    }
  }
  document.querySelectorAll('.fbtn').forEach(function(b){b.addEventListener('click',function(){
    document.querySelectorAll('.fbtn').forEach(function(x){x.classList.remove('active');});b.classList.add('active');
    state=b.getAttribute('data-f');page=1;render();});});
  inp.addEventListener('input',function(){page=1;render();});
  document.querySelectorAll('.qc-tag').forEach(function(tg){tg.addEventListener('click',function(ev){
    ev.preventDefault();ev.stopPropagation();inp.value=tg.getAttribute('data-tag');state='all';
    document.querySelectorAll('.fbtn').forEach(function(x){x.classList.remove('active');});
    var allb=document.querySelector('.fbtn[data-f="all"]');if(allb){allb.classList.add('active');}
    page=1;render();window.scrollTo({top:0,behavior:'smooth'});});});
  var prm=new URLSearchParams(location.search),tg=prm.get('tag'),qq=prm.get('q');
  if(tg){inp.value=tg;}else if(qq){inp.value=qq;}
  render();
})();
</script>'''
    open(os.path.join(out_root, "questions.html"), "w").write(idx)

for lang in ("en", "pt"):
    build_lang(lang)

# ---- sitemap (current pages only; both languages, with hreflang) ----
paths = (["/", "/questions.html", "/claims.html"]
         + [f"/q/{q['id']}.html" for q in Q["questions"]]
         + [f"/c/{cid}.html" for cid in C])
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for p in paths:
    for pre in ("", "/pt"):
        sm.append(f'  <url><loc>{BASE}{pre}{p}</loc><lastmod>{DATE}</lastmod>'
                  f'<xhtml:link rel="alternate" hreflang="en" href="{BASE}{p}"/>'
                  f'<xhtml:link rel="alternate" hreflang="pt-BR" href="{BASE}/pt{p}"/></url>')
sm.append('</urlset>')
open(os.path.join(SITE, "sitemap.xml"), "w").write("\n".join(sm) + "\n")

# ---- static read-API (machine-first; EN canonical with PT fields included) ----
os.makedirs(os.path.join(SITE, "api"), exist_ok=True)
api_q = {"registry": "SQ-LIP", "generated": DATE, "count": len(Q["questions"]),
         "evidence_verification": GLOBAL_VERIFY,
         "questions": [{"id": q["id"], "question": q["text"], "question_pt": q.get("text_pt"),
                        "phrasings": q.get("phrasings", []), "phrasings_pt": q.get("phrasings_pt", []),
                        "knowledge_state": q["knowledge_state"], "tags": q.get("tags", []), "keywords": q.get("keywords", []),
                        "bottom_line": q.get("bottom_line"),
                        "version": q.get("version", CUR_VER), "updated": q.get("updated", DATE),
                        "compiled_by": q.get("compiled_by"), "outcomes": q.get("outcomes") or [],
                        "evidence_direction": dict(zip(["supporting", "contradicting", "other"], counts(q.get("claims", [])))),
                        "knowledge_freshness": freshness(q.get("claims", [])),
                        "evidence_verification": verification_rollup(q.get("claims", [])),
                        "html": f"{BASE}/q/{q['id']}.html", "html_pt": f"{BASE}/pt/q/{q['id']}.html",
                        "json": f"{BASE}/q/{q['id']}.json"} for q in Q["questions"]]}
json.dump(api_q, open(os.path.join(SITE, "api", "questions.json"), "w"), ensure_ascii=False, indent=2)
json.dump({"registry": "SCR-LIP", "generated": DATE, "count": len(C), "claims": list(C.values())},
          open(os.path.join(SITE, "api", "claims.json"), "w"), ensure_ascii=False, indent=2)
try:
    json.dump(json.load(open(os.path.join(REG, "domains.json"))),
              open(os.path.join(SITE, "api", "domains.json"), "w"), ensure_ascii=False, indent=2)
except FileNotFoundError:
    pass
json.dump({"name": "Scientific Claim Registry API", "version": "0.1", "license": "CC-BY-4.0",
           "languages": ["en", "pt-BR"],
           "positioning": "A versioned memory of how scientific answers evolve.",
           "endpoints": {"questions": f"{BASE}/api/questions.json", "question": f"{BASE}/q/{{id}}.json",
                         "claims": f"{BASE}/api/claims.json", "domains": f"{BASE}/api/domains.json",
                         "sitemap": f"{BASE}/sitemap.xml"},
           "note": "Static, cacheable, CC-BY-4.0. Each question is an evidence-bounded, versioned answer. Not medical advice."},
          open(os.path.join(SITE, "api", "index.json"), "w"), ensure_ascii=False, indent=2)

print(f"Generated EN + PT: questions.html + {len(Q['questions'])} questions ×2 (current+snapshot) + JSON + sitemap (hreflang) + API.")
