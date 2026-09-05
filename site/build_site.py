#!/usr/bin/env python3
"""Generate claims.html (EN, root) and pt/claims.html (PT), filterable, from the registry.
Run from the site/ folder (or anywhere): python3 build_site.py
Reads ../registry/claims.json. sitemap.xml is owned by build_questions.py."""
import json, os, html, hashlib
from collections import Counter
from scrlib import timeline_svg, ref_link, ref_url, ev_label, cite_link, ANALYTICS
SITE = os.path.dirname(os.path.abspath(__file__))
CSSVER = hashlib.md5(open(os.path.join(SITE, "style.css"), "rb").read()).hexdigest()[:8]  # cache-bust CSS
BASE = "https://scientificclaims.org"
REG = os.path.join(SITE, "..", "registry")
data = json.load(open(os.path.join(REG, "claims.json")))
claims = data["claims"]
def e(s): return html.escape(str(s if s is not None else ""))
counts = Counter(c["knowledge_state"] for c in claims)

# claim -> questions it answers (the graph back-link)
QUESTIONS = json.load(open(os.path.join(REG, "questions.json")))["questions"]
claim_questions = {}
for _q in QUESTIONS:
    for _l in _q.get("claims", []):
        claim_questions.setdefault(_l["id"], []).append(
            {"id": _q["id"], "text": _q["text"], "text_pt": _q.get("text_pt"), "role": _l["role"]})

STATE_L = {
  "en": {"speculative":"Speculative","emerging":"Emerging","probable":"Probable","established":"Established","foundational":"Foundational","no_evidence":"Evidence gap"},
  "pt": {"speculative":"Especulativo","emerging":"Emergente","probable":"Provável","established":"Estabelecido","foundational":"Fundacional","no_evidence":"Lacuna de evidência"},
}
GRADE_L = {
  "en": {"high":"high","moderate":"moderate","low":"low","very_low":"very low"},
  "pt": {"high":"alta","moderate":"moderada","low":"baixa","very_low":"muito baixa"},
}
CTYPE_L = {
  "en": {},
  "pt": {"definitional":"definicional","diagnostic":"diagnóstico","causal":"causal",
         "clinical_association":"associação clínica","epidemiologic":"epidemiológico",
         "therapeutic":"terapêutico","prognostic":"prognóstico","historical":"histórico"},
}
def grade_label(g, lang): return GRADE_L[lang].get(g, (g or "").replace("_", " "))
def ctype_label(ct, lang): return CTYPE_L[lang].get(ct, (ct or "").replace("_", " "))
ROLE_L = {
  "en": {"supporting":"consistent","contradicting":"conflicting","refines":"refining","context":"contextual"},
  "pt": {"supporting":"consistente","contradicting":"conflitante","refines":"refina","context":"contextual"},
}
PECO_L = {
  "en": {"population":"Population","condition":"Condition","exposure":"Exposure","comparator":"Comparator","outcome":"Outcome","scope":"Scope"},
  "pt": {"population":"População","condition":"Condição","exposure":"Exposição","comparator":"Comparador","outcome":"Desfecho","scope":"Escopo"},
}
T = {
 "en": {"nav_q":"Questions","nav_c":"Claims","lang":"PT","lang_href":"/pt/claims.html",
        "h1":"All claims",
        "sub":f"The {len(claims)} evidence claims of the lipedema pilot registry. Each is an addressable object with an evidence-certainty rating (GRADE), a knowledge state, and explicit gaps. Consensus is tracked separately and added over time.",
        "all":"All","certainty":"Evidence certainty","sources":"source(s)","by_amato":"by Amato",
        "gaps":"Gaps:","foot_op":"Operated by BIO — Biological Intelligence Observatory.",
        "foot_dis":"Claims do not replace clinical judgment.","stmt":"statement",
        "search_ph":"Search claims by text, ID or type…","no_results":"No claims match your search.",
        "prev":"‹ Prev","next":"Next ›","results":"results",
        "claim_word":"Claim","json_link":"machine-readable JSON →","evidence_h":"Evidence",
        "context_h":"Context (PECO)","gaps_h":"Gaps & caveats","answers":"Answers these questions",
        "no_q":"Not yet linked to a question.","back_claims":"← All claims","ev_time":"Evidence over time",
        "rob":"risk of bias","auto_note":"Auto-compiled by the Layer 1 surveillance loop; not yet human-reviewed.",
        "v_verified":"verified","v_disputed":"needs review","v_unverified":"unverified",
        "v_title_ok":"Stance and quote independently confirmed by a second model.",
        "v_title_bad":"A second model could not confirm the stance or the quote — treat as provisional.",
        "extr_l":"reading confidence",
        "integ_warn":"Statement integrity: an independent model found specifics in this statement that appear in none of the cited sources — pending review:",
        "created_l":"Created","updated_l":"Last updated","log_h":"Change log",
        "glance_h":"Claim at a glance","type_l":"Type","kstate_l":"Knowledge state","answers_l":"Answers",
        "questions_w":"question(s)","dates_l":"Dates",
        "claim_cap":"Structured evidence, machine-compiled — not a verdict."},
 "pt": {"nav_q":"Perguntas","nav_c":"Claims","lang":"EN","lang_href":"/claims.html",
        "h1":"Todos os claims",
        "sub":f"Os {len(claims)} claims de evidência do registro-piloto de lipedema. Cada um é um objeto endereçável com certeza da evidência (GRADE), um estado do conhecimento e lacunas explícitas. O consenso é rastreado à parte e adicionado ao longo do tempo.",
        "all":"Todos","certainty":"Certeza da evidência","sources":"fonte(s)","by_amato":"de Amato",
        "gaps":"Lacunas:","foot_op":"Operado pelo BIO — Biological Intelligence Observatory.",
        "foot_dis":"Claims não substituem o julgamento clínico.","stmt":"statement_pt",
        "search_ph":"Buscar claims por texto, ID ou tipo…","no_results":"Nenhum claim corresponde à busca.",
        "prev":"‹ Anterior","next":"Próximo ›","results":"resultados",
        "claim_word":"Claim","json_link":"JSON legível por máquina →","evidence_h":"Evidência",
        "context_h":"Contexto (PECO)","gaps_h":"Lacunas e ressalvas","answers":"Responde a estas perguntas",
        "no_q":"Ainda não ligado a uma pergunta.","back_claims":"← Todos os claims","ev_time":"Evidência ao longo do tempo",
        "rob":"risco de viés","auto_note":"Compilado automaticamente pelo loop de vigilância da Layer 1; ainda não revisado por humano.",
        "v_verified":"verificado","v_disputed":"requer revisão","v_unverified":"não verificado",
        "v_title_ok":"Stance e citação confirmados de forma independente por um segundo modelo.",
        "v_title_bad":"Um segundo modelo não confirmou o stance ou a citação — tratar como provisório.",
        "extr_l":"confiança da leitura",
        "integ_warn":"Integridade do statement: um modelo independente encontrou especificidades neste statement ausentes de todas as fontes citadas — pendente de revisão:",
        "created_l":"Criado","updated_l":"Última atualização","log_h":"Histórico de mudanças",
        "glance_h":"Claim em resumo","type_l":"Tipo","kstate_l":"Estado do conhecimento","answers_l":"Responde a",
        "questions_w":"pergunta(s)","dates_l":"Datas",
        "claim_cap":"Evidência estruturada, compilada por máquina — não é um veredito."},
}

def render(lang):
    t = T[lang]; STATE = STATE_L[lang]; prefix = "/pt" if lang == "pt" else ""
    htmllang = "pt-BR" if lang == "pt" else "en"
    rows = []
    for c in claims:
        evs = c["evidence"]; amato = sum(1 for x in evs if x.get("amato_authored"))
        refs = " · ".join(cite_link(x) for x in evs)
        amato_txt = f" · {amato} {t['by_amato']}" if amato else ""
        tl = timeline_svg([{"year": x.get("year"), "kind": x.get("stance"), "label": ev_label(x), "url": ref_url(x.get("ref"))} for x in evs], w=560, h=44)
        tl_html = f'<div class="cr-tl">{tl}</div>' if tl else ''
        stmt = c.get(t["stmt"]) or c.get("statement")
        blob = " ".join([c['id'], stmt or '', c['claim_type'].replace('_', ' '), c.get('gaps', '') or '',
                         " ".join(x.get("ref", "") for x in evs)]).lower()
        rows.append(f'''<article class="claim-row" data-state="{c['knowledge_state']}" data-search="{e(blob)}">
  <div class="cr-head"><a class="mono id" href="{prefix}/c/{c['id']}.html">{e(c['id'])}</a><span class="chip">{e(ctype_label(c['claim_type'], lang))}</span><span class="badge st-{c['knowledge_state']}">{e(STATE.get(c['knowledge_state']))}</span></div>
  {tl_html}
  <p class="cr-text">{e(stmt)}</p>
  <div class="cr-meta"><span>{t["certainty"]}</span>: <strong>{e(grade_label(c['evidence_confidence'], lang))}</strong> (GRADE) · <span>{len(evs)} {t["sources"]}{amato_txt}</span></div>
  <p class="cr-evi mono">{refs}</p>
  <p class="cr-gap"><strong>{t["gaps"]}</strong> {e(c['gaps'])}</p>
</article>''')
    filters = "".join(
        f'<button class="fbtn" data-f="{k}">{e(STATE[k])} <span class="fct">{counts.get(k,0)}</span></button>'
        for k in ["established", "probable", "emerging", "speculative", "no_evidence"] if counts.get(k))
    canon = f"{BASE}{prefix}/claims.html"
    page = f'''<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{("Os claims" if lang=="pt" else "The Claims")} — Scientific Claim Registry (SCR)</title>
<meta name="description" content="{e(t['sub'])[:155]}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en" href="{BASE}/claims.html">
<link rel="alternate" hreflang="pt-BR" href="{BASE}/pt/claims.html">
<link rel="alternate" hreflang="x-default" href="{BASE}/claims.html">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:title" content="{e(t['h1'])} — Scientific Claim Registry">
<meta property="og:description" content="{e(t['sub'])[:155]}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/style.css?v={CSSVER}">
{ANALYTICS}
</head>
<body>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{prefix}/"><span class="mono">SCR</span> <span class="brand-full">Scientific Claim Registry</span></a>
    <nav>
      <a href="{prefix}/questions.html">{t["nav_q"]}</a>
      <a href="{prefix}/claims.html" class="active">{t["nav_c"]}</a>
      <a class="lang" href="{t["lang_href"]}">{t["lang"]}</a>
    </nav>
  </div>
</header>

<section class="claims-hero wrap">
  <h1>{t["h1"]}</h1>
  <p class="sub">{e(t["sub"])}</p>
  <div class="qsearch"><input id="csearch" type="search" placeholder="{e(t["search_ph"])}" autocomplete="off" aria-label="{e(t["search_ph"])}"></div>
  <div class="filters">
    <button class="fbtn active" data-f="all">{t["all"]} <span class="fct">{len(claims)}</span></button>
    {filters}
  </div>
  <p class="qcount-line muted small"><span id="ccount">{len(claims)}</span> {t["results"]}</p>
</section>

<main class="claims-bg"><section class="wrap claims-list" id="clist">
{''.join(rows)}
</section>
<p class="noresults muted" id="cnoresults" style="display:none">{t["no_results"]}</p>
<nav class="pager" id="cpager" data-prev="{e(t["prev"])}" data-next="{e(t["next"])}"></nav>
</main>

<footer class="site">
  <div class="wrap foot">
    <div><p class="brand"><span class="mono">SCR</span> Scientific Claim Registry</p>
    <p class="muted">{t["foot_op"]}</p></div>
    <div class="muted small"><p>CC BY 4.0 · DOI <a href="https://doi.org/10.5281/zenodo.20466195" rel="noopener">10.5281/zenodo.20466195</a></p>
    <p>{t["foot_dis"]}</p></div>
  </div>
</footer>

<script>
(function(){{
  var PAGE=15;
  var list=document.getElementById('clist');
  var rows=[].slice.call(list.querySelectorAll('.claim-row'));
  var inp=document.getElementById('csearch');
  var cnt=document.getElementById('ccount');
  var nores=document.getElementById('cnoresults');
  var pager=document.getElementById('cpager');
  var L_PREV=pager.getAttribute('data-prev'),L_NEXT=pager.getAttribute('data-next');
  var state='all',page=1;
  function matches(){{
    var qv=(inp.value||'').trim().toLowerCase();
    return rows.filter(function(r){{
      var okS=(state==='all'||r.getAttribute('data-state')===state);
      var okQ=(!qv||r.getAttribute('data-search').indexOf(qv)>=0);
      return okS&&okQ;
    }});
  }}
  function render(){{
    var m=matches();
    rows.forEach(function(r){{r.style.display='none';}});
    var pages=Math.max(1,Math.ceil(m.length/PAGE));
    if(page>pages)page=pages;
    m.slice((page-1)*PAGE,page*PAGE).forEach(function(r){{r.style.display='';}});
    cnt.textContent=m.length;
    nores.style.display=m.length?'none':'';
    pager.innerHTML='';
    if(pages>1){{
      var mk=function(label,p,dis,act){{var b=document.createElement('button');b.textContent=label;b.className='pgbtn'+(act?' active':'');if(dis){{b.disabled=true;}}else{{b.addEventListener('click',function(){{page=p;render();window.scrollTo({{top:0,behavior:'smooth'}});}});}}pager.appendChild(b);}};
      mk(L_PREV,page-1,page===1,false);
      for(var i=1;i<=pages;i++){{(function(i){{mk(String(i),i,false,i===page);}})(i);}}
      mk(L_NEXT,page+1,page===pages,false);
    }}
  }}
  document.querySelectorAll('.fbtn').forEach(function(b){{b.addEventListener('click',function(){{
    document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active');}});b.classList.add('active');
    state=b.getAttribute('data-f');page=1;render();}});}});
  inp.addEventListener('input',function(){{page=1;render();}});
  render();
}})();
</script>
</body>
</html>'''
    out = os.path.join(SITE, "pt", "claims.html") if lang == "pt" else os.path.join(SITE, "claims.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(page)

def shell(lang, title, desc, page_path, body):
    t = T[lang]; prefix = "/pt" if lang == "pt" else ""
    htmllang = "pt-BR" if lang == "pt" else "en"
    lang_href = ("" if lang == "pt" else "/pt") + page_path
    return f'''<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{prefix}{page_path}">
<link rel="alternate" hreflang="en" href="{BASE}{page_path}">
<link rel="alternate" hreflang="pt-BR" href="{BASE}/pt{page_path}">
<link rel="alternate" hreflang="x-default" href="{BASE}{page_path}">
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
<header class="site"><div class="wrap nav">
  <a class="brand" href="{prefix}/"><span class="mono">SCR</span> <span class="brand-full">Scientific Claim Registry</span></a>
  <nav><a href="{prefix}/questions.html">{t["nav_q"]}</a><a href="{prefix}/claims.html" class="active">{t["nav_c"]}</a><a class="lang" href="{lang_href}">{t["lang"]}</a></nav>
</div></header>
{body}
<footer class="site"><div class="wrap foot">
  <div><p class="brand"><span class="mono">SCR</span> Scientific Claim Registry</p><p class="muted">{t["foot_op"]}</p></div>
  <div class="muted small"><p>CC BY 4.0 · DOI <a href="https://doi.org/10.5281/zenodo.20466195" rel="noopener">10.5281/zenodo.20466195</a></p><p>{t["foot_dis"]}</p></div>
</div></footer>
</body>
</html>'''

def render_claim(c, lang):
    t = T[lang]; STATE = STATE_L[lang]; prefix = "/pt" if lang == "pt" else ""
    cid = c["id"]; stmt = c.get(t["stmt"]) or c.get("statement")
    evs = c["evidence"]
    amato_txt = (" · " + t["by_amato"]) if any(x.get("amato_authored") for x in evs) else ""
    tl = timeline_svg([{"year": x.get("year"), "kind": x.get("stance"), "label": ev_label(x), "url": ref_url(x.get("ref"))} for x in evs], w=680, h=56)
    ev_items = ""
    for x in evs:
        meta = " · ".join(p for p in [
            ROLE_L[lang].get(x.get("stance"), x.get("stance")),
            (x.get("study_design") or "").replace("_", " ") or None,
            (f'n={x["n"]}' if x.get("n") else None),
            (str(x["year"]) if x.get("year") else None),
            (f'{t["rob"]}: {x["risk_of_bias"]}' if x.get("risk_of_bias") and x["risk_of_bias"] != "unknown" else None),
        ] if p)
        note = f'<br><span class="muted small">{e(x.get("note"))}</span>' if x.get("note") else ""
        # R-AI-14 — verification badge (verified / needs review / unverified) per evidence item.
        vd = (x.get("verification") or {}).get("verdict")
        if vd == "verified":
            badge = f'<span class="vbadge v-ok" title="{e(t["v_title_ok"])}">✓ {t["v_verified"]}</span>'
        elif vd == "disputed":
            badge = f'<span class="vbadge v-bad" title="{e(t["v_title_bad"])}">⚠ {t["v_disputed"]}</span>'
        elif vd == "unverified" or vd is None:
            badge = f'<span class="vbadge v-na">{t["v_unverified"]}</span>'
        else:
            badge = ""
        # R-AI-13 — sentence-level provenance: show the quote ONLY when it was deterministically grounded
        # (an exact span of the source), so a displayed quote is always a true verbatim guarantee.
        _grnd = (x.get("verification") or {}).get("quote_grounded")
        quote = f'<br><span class="evquote">“{e(x.get("quote"))}”</span>' if (x.get("quote") and _grnd) else ""
        ec = x.get("extraction_confidence")
        ec_html = f' <span class="muted small">· {t["extr_l"]}: {e(ec)}</span>' if ec else ""
        ev_items += (f'<li>{cite_link(x)} {badge} <span class="muted small">— {e(meta)}</span>'
                     f'{ec_html}{quote}{note}</li>')
    ql = claim_questions.get(cid, [])
    if ql:
        q_items = "".join(
            f'<li><a href="{prefix}/q/{q["id"]}.html">{e(q["text_pt"] if (lang=="pt" and q.get("text_pt")) else q["text"])}</a> '
            f'<span class="role role-{q["role"]}">{ROLE_L[lang].get(q["role"], q["role"])}</span></li>' for q in ql)
    else:
        q_items = f'<li class="muted">{t["no_q"]}</li>'
    ctx = c.get("context") or {}
    peco = "".join(f'<div><span class="mk">{PECO_L[lang].get(k, k)}</span><span>{e(v)}</span></div>'
                   for k, v in ctx.items() if v and v != "—")
    prov = c.get("provenance")
    prov_html = (f'<p class="frnote">{t["auto_note"]} <span class="mono small">{e(prov.get("engine"))} · {e(prov.get("ingested"))}</span></p>'
                 if prov and prov.get("auto") else "")
    created = c.get("created", ""); updated = c.get("updated", "")
    # R-AI-14 (per-claim altitude) — flag a statement whose specifics appear in none of its sources.
    integ = c.get("statement_integrity") or {}
    integ_html = ""
    if integ.get("fabricated") and integ.get("invented"):
        items = ", ".join(f'“{e(x)}”' for x in integ["invented"][:6])
        integ_html = f'<p class="frnote integ-warn">⚠ {t["integ_warn"]} {items}</p>'
    log = c.get("history") or []
    log_html = "".join(f'<li><span class="mono">{e(h.get("date"))}</span> — {e(h.get("event"))}'
                       f'{(" · " + e(h.get("detail"))) if h.get("detail") else ""}</li>' for h in log)
    body = f'''<main class="qpage wrap">
  <p class="qid mono">{e(cid)} · {t["claim_word"]} · <a href="/c/{cid}.json">{t["json_link"]}</a></p>
  <h1 class="qtitle">{e(stmt)}</h1>
  {integ_html}
  <div class="glance">
    <span class="glance-h">{t["glance_h"]}</span>
    <dl>
      <div class="g-row"><dt>{t["type_l"]}</dt><dd>{e(ctype_label(c["claim_type"], lang))}</dd></div>
      <div class="g-row"><dt>{t["kstate_l"]}</dt><dd><span class="badge st-{c["knowledge_state"]}">{e(STATE.get(c["knowledge_state"]))}</span></dd></div>
      <div class="g-row"><dt>{t["certainty"]}</dt><dd>{e(grade_label(c["evidence_confidence"], lang))} <span class="muted">(GRADE)</span></dd></div>
      <div class="g-row"><dt>{t["evidence_h"]}</dt><dd>{len(evs)} {t["sources"]}{amato_txt}</dd></div>
      <div class="g-row"><dt>{t["answers_l"]}</dt><dd><a class="evlink" href="#answers">{len(ql)} {t["questions_w"]}</a></dd></div>
      <div class="g-row"><dt>{t["dates_l"]}</dt><dd>{e(created)} <span class="muted">→ {e(updated)}</span></dd></div>
    </dl>
    <p class="answer-cap">{t["claim_cap"]}</p>
  </div>
  {prov_html}
  {f'<h2>{t["ev_time"]}</h2><div class="qtl">{tl}</div>' if tl else ''}
  <h2>{t["evidence_h"]} ({len(evs)})</h2>
  <ul class="qclaims">{ev_items}</ul>
  {f'<h2>{t["context_h"]}</h2><div class="qmeta">{peco}</div>' if peco else ''}
  <h2 id="answers">{t["answers"]}</h2>
  <ul class="qclaims">{q_items}</ul>
  <h2>{t["gaps_h"]}</h2>
  <p class="uncert">{e(c.get("gaps"))}</p>
  {f'<h2>{t["log_h"]}</h2><ul class="verhist">{log_html}</ul>' if log_html else ''}
  <p class="backlink"><a href="{prefix}/claims.html">{t["back_claims"]}</a></p>
</main>'''
    out = shell(lang, f'{(stmt or "")[:70]} — SCR {cid}', (stmt or "")[:155], f"/c/{cid}.html", body)
    d = os.path.join(SITE, "pt", "c") if lang == "pt" else os.path.join(SITE, "c")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, f"{cid}.html"), "w").write(out)

def claim_json(c):
    ql = claim_questions.get(c["id"], [])
    obj = dict(c)
    obj["answers_questions"] = [{"id": q["id"], "role": q["role"], "question": q["text"],
                                 "url": f"{BASE}/q/{q['id']}.html"} for q in ql]
    obj["url"] = f"{BASE}/c/{c['id']}.html"; obj["license"] = "CC-BY-4.0"
    os.makedirs(os.path.join(SITE, "c"), exist_ok=True)
    json.dump(obj, open(os.path.join(SITE, "c", f"{c['id']}.json"), "w"), ensure_ascii=False, indent=2)

for lang in ("en", "pt"):
    render(lang)
    for c in claims:
        render_claim(c, lang)
for c in claims:
    claim_json(c)

# Prune orphan claim pages/JSON left from removed (banned/merged) claims, so the site never drifts.
import glob
_ids = {c["id"] for c in claims}
_pruned = 0
for _pat in ("c/SCR-*.html", "pt/c/SCR-*.html", "c/SCR-*.json", "pt/c/SCR-*.json"):
    for _f in glob.glob(os.path.join(SITE, _pat)):
        if os.path.basename(_f).rsplit(".", 1)[0] not in _ids:
            os.remove(_f); _pruned += 1
print(f"Generated claims.html + pt/claims.html + {len(claims)} claim pages ×2 + JSON. "
      f"Pruned {_pruned} orphan file(s). States: {dict(counts)}")
