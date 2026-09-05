"""Shared build helpers for the SCR site (imported by build_site.py / build_questions.py).
Not deployed (excluded as *.py)."""
from collections import defaultdict
import html as _html
import re as _re


def ref_url(ref):
    """Resolve a reference string to a direct article URL. DOI:/PMID: → resolver URL;
    bibliographic strings (pre-MEDLINE, no identifier) → None."""
    if not ref:
        return None
    r = str(ref).strip()
    up = r.upper()
    if up.startswith("DOI:"):
        return "https://doi.org/" + r[4:].strip()
    if up.startswith("PMID:"):
        return "https://pubmed.ncbi.nlm.nih.gov/" + r[5:].strip().rstrip("/") + "/"
    return None


def ref_link(ref):
    """Render a reference as a clickable link to the source article when it has a DOI/PMID.
    Otherwise return the escaped citation text — but NEVER expose a raw local filename
    (e.g. 'Amato_2019_….pdf'): collapse it to a clean 'Surname YEAR' label."""
    r = str(ref if ref is not None else "")
    u = ref_url(ref)
    if u:
        return f'<a class="reflink" href="{_html.escape(u)}" target="_blank" rel="noopener">{_html.escape(r)}</a>'
    if r.lower().endswith((".pdf", ".docx", ".doc")) or (" " not in r and "_" in r):
        m = _re.match(r'([A-Za-z]+)[_-](\d{4})', r)
        return _html.escape(f"{m.group(1).title()} {m.group(2)}" if m else "source on file")
    return _html.escape(r)

def clean_text(s):
    """Strip JATS/HTML markup that leaks from Crossref/Europe PMC metadata (e.g. <scp>…</scp>,
    <i>, <sub>, <sup>) and collapse whitespace/newlines. Safe on None."""
    if not s:
        return s
    s = _re.sub(r"<[^>]+>", "", str(s))          # drop any <tag>
    s = _html.unescape(s)                          # &amp; etc. → real chars (re-escaped at output)
    return _re.sub(r"\s+", " ", s).strip()


def ev_label(ev):
    """Human-readable citation for an evidence entry (tooltips/labels): 'Title — Authors (Year)'.
    Falls back to the raw ref only when no title was enriched."""
    t = clean_text(ev.get("title"))
    if not t:
        return ev.get("ref") or ""
    s = t
    if ev.get("authors"): s += f" — {clean_text(ev['authors'])}"
    if ev.get("year"): s += f" ({ev['year']})"
    return s

def cite_link(ev):
    """Render an evidence entry as a human-readable citation linking to the source article."""
    label = ev_label(ev)
    u = ref_url(ev.get("ref"))
    if u:
        return f'<a class="reflink" href="{_html.escape(u)}" target="_blank" rel="noopener">{_html.escape(label)}</a>'
    return ref_link(ev.get("ref"))

# stance/role -> colour
KIND_COLOR = {
    "supporting": "#1d7a4f", "contradicting": "#a23b52", "mentioning": "#94a3b8",
    "refines": "#1f6a93", "context": "#94a3b8", "origin": "#0f1b2d",
}
# internal role key -> display label (data keys unchanged; only the wording shown to humans)
ROLE_LABEL = {
    "supporting": "consistent", "contradicting": "conflicting", "refines": "refining",
    "context": "contextual", "mentioning": "contextual", "origin": "origin",
}

def timeline_svg(items, w=620, h=48):
    """items: list of dicts {year:int, kind:str, label?:str}. Renders an inline SVG
    evidence timeline: a horizontal axis with one dot per item positioned by year,
    coloured by kind. Same-year items stack upward. Returns '' if no dated items."""
    yrs = [i["year"] for i in items if isinstance(i.get("year"), int)]
    if not yrs:
        return ""
    y0, y1 = min(yrs), max(yrs)
    pad = 34
    base = h - 16
    def x(yr):
        return (pad + (yr - y0) / (y1 - y0) * (w - 2 * pad)) if y1 > y0 else w / 2
    out = [f'<svg class="tl" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="evidence timeline">']
    out.append(f'<line x1="{pad}" y1="{base}" x2="{w-pad}" y2="{base}" stroke="#d7deea" stroke-width="2"/>')
    out.append(f'<text x="{pad}" y="{h-2}" class="tlyr">{y0}</text>')
    if y1 > y0:
        out.append(f'<text x="{w-pad}" y="{h-2}" class="tlyr" text-anchor="end">{y1}</text>')
    bucket = defaultdict(int)
    for it in sorted(items, key=lambda d: d.get("year") or 0):
        yr = it.get("year")
        if not isinstance(yr, int):
            continue
        k = bucket[yr]; bucket[yr] += 1
        cx = x(yr); cy = base - 5 - k * 9
        col = KIND_COLOR.get(it.get("kind"), "#1f6a93")
        lab = it.get("label")
        kind_lab = ROLE_LABEL.get(it.get("kind"), it.get("kind", ""))
        title = _html.escape(f'{lab} · {kind_lab}' if lab else f'{kind_lab}, {yr}')
        if it.get("kind") == "origin":   # first literature mention: hollow ring, distinct from evidence dots
            dot = f'<circle cx="{cx:.1f}" cy="{cy}" r="6" fill="#fff" stroke="{col}" stroke-width="2.5"><title>{title}</title></circle>'
        else:
            dot = f'<circle cx="{cx:.1f}" cy="{cy}" r="5" fill="{col}"><title>{title}</title></circle>'
        url = it.get("url")
        if url:
            dot = f'<a href="{_html.escape(url)}" target="_blank" rel="noopener" class="tldotlink">{dot}</a>'
        out.append(dot)
    out.append("</svg>")
    return "".join(out)

LEGEND = ('<span class="tllg"><span class="tldot" style="background:#1d7a4f"></span>consistent '
          '<span class="tldot" style="background:#a23b52"></span>conflicting '
          '<span class="tldot" style="background:#94a3b8"></span>contextual</span>')


# Umami (analytics self-hospedado, sem cookies) — uma única definição para TODAS as páginas.
# Fica aqui e não copiado em cada template para que trocar o host/ID seja uma edição só.
# Também é colado à mão em index.html e pt/index.html, que são escritos à mão (não gerados).
ANALYTICS = ('<script defer src="https://umami.caprover.amato.io/script.js" '
             'data-website-id="58f2ba6a-560e-4c60-b96d-2c890a3bd339"></script>')
