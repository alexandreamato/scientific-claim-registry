#!/usr/bin/env python3
"""SCR — Layer 1 surveillance loop (prototype).

For a scientific question, search the live literature (Europe PMC, no API key needed),
find articles NOT yet indexed in the registry, and stage them as candidates. An LLM step
(see classify()) then turns each relevant candidate into a draft claim with a stance.

Run LOCALLY; deploy only the static site. Pipeline:
  ingest.py <Q> --commit  →  db.py export  →  build_questions.py/build_site.py  →  rsync  →  purge

Usage:
  python3 ingest.py SQ-LIP-000005            # dry-run: show new articles
  python3 ingest.py SQ-LIP-000005 --commit   # stage candidates (+ temp ids) into scr.db
  python3 ingest.py --all [--commit]
  python3 ingest.py SQ-LIP-000005 --since 2024 --max 25
"""
import sys, os, json, re, html, urllib.request, urllib.parse, datetime
import db  # same folder: reuse conn(), request_id()

_TAG_RE = re.compile(r"<[^>]+>")

def clean_text(s):
    """Strip JATS/HTML markup that leaks from Crossref/Europe PMC metadata (<scp>, <i>, <sub>,
    <sup>, <italic>…) and collapse whitespace/newlines. The registry stores CLEAN text always —
    every write of a title/author/journal passes through this (R-CLM-14). Safe on None."""
    if not s:
        return s
    s = _TAG_RE.sub("", str(s))
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

DIR = os.path.dirname(os.path.abspath(__file__))
QJSON = os.path.join(DIR, "questions.json")
CJSON = os.path.join(DIR, "claims.json")
def _load_domains():
    """Canonical domain-code dictionary (registry/domains.json) → {CODE: search_term}."""
    try:
        return {d["code"]: (d.get("search_term") or d["name"])
                for d in json.load(open(os.path.join(DIR, "domains.json")))["domains"]}
    except Exception:
        return {"LIP": "lipedema"}
DOMAIN_TERM = _load_domains()
STOP = set("does is are the a an of to in on and or with without between among lipedema increase "
           "prevalence affect linked associated other related symptoms patients people who what how "
           "than more most can may have has been being effective safe recommended".split())

def domain_of(qid): return qid.split("-")[1] if "-" in qid else "LIP"

def build_query(q):
    """Per-question curated query if present; else heuristic (domain term + 2 most distinctive words)."""
    if q.get("query"):
        return q["query"]
    dom = DOMAIN_TERM.get(domain_of(q["id"]), domain_of(q["id"]).lower())
    words = [w for w in re.findall(r"[a-zA-Z\-]{4,}", q["text"].lower()) if w not in STOP and w != dom]
    words = sorted(set(words), key=len, reverse=True)[:2]
    return f'{dom} AND ({" OR ".join(words)})' if words else dom

def indexed_refs():
    """DOIs/PMIDs already in the registry (so we ingest only what's new)."""
    dois, pmids = set(), set()
    for c in json.load(open(CJSON))["claims"]:
        for ev in c.get("evidence", []):
            r = (ev.get("ref") or "").strip()
            if r.upper().startswith("DOI:"): dois.add(r[4:].lower())
            elif r.upper().startswith("PMID:"): pmids.add(r[5:])
    return dois, pmids

def europepmc(query, from_year, n):
    q = f'({query}) AND (PUB_YEAR:[{from_year} TO {datetime.date.today().year}])'
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": q, "format": "json", "pageSize": n,
                                     "resultType": "core", "sort": "P_PDATE_D desc"}))
    req = urllib.request.Request(url, headers={"User-Agent": "SCR-ingest/0.1 (scientificclaims.org)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data.get("resultList", {}).get("result", [])

# ---- provider-agnostic LLM layer (Anthropic/Claude OR OpenAI) ----
DEF_MODEL = {"openrouter": "anthropic/claude-opus-4.8", "anthropic": "claude-opus-4-8", "openai": "gpt-4o"}

def _filekey(name):
    p = os.path.expanduser(f"~/.config/{name}")
    return open(p).read().strip() if os.path.exists(p) else None

# Secret resolution order (decentralization Fase 1): canonical SCR_* env var → conventional vendor
# env var (back-compat) → ~/.config file (back-compat). Same code runs from a local .env, a
# container, or GitHub Actions with no change.
def _openai_key():
    return (os.environ.get("SCR_OPENAI_TOKEN") or os.environ.get("OPENAI_API_KEY")
            or _filekey("scr_openai_token"))

def _anthropic_key():
    return (os.environ.get("SCR_ANTHROPIC_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
            or _filekey("scr_anthropic_token"))

def _openrouter_key():
    return (os.environ.get("SCR_OPENROUTER_TOKEN") or os.environ.get("OPENROUTER_API_KEY")
            or _filekey("scr_openrouter_token"))

def provider():
    """LLM backend: env SCR_LLM_PROVIDER, else auto (OpenRouter > Anthropic > OpenAI by key presence)."""
    p = os.environ.get("SCR_LLM_PROVIDER")
    if p: return p
    if _openrouter_key(): return "openrouter"
    if _anthropic_key(): return "anthropic"
    if _openai_key(): return "openai"
    return None

def model_name():
    return os.environ.get("SCR_LLM_MODEL") or DEF_MODEL.get(provider() or "openai", "gpt-4o")

def _extract_json(s):
    i, j = s.find("{"), s.rfind("}")
    return s[i:j + 1] if i >= 0 and j > i else s

def _chat_json(system, user, model=None):
    """Single-turn 'return strict JSON' call routed to the active provider. Returns a parsed dict.
    `model` overrides the default model for this call (used by the independent verifier, R-AI-14)."""
    prov = provider()
    mdl = model or model_name()
    if prov == "openrouter":
        body = json.dumps({"model": mdl, "temperature": 0,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                     headers={"Authorization": f"Bearer {_openrouter_key()}",
                                              "Content-Type": "application/json",
                                              "X-Title": "Scientific Claim Registry"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        return json.loads(_extract_json(d["choices"][0]["message"]["content"]))
    if prov == "anthropic":
        body = json.dumps({"model": mdl, "max_tokens": 1500, "temperature": 0, "system": system,
                           "messages": [{"role": "user", "content": user},
                                        {"role": "assistant", "content": "{"}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
                                     headers={"x-api-key": _anthropic_key(), "anthropic-version": "2023-06-01",
                                              "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        s = "{" + d["content"][0]["text"]
        return json.loads(s[:s.rfind("}") + 1])
    body = json.dumps({"model": mdl, "temperature": 0, "response_format": {"type": "json_object"},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {_openai_key()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    return json.loads(d["choices"][0]["message"]["content"])


# R-AI-14 — the INDEPENDENT verifier runs a DIFFERENT model from the primary classifier, so a
# stance/extraction error has to survive two distinct models to enter the registry as verified.
DEF_VERIFY = {"openrouter": "anthropic/claude-sonnet-4-6", "anthropic": "claude-sonnet-4-6",
              "openai": "gpt-4o-mini"}

def verify_model_name():
    """Model used for the adversarial verification pass — env SCR_VERIFY_MODEL, else a per-provider
    default DISTINCT from the primary classifier (independence is the whole point)."""
    return os.environ.get("SCR_VERIFY_MODEL") or DEF_VERIFY.get(provider() or "openai", "gpt-4o-mini")

_MODEL_LABELS = {"claude-opus-4.8": "Claude Opus 4.8", "claude-opus-4-8": "Claude Opus 4.8",
                 "claude-opus-4-7": "Claude Opus 4.7", "claude-sonnet-4-6": "Claude Sonnet 4.6",
                 "gpt-4o": "GPT-4o", "gpt-4o-mini": "GPT-4o mini"}

def model_label(m):
    """Human-friendly label for a model id (provider prefix stripped). Shared by loop.py/verify_claims.py."""
    base = (m or "").split("/")[-1].lower()
    return _MODEL_LABELS.get(base, (m or "").split("/")[-1])

MODEL = model_name()

def search_library(q, n):
    """Fallback library search (registry/library.db, FTS5 keyword). Lipedema domain only."""
    try:
        import library_index
    except Exception:
        return []
    return library_index.search(build_query(q), n)

# ---- bib: the author's local library with SEMANTIC retrieval + structured fichas ----
BIB_API = os.environ.get("BIB_API", "http://127.0.0.1:8900")
BIB_DIR = os.environ.get("BIB_DIR", "/Users/alexandreamato/Library/CloudStorage/SynologyDrive-aamato/artigos lipedema")
_FICHAMOD = None

def _fichamod():
    """Lazy-load the library's ficha module (exact ficha lookup by stem; lightweight file IO)."""
    global _FICHAMOD
    if _FICHAMOD is None:
        tools = os.path.join(BIB_DIR, "tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        from bib_cli.commands import semantic as _sm
        _FICHAMOD = _sm.fichamod
    return _FICHAMOD

def _bib_get(path):
    with urllib.request.urlopen(urllib.request.Request(BIB_API + path), timeout=25) as r:
        return json.loads(r.read())

def bib_available():
    try:
        return bool(_bib_get("/health").get("ok"))
    except Exception:
        return False

def _flat(x):
    if isinstance(x, list): return " ".join(_flat(i) for i in x)
    return str(x) if x not in (None, "") else ""

def _ficha_candidate(f, stem):
    """Compose a candidate from a bib ficha — the curated card (objetivo/resultados/conclusão)
    is a richer, cleaner classify input than a raw abstract."""
    abstract = " ".join(_flat(f.get(k)) for k in ("objetivo", "intervencao_exposicao",
              "principais_resultados", "conclusao_autores", "resumo_oficial")).strip()
    yr = f.get("ano")
    return {"source": "library", "id": stem, "doi": (f.get("doi") or None), "pmid": None,
            "title": f.get("titulo") or stem, "pubYear": (int(yr) if str(yr).isdigit() else None),
            "abstractText": (abstract or f.get("resumo_oficial") or "")[:4000],
            "grau": f.get("grau_evidencia"), "tipo_estudo": f.get("tipo_estudo"),
            "amato_authored": str(stem).lower().startswith("amato")}

def bib_search(question_text, n):
    """SEMANTIC retrieval over the local library: bib /semantic ranks by meaning (Ollama embeddings),
    then each stem's EXACT structured ficha (objetivo/resultados/conclusão + DOI) becomes a candidate."""
    try:
        sem = _bib_get(f"/semantic?q={urllib.parse.quote(question_text)}&limit={n}").get("results", [])
        fm = _fichamod()
    except Exception as ex:
        print(f"  [bib semantic error: {ex} — skipping library this call]")
        return []
    out = []
    for s in sem:
        stem = s.get("stem", "")
        try:
            f = fm.load(fm.stem_to_path(stem))
        except Exception:
            continue
        out.append(_ficha_candidate(f, stem))
    return out

def excluded_set():
    """DOIs/PMIDs banned from ingestion (registry/exclude.json), managed via curate.py."""
    try:
        x = json.load(open(os.path.join(DIR, "exclude.json")))
        return {(e["ref"] or "").replace("DOI:", "").replace("doi:", "").strip().lower()
                for e in x.get("excluded", [])}
    except Exception:
        return set()

def gather(q, sources, from_year, n):
    """Collect candidate articles from the requested sources (library + Europe PMC)."""
    out = []
    if "library" in sources and domain_of(q["id"]) == "LIP":
        if bib_available():
            out += bib_search(q["text"], n)
        else:
            out += search_library(q, n)
    if "europepmc" in sources:
        try: out += europepmc(build_query(q), from_year, n)
        except Exception as e: print(f"  [europepmc error] {e}")
    # de-dup within the gathered set, and drop banned refs (exclude.json)
    excl = excluded_set()
    seen, uniq = set(), []
    for a in out:
        if (a.get("doi") or "").lower() in excl:
            continue
        key = (a.get("doi") or "").lower() or a.get("pmid") or (a.get("title") or "")[:80].lower()
        if key and key not in seen:
            seen.add(key); uniq.append(a)
    return uniq

# R-AI-12 — ACTIVE contradiction-seeking retrieval. The topic-focused query (build_query) surfaces mostly
# confirming studies; to avoid a confirmation-biased evidence base we ALSO query specifically for null /
# negative / non-replication / opposing findings, on every run. The classifier (R-AI-11) then labels them.
NEG_TERMS = ('"no association"', '"not associated"', '"no significant"', '"no difference"', '"no correlation"',
             '"did not"', '"failed to"', '"no benefit"', '"no effect"', '"does not"', 'null', 'negative',
             'refute', 'contradict', 'unrelated')

def contra_query(q):
    """Europe PMC query targeting DISCONFIRMING evidence on the question's topic."""
    return f'({build_query(q)}) AND ({" OR ".join(NEG_TERMS)})'

def contra_text(q):
    """Disconfirming-biased phrasing for the semantic library search."""
    return f'null result, no association, negative finding, evidence against, fails to confirm: {q["text"]}'

def gather_contra(q, from_year, n):
    """Active contradiction-seeking pass — runs on EVERY loop run, in any mode (R-AI-12)."""
    out = []
    try:
        out += europepmc(contra_query(q), min(from_year, 2000), n)  # widen: null findings are often older
    except Exception as e:
        print(f"  [contra europepmc error] {e}")
    if domain_of(q["id"]) == "LIP" and bib_available():
        try:
            out += bib_search(contra_text(q), max(4, n // 2))
        except Exception as e:
            print(f"  [contra library error] {e}")
    excl = excluded_set()
    seen, uniq = set(), []
    for a in out:
        if (a.get("doi") or "").lower() in excl:
            continue
        key = (a.get("doi") or "").lower() or a.get("pmid") or (a.get("title") or "")[:80].lower()
        if key and key not in seen:
            seen.add(key); uniq.append(a)
    return uniq

SYS_CLASSIFY = ("You compile scientific evidence for a registry that REGISTERS, it does not arbitrate truth. "
    "Given a scientific QUESTION and an ARTICLE (title + abstract), decide whether the article provides "
    "evidence bearing on the question and, if so, its stance relative to the question's affirmative direction. "
    "Be conservative: if the article does not directly address the question, set relevant=false. "
    "Never give opinions; describe only what the article reports. Output strict JSON.\n"
    "ANTI-CONFIRMATION-BIAS (R-AI-11) — this is mandatory. Do NOT default to 'supporting'. Real literature is "
    "rarely one-sided; a body of evidence that is ~100% supporting is a RED FLAG of detection bias, not a feature. "
    "Actively look for disconfirming signal and use the precise stance:\n"
    "  • contradicting — the article reports a NULL / negative / non-significant / failed-replication result on "
    "the relationship, OR an effect in the OPPOSITE direction, OR concludes against the affirmative answer. A "
    "well-powered null result IS contradicting evidence — classify it as such, do not soften it to 'context'.\n"
    "  • refines — supports a qualified/narrower version, or supports only after adjustment / in a subgroup, or "
    "adds an important caveat (e.g. association is crude-only and disappears after adjusting for BMI).\n"
    "  • context — on-topic but does NOT itself test the relationship (background, definitions, mechanism without "
    "the outcome, a different population) — i.e. NOT directly informative either way.\n"
    "  • supporting — directly provides affirmative evidence FOR the relationship.\n"
    "When the abstract is ambiguous or only mentions the topic without testing it, prefer 'context' over "
    "'supporting'. Reserve 'supporting' for genuine affirmative findings.")

def llm_classify(question, art):
    user = (f'QUESTION ({question["id"]}): {question["text"]}\n'
            f'ARTICLE TITLE: {art.get("title")}\n'
            f'ARTICLE ABSTRACT: {(art.get("abstractText") or "")[:3500]}\n\n'
            'Return a JSON object with keys:\n'
            ' relevant (boolean),\n'
            ' stance (one of: supporting, contradicting, refines, context, irrelevant) — relative to the '
            "question's affirmative answer,\n"
            " statement (one neutral, self-contained sentence stating the article's SPECIFIC primary finding — "
            'the actual mechanism, biomarker, measurement, imaging result, population or effect size — NOT a '
            'generic restatement of the question\'s conclusion. E.g. prefer "Lipedema adipose tissue shows '
            'distinct gene expression and adipocyte hypertrophy versus controls" over "lipedema is a distinct '
            'disease"; prefer "MR lymphangiography reveals subcutaneous tissue edema in lipedema" over "lipedema '
            'is distinct from lymphedema". Empty string "" if irrelevant),\n'
            ' statement_pt (the statement in Brazilian Portuguese),\n'
            ' study_design (meta_analysis | rct | cohort | cross_sectional | case_series | case_report | '
            'review | basic_science | unknown),\n'
            ' confidence_grade (high | moderate | low | very_low),\n'
            ' quote (R-AI-13 — a VERBATIM span copied WORD-FOR-WORD from the ARTICLE ABSTRACT above that '
            'directly justifies the stance and statement; ≤300 chars; it MUST be an exact substring of the '
            'abstract — do NOT paraphrase, summarize, translate, or fix typos. Empty string "" if the abstract '
            'does not contain a span that grounds the finding),\n'
            ' extraction_confidence (high | moderate | low — how confident YOU are that you read the article '
            "correctly and the statement faithfully reflects it; this is about READING the source, NOT the "
            "study's scientific quality, which is confidence_grade. Use 'low' when the abstract is thin, "
            'ambiguous, or you are inferring beyond what it states),\n'
            ' population (PECO: who was studied — short noun phrase, e.g. "women with lipedema, stage I-III"),\n'
            ' exposure (PECO: the intervention/factor studied — short, e.g. "tumescent liposuction"),\n'
            ' comparator (PECO: vs what — short, or "—" if none),\n'
            ' outcome (PECO: the measured endpoint — short, e.g. "limb pain (VAS)"),\n'
            ' reason (short justification).\n\n'
            'CRITICAL for ASSOCIATION / "is X linked to Y" / causal questions: prioritize the article\'s '
            'MOST RIGOROUS result on that relationship — an ADJUSTED / multivariate analysis OUTRANKS a crude '
            'prevalence or unadjusted comparison. If the article found NO independent association after '
            'adjusting for confounders (e.g. obesity/BMI; p>0.05 on multivariate), the statement MUST say so '
            'and the stance is "refines" or "contradicting" — NEVER report only the crude/raw prevalence as if '
            'it established the association. State both when present (e.g. "crude prevalence high, but NOT an '
            'independent factor after adjustment, p=…").')
    return _chat_json(SYS_CLASSIFY, user)

def _norm(s):
    """Normalize for substring matching: lowercase, strip markup, collapse whitespace/punctuation spacing."""
    s = (clean_text(s) or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()

def is_grounded(quote, source_text):
    """R-AI-13 — DETERMINISTIC quote-grounding: is `quote` an exact (normalized) span of the source we
    classified from? Catches a hallucinated/paraphrased quote for free, with no model and no ambiguity.
    Short quotes (<20 normalized chars) are too weak to ground a claim → not grounded."""
    nq = _norm(quote)
    if len(nq) < 20:
        return False
    return nq in _norm(source_text)


def combined_source_text(art):
    """The FULLEST available source text to verify against (R-AI-14 calibration). A library candidate
    carries the curated PT ficha (rich on buried Results, but a partial card); the original EN statement
    was often extracted from the fuller Europe PMC abstract. Judging faithfulness against only the ficha
    caused false 'invented specifics' disputes (e.g. a sample size that IS in the EN abstract). So we
    verify against ficha + EN abstract combined: a specific is 'invented' only if absent from BOTH."""
    parts, seen = [], set()
    for t in (art.get("abstractText"),):
        if t and t not in seen:
            parts.append(t); seen.add(t)
    doi = art.get("doi")
    if doi and art.get("source") != "europepmc":
        try:
            ext = europepmc_by_doi(doi)
            eab = (ext or {}).get("abstractText")
            if eab and eab not in seen:
                parts.append(eab); seen.add(eab)
        except Exception:
            pass
    return "\n\n".join(parts)


SYS_VERIFY = ("You are an INDEPENDENT verifier for a scientific evidence registry. A primary system read an "
    "ARTICLE and proposed, for a QUESTION: a STANCE (supporting/contradicting/refines/context relative to the "
    "question's affirmative answer) and a one-sentence STATEMENT of the finding. Your job is ADVERSARIAL but "
    "at the RIGHT ALTITUDE (R-AI-14). The STATEMENT belongs to a registry CLAIM that may be backed by MULTIPLE "
    "sources; THIS article is only ONE of them — a claim statement legitimately says MORE than any single "
    "source. So do NOT flag the statement merely because it contains extra descriptors this source does not "
    "mention. Flag faithful=false ONLY when (a) THIS source CONTRADICTS the statement (asserts the opposite, or "
    "a finding incompatible with it), OR (b) the statement MISATTRIBUTES to this source a specific it does not "
    "contain — a sample size, population, method, named author, or numeric result that is simply not in this "
    "source. Otherwise faithful=true. Also independently decide the STANCE yourself; a well-powered null/negative "
    "result is 'contradicting', not 'context'. You REGISTER evidence; you do not arbitrate truth. Output strict JSON.")

def verify_extraction(question, art, cl):
    """R-AI-14 — adversarial verification of one extracted evidence item. Combines:
      • DETERMINISTIC grounding: the model's `quote` must be an exact span of the abstract (R-AI-13);
      • INDEPENDENT stance: a DIFFERENT model re-derives stance + judges faithfulness (R-AI-14).
    verdict = 'verified' iff grounded AND the verifier agrees on stance AND finds the statement faithful;
    else 'disputed'. Never deletes anything — the caller records the verdict (registra, não arbitra)."""
    src = combined_source_text(art) or art.get("abstractText") or ""
    grounded = is_grounded(cl.get("quote"), src)
    out = {"method": "dual-model", "verifier_model": None, "primary_model": cl.get("engine") or model_name(),
           "quote_grounded": grounded, "stance_agreed": None, "faithful": None,
           "verifier_stance": None, "verdict": "unverified", "reason": "", "date": datetime.date.today().isoformat()}
    if not provider():
        out["reason"] = "no LLM available for verification"
        return out
    vm = verify_model_name()
    out["verifier_model"] = vm
    user = (f'QUESTION ({question["id"]}): {question["text"]}\n'
            f'ARTICLE TITLE: {art.get("title")}\n'
            f'ARTICLE ABSTRACT: {(src or "")[:5000]}\n\n'
            f'PROPOSED STANCE: {cl.get("stance")}\n'
            f'PROPOSED STATEMENT: {cl.get("statement")}\n\n'
            'Independently return JSON: {"stance": "supporting|contradicting|refines|context|irrelevant" '
            '(YOUR own reading), "stance_agreed": bool (does YOUR stance match the proposed one?), '
            '"faithful": bool (TRUE unless THIS source contradicts the statement OR the statement misattributes '
            'a specific finding/number/population/method/author to this source; additional true descriptors '
            'supported elsewhere do NOT make it false), "reason": "<short>"}.')
    try:
        v = _chat_json(SYS_VERIFY, user, model=vm)
    except Exception as ex:
        out["reason"] = f"verifier error: {ex}"
        return out
    out["verifier_stance"] = v.get("stance")
    out["stance_agreed"] = bool(v.get("stance_agreed")) if v.get("stance_agreed") is not None else (v.get("stance") == cl.get("stance"))
    out["faithful"] = bool(v.get("faithful"))
    out["reason"] = (v.get("reason") or "")[:240]
    # Grounding is provenance ENRICHMENT, not the arbiter (R-AI-14 calibration on the full pilot). When an
    # independent model that READ the source confirms stance AND faithfulness, a failed deterministic
    # quote-substring (number formatting, language, or a non-verbatim span) must NOT alone mark the item
    # disputed — that floods human review with already-confirmed items (62% of disputes were exactly this).
    # disputed iff the CONTENT check fails (stance disagreement or unfaithful); `quote_grounded` stays a flag.
    out["verdict"] = "verified" if (out["stance_agreed"] and out["faithful"]) else "disputed"
    if out["verdict"] == "verified" and not grounded:
        out["reason"] = ("verified by verifier; quote not verbatim-grounded. " + (out["reason"] or ""))[:240]
    return out


SYS_INTEGRITY = ("You audit the STATEMENT of a scientific registry claim for FABRICATION — concrete specifics it "
    "asserts that appear in NONE of the claim's sources. This is the per-claim complement to per-source checking "
    "(R-AI-14): a statement may legitimately synthesize across several sources, so a specific present in ANY source "
    "is fine. Flag ONLY specifics — sample sizes, numeric results, named methods/authors, populations, biomarkers, "
    "mechanisms, measurements — that are present in NONE of the provided SOURCES. Do NOT flag broad, true, "
    "general-knowledge descriptors (e.g. 'painful', 'bilateral') for being absent — only concrete, checkable "
    "specifics. You REGISTER evidence; you do not arbitrate truth. Output strict JSON.")

def verify_statement_integrity(question, statement, sources_text, model=None):
    """R-AI-14 (per-claim altitude) — does the STATEMENT assert concrete specifics absent from the UNION of the
    claim's sources (fabrication)? Catches what per-source checking cannot: a specific that is in NO source.
    `sources_text` is the combined text of ALL the claim's evidence sources. Returns {fabricated, invented, reason}."""
    if not provider() or not (sources_text or "").strip():
        return {"fabricated": None, "invented": [], "reason": "no sources/LLM for integrity check",
                "verifier_model": None, "date": datetime.date.today().isoformat()}
    mdl = model or verify_model_name()
    user = (f'QUESTION ({question["id"]}): {question["text"]}\n'
            f'CLAIM STATEMENT: {statement}\n\n'
            f'ALL SOURCES FOR THIS CLAIM (union — a specific present in ANY of these is supported):\n'
            f'{(sources_text or "")[:9000]}\n\n'
            'Return JSON: {"fabricated": bool (does the statement assert any concrete specific present in NONE of '
            'the sources?), "invented": [list the specific phrases from the statement that are absent from ALL '
            'sources], "reason": "<short>"}.')
    try:
        r = _chat_json(SYS_INTEGRITY, user, model=mdl)
    except Exception as ex:
        return {"fabricated": None, "invented": [], "reason": f"integrity error: {ex}",
                "verifier_model": mdl, "date": datetime.date.today().isoformat()}
    return {"fabricated": bool(r.get("fabricated")), "invented": (r.get("invented") or [])[:8],
            "reason": (r.get("reason") or "")[:240], "verifier_model": mdl,
            "date": datetime.date.today().isoformat()}


def europepmc_by_doi(doi):
    """Fetch one article's metadata (title+abstract) by DOI from Europe PMC."""
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": f'DOI:"{doi}"', "format": "json",
                                     "resultType": "core", "pageSize": 1}))
    req = urllib.request.Request(url, headers={"User-Agent": "SCR-ingest/0.1 (scientificclaims.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read()).get("resultList", {}).get("result", [])
        if res:
            a = res[0]; a["source"] = "europepmc"
            a.setdefault("doi", doi)
            return a
    except Exception:
        pass
    return {"source": "external", "doi": doi, "pmid": None, "title": None, "abstractText": None, "id": doi}

def bib_by_doi(doi):
    """If the DOI is in the local library, build the candidate from its rich ficha (objetivo/resultados/
    conclusão) instead of the thin Europe PMC abstract — findings buried in Results (e.g. an adjusted
    null result) are then visible to the classifier. Returns None if not in the library."""
    if not bib_available():
        return None
    try:
        res = _bib_get(f"/search?q={urllib.parse.quote(doi)}&context=1&limit=3").get("results", [])
    except Exception:
        return None
    for f in res:
        if (f.get("doi") or "").lower() == doi.lower():
            return _ficha_candidate(f, f.get("stem", doi))
    return None

def fetch_dois(dois):
    """Resolve a curated DOI list into candidates — local library ficha first (richer), else Europe PMC."""
    return [(bib_by_doi(d.strip()) or europepmc_by_doi(d.strip())) for d in dois if d.strip()]

def classify(question, art):
    """Relevance + stance + one-sentence claim. Uses OpenAI when a key is available, else a
    conservative heuristic fallback. Prompt contract documented in docs/spec/surveillance.md."""
    if provider():
        try:
            r = llm_classify(question, art)
            r.setdefault("stance", "context"); r.setdefault("study_design", "unknown")
            r.setdefault("statement", art.get("title") or "")
            r.setdefault("quote", ""); r.setdefault("extraction_confidence", "moderate")
            r["relevant"] = bool(r.get("relevant")) and r.get("stance") != "irrelevant"
            r["engine"] = model_name()
            return r
        except Exception as e:
            print(f"    [llm error: {e} — heuristic fallback]")
    text = ((art.get("title") or "") + " " + (art.get("abstractText") or "")).lower()
    dom = DOMAIN_TERM.get(domain_of(question["id"]), "").lower()
    return {"relevant": dom in text, "stance": "unclassified", "engine": "heuristic",
            "statement": art.get("title") or "", "study_design": "unknown"}

def run(q, commit, from_year, n, sources):
    query = build_query(q)
    dois, pmids = indexed_refs()
    results = gather(q, sources, from_year, n)
    new = [a for a in results if ((a.get("doi") or "").lower() not in dois) and ((a.get("pmid") or "") not in pmids)]
    print(f"\n{q['id']}  ·  sources: {'+'.join(sources)}  ·  query: {query}")
    print(f"  found {len(results)} · {len(new)} not yet indexed")
    staged = 0
    c = db.conn()
    c.execute("INSERT INTO ingest_runs(question_id,query,found,new_n,ran_at) VALUES(?,?,?,?,?)",
              (q["id"], query, len(results), len(new), datetime.date.today().isoformat()))
    for a in new:
        cl = classify(q, a)
        flag = f"✓{cl['stance']}" if cl["relevant"] else "·skip"
        print(f"    {flag:14s} {a.get('pubYear','?')}  [{a.get('source','?')}]  {(a.get('title') or '')[:78]}  [{a.get('doi') or a.get('pmid') or a.get('id')}]")
        if commit and cl["relevant"]:
            temp = db.request_id("SCR", domain_of(q["id"]), "claim",
                                 note=f"ingest for {q['id']}", source=a.get("doi") or a.get("pmid") or a.get("id"))
            try:
                c.execute("""INSERT INTO ingest_candidates(question_id,source,ext_id,doi,pmid,title,year,abstract,stance,proposed_statement,temp_id,status,created)
                             VALUES(?,?,?,?,?,?,?,?,?,?,?, 'drafted', ?)""",
                          (q["id"], a.get("source"), a.get("id"), a.get("doi"), a.get("pmid"),
                           a.get("title"), int(a.get("pubYear") or 0) or None, a.get("abstractText"),
                           cl["stance"], cl["statement"], temp, datetime.date.today().isoformat()))
                staged += 1
            except Exception:
                pass  # UNIQUE(question_id, ext_id) — already staged
    c.commit(); c.close()
    if commit:
        print(f"  staged {staged} candidate(s) as drafts (status: needs LLM classification).")
    return len(new), staged

if __name__ == "__main__":
    args = sys.argv[1:]
    commit = "--commit" in args
    from_year = int(args[args.index("--since")+1]) if "--since" in args else datetime.date.today().year - 3
    n = int(args[args.index("--max")+1]) if "--max" in args else 20
    src_arg = args[args.index("--source")+1] if "--source" in args else "all"
    sources = ["library", "europepmc"] if src_arg == "all" else src_arg.split(",")
    qs = json.load(open(QJSON))["questions"]
    targets = qs if "--all" in args else [x for x in qs if x["id"] in args]
    if not targets:
        print(__doc__); sys.exit(0)
    print(f"engine: {'OpenAI ' + MODEL if _openai_key() else 'heuristic (no OPENAI key — set OPENAI_API_KEY or ~/.config/scr_openai_token)'}")
    tot_new = tot_staged = 0
    for q in targets:
        nn, st = run(q, commit, from_year, n, sources); tot_new += nn; tot_staged += st
    print(f"\nTotal: {tot_new} new article(s); {tot_staged} staged." + ("" if commit else "  (dry-run; use --commit to stage)"))
