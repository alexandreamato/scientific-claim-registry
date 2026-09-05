#!/usr/bin/env python3
"""Generate the homepage hero CARD for the featured question (R-OBJ-6) so the volatile facts never
drift. HYBRID: live metadata (version, knowledge state, first-mention year) is pulled from the real
question; the polished prose (answer summary + historical ladder labels) is CURATED in CARD_COPY so
the homepage stays clean. If the live version moves past the curated ladder, it WARNS to refresh copy.
Injects between <!--HERO-->…<!--/HERO--> markers in index.html (EN) and pt/index.html (PT).
Run after build_questions.py, before deploy:  python3 build_home.py
"""
import json, os, re, html, sys

import hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "..", "registry")
FEATURED = "SQ-LIP-000012"
CSSVER = hashlib.md5(open(os.path.join(HERE, "style.css"), "rb").read()).hexdigest()[:8]  # cache-bust CSS

# Curated, polished prose for the featured question. Update ONLY when the answer materially changes.
# `hist` = stable historical ladder steps; the CURRENT step is generated live (version + state).
CARD_COPY = {
    "SQ-LIP-000012": {
        "en": {"answer": "Probably both — though the evidence remains predominantly low-to-moderate quality.",
               "hist": [("1.1", "formalized the hormonal hypotheses (onset at puberty, pregnancy, menopause)"),
                        ("1.3", "added genetic evidence: multiple GWAS, including UK&nbsp;Biobank loci")],
               "current": "current synthesis: hormones <em>and</em> heredity"},
        "pt": {"answer": "Provavelmente ambos — embora a evidência ainda seja predominantemente de qualidade baixa a moderada.",
               "hist": [("1.1", "formalizou as hipóteses hormonais (início na puberdade, gravidez, menopausa)"),
                        ("1.3", "acrescentou evidência genética: múltiplos GWAS, incluindo loci do UK&nbsp;Biobank")],
               "current": "síntese atual: hormônios <em>e</em> hereditariedade"},
    },
}

STATE = {"en": {"speculative": "Speculative", "emerging": "Emerging", "probable": "Probable",
                "established": "Established", "foundational": "Foundational", "no_evidence": "No evidence"},
         "pt": {"speculative": "Especulativo", "emerging": "Emergente", "probable": "Provável",
                "established": "Estabelecido", "foundational": "Fundacional", "no_evidence": "Sem evidência"}}
T = {"en": {"live": "● live question", "ans": "Answer", "synth": "a synthesis, not a verdict",
            "kstate": "Knowledge state", "first": "First described", "aver": "Answer version",
            "evolved": "How the answer evolved", "graded": "graded", "cta": "Open this question · see every version →"},
     "pt": {"live": "● pergunta viva", "ans": "Resposta", "synth": "uma síntese, não um veredito",
            "kstate": "Estado do conhecimento", "first": "Descrito pela 1ª vez", "aver": "Versão da resposta",
            "evolved": "Como a resposta evoluiu", "graded": "grau", "cta": "Abrir esta pergunta · ver todas as versões →"}}
e = lambda s: html.escape(str(s if s is not None else ""))


def card(q, lang):
    t = T[lang]; prefix = "" if lang == "en" else "/pt"
    copy = CARD_COPY[q["id"]][lang]
    qid = q["id"]; ver = q.get("version", "1.0")
    text = q.get("text_pt" if lang == "pt" else "text")
    state = STATE[lang].get(q.get("knowledge_state"), q.get("knowledge_state"))
    fm = (q.get("first_mention") or {}).get("year", "—")
    # ladder: curated historical steps + a LIVE current step (version + state)
    steps = list(copy["hist"]) + [(ver, f'{copy["current"]}, {t["graded"]} {e(state)}')]
    if _cmp_ver(ver, copy["hist"][-1][0]) <= 0:
        print(f"  ⚠ hero copy may be stale: live v{ver} ≤ curated ladder v{copy['hist'][-1][0]} — refresh CARD_COPY")
    lad = "".join(f"<li><b>v{e(v)}</b> — {c}</li>" for v, c in steps)  # curated c is trusted HTML
    return (f'<!--HERO-->\n  <a class="qfeat" href="{prefix}/q/{qid}.html">\n'
            f'    <div class="qf-top"><span class="mono qf-id">{e(qid)}</span><span class="qf-live">{t["live"]}</span></div>\n'
            f'    <h2 class="qf-q">{e(text)}</h2>\n'
            f'    <p class="qf-a"><span class="qf-lbl">{t["ans"]} · v{e(ver)} — {t["synth"]}</span> {e(copy["answer"])}</p>\n'
            f'    <div class="qf-meta"><span><b>{t["kstate"]}</b> · {e(state)}</span>'
            f'<span><b>{t["first"]}</b> · {e(fm)}</span><span><b>{t["aver"]}</b> · v{e(ver)}</span></div>\n'
            f'    <div class="qf-ladder"><span class="qf-lbl">{t["evolved"]}</span><ol>{lad}</ol></div>\n'
            f'    <span class="qf-cta">{t["cta"]}</span>\n  </a>\n  <!--/HERO-->')


def _cmp_ver(a, b):
    pa = [int(x) for x in str(a).split(".")]; pb = [int(x) for x in str(b).split(".")]
    return (pa > pb) - (pa < pb)


def global_verify():
    """Registry-wide verification rollup (R-AI-14) from claims.json — verified/disputed/total evidence."""
    claims = json.load(open(os.path.join(REG, "claims.json")))["claims"]
    vd = [(ev.get("verification") or {}).get("verdict") or "unverified"
          for c in claims for ev in c.get("evidence", [])]
    return {"verified": vd.count("verified"), "disputed": vd.count("disputed"), "total": len(vd)}

_VSEAL = {
    "en": lambda g: (f'<!--VERSEAL--><p class="verseal" title="Each evidence source is independently '
        f're-read by a second AI model that must confirm its stance and a verbatim quote from the source '
        f'(R-AI-13/14).">✓ <strong>{g["verified"]} of {g["total"]}</strong> evidence sources independently '
        f'AI-verified · {g["disputed"]} disputed</p><!--/VERSEAL-->'),
    "pt": lambda g: (f'<!--VERSEAL--><p class="verseal" title="Cada fonte de evidência é relida por um '
        f'segundo modelo de IA, que precisa confirmar o stance e uma citação verbatim da fonte '
        f'(R-AI-13/14).">✓ <strong>{g["verified"]} de {g["total"]}</strong> fontes de evidência verificadas '
        f'de forma independente por IA · {g["disputed"]} em revisão</p><!--/VERSEAL-->'),
}


def inject(path, html_card, vseal=None):
    src = open(path).read()
    if "<!--HERO-->" not in src:
        sys.exit(f"no <!--HERO--> markers in {path}")
    src = re.sub(r"<!--HERO-->.*?<!--/HERO-->", lambda _: html_card, src, flags=re.S)
    if vseal and "<!--VERSEAL-->" in src:
        src = re.sub(r"<!--VERSEAL-->.*?<!--/VERSEAL-->", lambda _: vseal, src, flags=re.S)
    # cache-bust the stylesheet link (static index files), keeping the relative path (style.css / ../style.css)
    src = re.sub(r'href="((?:\.\./)?style\.css)(\?v=[0-9a-f]+)?"', rf'href="\1?v={CSSVER}"', src)
    open(path, "w").write(src)
    print(f"hero injected (+css v{CSSVER}) → {path}")


def main():
    qs = json.load(open(os.path.join(REG, "questions.json")))["questions"]
    q = next(x for x in qs if x["id"] == FEATURED)
    gv = global_verify()
    inject(os.path.join(HERE, "index.html"), card(q, "en"), _VSEAL["en"](gv))
    inject(os.path.join(HERE, "pt", "index.html"), card(q, "pt"), _VSEAL["pt"](gv))


if __name__ == "__main__":
    main()
