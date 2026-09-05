#!/usr/bin/env python3
"""SCR — Layer 1, the closed loop: ingest → classify → PROMOTE → re-compile → VERSION.

For a question: gather candidate articles (library + Europe PMC), classify each with OpenAI
(stance + one-sentence claim), and for the relevant, NOT-yet-indexed ones with a VERIFIABLE
reference: mint a new claim, link it to the question, then have the AI re-compile the question's
current answer from the full claim set and bump the question's version (frozen snapshot of the old
one is preserved). The AI compiles; it does not arbitrate (R-AI-1).

Run LOCALLY (needs OpenAI key: env OPENAI_API_KEY or ~/.config/scr_openai_token). Pipeline:
  loop.py <Q> --commit  →  build_questions.py + build_site.py  →  rsync  →  purge

Usage:
  python3 loop.py SQ-LIP-000005                  # dry-run: show proposed claims + new answer
  python3 loop.py SQ-LIP-000005 --commit         # write claims.json + questions.json
  python3 loop.py SQ-LIP-000005 --accept 2 --commit   # cap promotions to top 2 relevant
  python3 loop.py SQ-LIP-000005 --no-recompile --commit  # add claims + bump, keep answer text
"""
import json, os, sys, datetime, urllib.request, urllib.parse, urllib.error
import ingest
import db  # standardized DB auto-sync (db.sync) after every seed write

DIR = os.path.dirname(os.path.abspath(__file__))
QJSON = os.path.join(DIR, "questions.json")
CJSON = os.path.join(DIR, "claims.json")
TODAY = datetime.date.today().isoformat()
THIS_YEAR = datetime.date.today().year

def safe_year(art):
    """Publication year, guarded: reject impossible future years (Europe PMC pubYear quirks)."""
    y = int(art.get("pubYear") or 0)
    return y if 1900 <= y <= THIS_YEAR else None
STANCE_ROLE = {"supporting": "supporting", "contradicting": "contradicting",
               "refines": "refines", "context": "context"}


def verify_ref(doi, pmid):
    """Return a clean 'DOI:'/'PMID:' ref that actually resolves, or None. Guards against the
    dirty DOIs that pdftotext sometimes produces (trailing journal words, etc.)."""
    if doi:
        d = doi.strip().lower()
        try:
            req = urllib.request.Request("https://doi.org/" + urllib.parse.quote(d), method="HEAD",
                                         headers={"User-Agent": "SCR-loop/0.1 (scientificclaims.org)"})
            urllib.request.urlopen(req, timeout=10)
            return f"DOI:{d}"
        except urllib.error.HTTPError as ex:
            if ex.code != 404:
                return f"DOI:{d}"   # resolved to a publisher that blocks HEAD → DOI is real
        except Exception:
            pass
    if pmid and str(pmid).isdigit():
        return f"PMID:{pmid}"
    return None


def bump(ver):
    maj, mnr = (ver.split(".") + ["0"])[:2]
    return f"{maj}.{int(mnr) + 1}"

# R-AI-9 — public AI provenance: stamp which model consolidated each answer.
_MODEL_LABELS = {"claude-opus-4.8": "Claude Opus 4.8", "claude-opus-4-8": "Claude Opus 4.8",
                 "claude-opus-4-7": "Claude Opus 4.7", "claude-sonnet-4-6": "Claude Sonnet 4.6",
                 "gpt-4o": "GPT-4o", "gpt-4o-mini": "GPT-4o mini"}

def model_label(m):
    base = (m or "").split("/")[-1].lower()
    return _MODEL_LABELS.get(base, (m or "").split("/")[-1])

def compiled_by():
    """Provenance of the AI consolidation step, shown publicly (R-AI-9). We record the AI MODEL only —
    not the access route/provider (the means is irrelevant; the model is what matters)."""
    m = ingest.model_name()
    return {"model": m, "label": model_label(m), "date": TODAY}


# R-CLM-13 — the human-curated Oxford level in the author's library (`bib`, field `grau`,
# N1=best..N6=mechanism/opinion) is a CEILING on the grade the LLM may assign. A weak paper
# (e.g. an N6 narrative review) can never enter as `moderate`/`high`. Curated grade > model grade.
_GRADE_RANK = {"very_low": 0, "low": 1, "moderate": 2, "high": 3}
_N_TO_GRADE = {"N1": "high", "N2": "high", "N3": "moderate", "N4": "low", "N5": "low", "N6": "very_low"}

def _grade_ceiling(art):
    """Curated GRADE ceiling for an article, from its bib `grau` (carried on library candidates,
    else resolved by DOI). Returns None when the library has no curated grade for it."""
    grau = art.get("grau")
    if not grau and art.get("doi"):
        try:
            grau = (ingest.bib_by_doi(art["doi"]) or {}).get("grau")
        except Exception:
            grau = None
    return _N_TO_GRADE.get(str(grau).strip().upper().replace(" ", "")) if grau else None

def cap_grade(grade, art):
    """Lower `grade` to the curated ceiling if the model over-graded; never raises it."""
    ceil = _grade_ceiling(art)
    if ceil and _GRADE_RANK.get(grade, 9) > _GRADE_RANK[ceil]:
        return ceil
    return grade

_DESIGN_MAX = {"case_report": "very_low", "case_series": "low", "basic_science": "low",
               "review": "moderate", "narrative_review": "very_low", "expert_opinion": "very_low", "cohort": "moderate"}

def design_cap(grade, design):
    """A weak study design caps the grade (audit 2026-06; extends R-CLM-13 to design)."""
    ceil = _DESIGN_MAX.get((design or "").lower())
    if ceil and _GRADE_RANK.get(grade, 9) > _GRADE_RANK[ceil]:
        return ceil
    return grade


def next_claim_id(claims, domain):
    seqs = [int(c["id"].split("-")[-1]) for c in claims if c["id"].startswith(f"SCR-{domain}-")]
    return f"SCR-{domain}-{(max(seqs) + 1) if seqs else 1:06d}"


def cite_meta(art):
    """Citation metadata for an evidence entry — title/authors/journal carried from the article
    at ingestion so the timeline/refs always show 'Title — Authors (Year)' (R-CLM-16). Sanitized
    on write (R-CLM-14). Empty dict if the article has none; enrich_evidence.py backfills later."""
    m = {}
    t = ingest.clean_text(art.get("title"))
    if t and not t.lower().startswith(("doi:", "pmid:")):
        m["title"] = t[:300]
    a = ingest.clean_text(art.get("authors") or art.get("authorString"))
    if a:
        m["authors"] = a
    j = ingest.clean_text(art.get("journal") or art.get("journalTitle"))
    if j:
        m["journal"] = j
    return m


def _evidence_entry(art, cl, ref, grade, ver=None):
    """One evidence record, carrying sentence-level provenance (quote, R-AI-13), extraction confidence
    (R-CLM-17, distinct from GRADE), and the adversarial verification verdict (R-AI-14). A `disputed`
    verdict is recorded with needs_review=true — never dropped (registra, não arbitra)."""
    ec = cl.get("extraction_confidence")
    e = {**cite_meta(art), "ref": ref, "stance": cl.get("stance", "context"),
         "study_design": cl.get("study_design", "unknown"), "n": None,
         "risk_of_bias": "unknown", "grade": grade, "year": safe_year(art),
         "amato_authored": bool(art.get("amato_authored")),
         "quote": (cl.get("quote") or "")[:300],
         "extraction_confidence": ec if ec in ("high", "moderate", "low") else "moderate",
         "note": (cl.get("reason") or "")[:240]}
    if ver:
        e["verification"] = ver
        if ver.get("verdict") == "disputed":
            e["needs_review"] = True
    return e


def make_claim(cid, qid, art, cl, ref, ver=None):
    grade = cl.get("confidence_grade") if cl.get("confidence_grade") in ("high", "moderate", "low", "very_low") else "low"
    grade = design_cap(cap_grade(grade, art), cl.get("study_design"))  # R-CLM-13 + design ceiling
    return {
        "id": cid,
        "statement": cl.get("statement") or art.get("title") or "",
        "statement_pt": cl.get("statement_pt") or "",
        "claim_type": "clinical_association",
        "context": {"population": cl.get("population") or "—",
                    "condition": ingest.DOMAIN_TERM.get(ingest.domain_of(qid), ""),
                    "exposure": cl.get("exposure") or "—", "comparator": cl.get("comparator") or "—",
                    "outcome": cl.get("outcome") or "—",
                    "scope": "auto-ingested from Layer 1 surveillance"},
        "knowledge_state": "emerging",
        "evidence_confidence": grade,
        "evidence": [_evidence_entry(art, cl, ref, grade, ver)],
        "relations": [],
        "gaps": "Auto-ingested single source; not yet human-reviewed.",
        "primary_amato_source": None,
        "curators": [],
        "provenance": {"auto": True, "engine": cl.get("engine", ingest.MODEL),
                       "question": qid, "source": art.get("source"), "ingested": TODAY},
        "created": TODAY, "updated": TODAY,
        "history": [{"date": TODAY, "event": "created", "detail": f"auto-ingested for {qid}"}],
        "license": "CC-BY-4.0",
    }


SYS_COMPILE = ("You are the SCR compiler. Write a cautious, EVIDENCE-BOUNDED current answer to a scientific "
    "QUESTION. You REGISTER evidence; you do NOT arbitrate truth or give opinions. Compile from the FULL "
    "ACCUMULATED evidence base provided — every claim AND every persisted supporting article under the "
    "question, not only the newest additions. Evidence never expires: an article that once supported a claim "
    "remains part of the basis for every future review. "
    "WEIGHT EVIDENCE BY QUALITY: a high-quality source (systematic review / meta-analysis, RCT, large "
    "prospective cohort; high or moderate GRADE; low risk of bias) OUTWEIGHS and OVERSHADOWS low-quality "
    "sources (single case reports, small/uncontrolled cross-sectional, very_low GRADE, preprints, predatory "
    "venues) on the SAME point. When strong and weak evidence disagree, the answer follows the STRONG "
    "evidence; weak or preliminary findings are flagged as such and NEVER given equal footing. A pile of "
    "low-quality studies does not override one high-quality study. "
    "OUTCOME DISCIPLINE (R-Q-7) — mandatory for efficacy/effectiveness/treatment/management questions: NEVER say "
    "an intervention is 'effective' without naming the OUTCOME. Decompose the answer BY OUTCOME and judge each "
    "separately (e.g. pain, limb volume, quality of life, disease progression/cure, complications/safety). "
    "ALWAYS distinguish SYMPTOMATIC improvement (e.g. less pain) from DISEASE MODIFICATION / cure — an "
    "intervention can reduce symptoms while NOT altering the disease; say so explicitly. If an outcome has no "
    "evidence, state 'not demonstrated' rather than implying benefit. Do not let a positive symptomatic outcome "
    "read as overall efficacy. "
    "BOTTOM LINE: also produce a 2-sentence, plain-language bottom_line (no jargon, no 'Based on currently "
    "indexed evidence' preamble): sentence 1 = what the evidence DOES support; sentence 2 = what it does NOT "
    "support or what remains uncertain. It must be readable in 10 seconds and never overstate. "
    "VERIFICATION STATUS (R-AI-14): each evidence item carries a `verified` field. Treat items with "
    "verified='disputed' or 'unverified' as PROVISIONAL — an independent model could not confirm their "
    "stance or sentence-level provenance. NEVER let a disputed item drive or flip the answer; if you mention "
    "it, mark it explicitly as not-yet-verified. Verified evidence carries the weight. "
    "Stay hedged ('Based on currently indexed evidence…'). Output strict JSON.")


def claim_brief(c, role):
    """Full evidence-bearing view of a claim for the compiler: statement + every persisted article."""
    return {"id": c.get("id"), "role": role, "statement": c.get("statement", ""),
            "grade": c.get("evidence_confidence", ""), "knowledge_state": c.get("knowledge_state", ""),
            "evidence": [{"ref": e.get("ref"), "year": e.get("year"),
                          "study_design": e.get("study_design"), "grade": e.get("grade"),
                          "risk_of_bias": e.get("risk_of_bias"), "stance": e.get("stance"),
                          "extraction_confidence": e.get("extraction_confidence"),
                          "verified": (e.get("verification") or {}).get("verdict", "unverified"),
                          "finding": e.get("note")} for e in c.get("evidence", [])]}


def recompile(q, links, claims_by_id, prior_answer, added):
    if not ingest.provider():
        return None
    base = [claim_brief(claims_by_id.get(l["id"], {}), l["role"]) for l in links]
    n_articles = sum(len(c["evidence"]) for c in base)
    user = (f'QUESTION ({q["id"]}): {q["text"]}\n\n'
            f'PRIOR ANSWER: {prior_answer}\n\n'
            f'NEWLY ADDED this update:\n' + "\n".join(f'- ({a["role"]}) {a["statement"]}' for a in added) + "\n\n"
            f'FULL ACCUMULATED EVIDENCE BASE ({len(base)} claims, {n_articles} articles — compile from ALL of it):\n'
            + json.dumps(base, ensure_ascii=False) + "\n\n"
            'Return JSON with keys: current_answer, current_answer_pt, bottom_line (2 plain sentences: '
            'what the evidence supports + what it does not / remains uncertain), bottom_line_pt, '
            'major_uncertainty, major_uncertainty_pt, what_changed (one sentence describing what THIS update '
            'added relative to the prior answer), what_changed_pt, AND outcomes — an array (may be empty for non-efficacy '
            'questions) of {outcome (short label EN), outcome_pt, direction (one of: improved | reduced | '
            'increased | no_effect | not_demonstrated | mixed), confidence (GRADE: high|moderate|low|very_low), '
            'disease_modifying (boolean — true only if it alters disease course/cure, false for symptom-only), '
            'note (≤120 chars, EN), note_pt}. Decompose efficacy/treatment answers by outcome here.')
    return ingest._chat_json(SYS_COMPILE, user)


SYS_MATCH = ("You deduplicate scientific claims for an evidence registry. A new article is CORROBORATING "
    "EVIDENCE for an existing claim ONLY when it makes essentially the SAME SPECIFIC assertion — a "
    "restatement or replication of the same proposition, at the same level of specificity and the same KIND "
    "of evidence. It is a NEW, SEPARATE claim — EVEN IF it points in the same overall direction or supports "
    "the same broad conclusion — whenever it contributes a DISTINCT mechanism, biomarker, molecular/genetic "
    "finding, histology, imaging modality, measurement, methodology, population, or a more specific "
    "sub-finding. A broad/generic claim must NEVER absorb a specific mechanistic, molecular, or imaging "
    "finding. Prefer NEW when in doubt — registering a distinct finding is cheap; wrongly collapsing it "
    "destroys information. Output strict JSON.")

MATCH_EXAMPLES = (
    "Examples (target = a broad claim 'Lipedema is a clinically distinct entity'):\n"
    "- New: 'A review concludes lipedema is clinically distinct from obesity and lymphedema.' → MATCH "
    "(same clinical assertion, restatement).\n"
    "- New: 'Lipedema tissue shows distinct gene expression and adipocyte hypertrophy versus controls.' → "
    "NO MATCH (distinct molecular/histological finding → new claim).\n"
    "- New: 'MR lymphangiography reveals subcutaneous tissue edema in lipedema.' → NO MATCH (distinct "
    "imaging finding → new claim).\n")

def match_existing(q, cl, existing):
    """Return {match, claim_id, reason}: does the new finding RESTATE an existing claim (merge) or add a
    distinct finding (new)? Hardened to keep mechanistic/imaging/molecular findings as their own claims."""
    if not ingest.provider() or not existing:
        return {"match": False}
    user = (f'QUESTION: {q["text"]}\n'
            f'NEW FINDING (stance={cl.get("stance")}, study_design={cl.get("study_design")}): {cl.get("statement")}\n\n'
            'EXISTING CLAIMS under this question:\n'
            + "\n".join(f'- {x["id"]} (role={x["role"]}): {x["statement"]}' for x in existing)
            + "\n\n" + MATCH_EXAMPLES
            + '\nReturn JSON: {"match": bool, "claim_id": "<existing id or null>", '
              '"finding_type": "clinical|molecular|histological|imaging|epidemiological|therapeutic|other", '
              '"reason": "<short>"}.')
    try:
        return ingest._chat_json(SYS_MATCH, user)
    except Exception as ex:
        print(f"    [match error: {ex}]"); return {"match": False}

def add_evidence(claim, art, cl, ref, ver=None):
    """Append a corroborating source to an existing claim (multi-evidence)."""
    g = cl.get("confidence_grade") if cl.get("confidence_grade") in ("high", "moderate", "low", "very_low") else "low"
    g = design_cap(cap_grade(g, art), cl.get("study_design"))  # R-CLM-13 + design ceiling
    claim["evidence"].append(_evidence_entry(art, cl, ref, g, ver))
    claim["updated"] = TODAY
    detail = f"corroborated by {ref}" + (" (extraction disputed — needs review)"
                                         if ver and ver.get("verdict") == "disputed" else "")
    claim.setdefault("history", []).append({"date": TODAY, "event": "evidence added", "detail": detail})


def main():
    args = sys.argv[1:]
    commit = "--commit" in args
    recompile_on = "--no-recompile" not in args
    cap = int(args[args.index("--accept") + 1]) if "--accept" in args else 99
    src_arg = args[args.index("--source") + 1] if "--source" in args else "all"
    sources = ["library", "europepmc"] if src_arg == "all" else src_arg.split(",")
    from_year = int(args[args.index("--since") + 1]) if "--since" in args else datetime.date.today().year - 3
    n = int(args[args.index("--max") + 1]) if "--max" in args else 12
    qid = next((a for a in args if a.startswith("SQ-")), None)
    if not qid:
        print(__doc__); sys.exit(0)
    if not ingest.provider():
        sys.exit("No LLM key — set an Anthropic key (~/.config/scr_anthropic_token) or OpenAI key "
                 "(~/.config/scr_openai_token). This loop needs one.")

    qdata = json.load(open(QJSON)); cdata = json.load(open(CJSON))
    q = next((x for x in qdata["questions"] if x["id"] == qid), None)
    if not q:
        sys.exit(f"Question {qid} not found.")
    claims = cdata["claims"]; by_id = {c["id"]: c for c in claims}
    domain = ingest.domain_of(qid)

    print(f"engine: {ingest.provider()} {ingest.model_name()}  ·  {qid}: {q['text']}")

    if "--recompile-only" in args:
        # No ingestion: just re-compile the answer from the (possibly hand-curated) current claim set.
        rc = recompile(q, q.get("claims", []), by_id, q.get("current_answer", ""), [])
        if not rc:
            sys.exit("recompile failed (no LLM).")
        q["current_answer"] = rc.get("current_answer", q.get("current_answer"))
        q["current_answer_pt"] = rc.get("current_answer_pt", q.get("current_answer_pt"))
        if rc.get("major_uncertainty"): q["major_uncertainty"] = rc["major_uncertainty"]
        if rc.get("major_uncertainty_pt"): q["major_uncertainty_pt"] = rc["major_uncertainty_pt"]
        if rc.get("bottom_line"): q["bottom_line"] = rc["bottom_line"]  # R-SITE-14 plain-language takeaway
        if rc.get("bottom_line_pt"): q["bottom_line_pt"] = rc["bottom_line_pt"]
        if rc.get("outcomes") is not None: q["outcomes"] = rc["outcomes"]  # R-Q-7 outcome breakdown
        q["version"] = bump(q.get("version", "1.0")); q["updated"] = TODAY
        q["compiled_by"] = compiled_by()  # R-AI-9: public AI provenance
        q.setdefault("history", []).insert(0, {"version": q["version"], "date": TODAY,
            "change": "Answer recompiled after human curation of the claim set.",
            "change_pt": "Resposta recompilada após curadoria humana dos claims.",
            "engine": q["compiled_by"]["model"]})
        print(f"  ↻ recompiled {qid} → v{q['version']}\n      {q['current_answer'][:240]}")
        if "--commit" in args:
            json.dump(qdata, open(QJSON, "w"), ensure_ascii=False, indent=2)
            db.sync(verbose=False); print("✓ written + DB synced. Next: build + deploy.")
        else:
            print("(dry-run — add --commit to write)")
        return

    doi_file = args[args.index("--doi-file") + 1] if "--doi-file" in args else None
    if doi_file:
        dois = [l.strip() for l in open(doi_file) if l.strip() and not l.startswith("#")]
        print(f"  ingesting {len(dois)} curated DOI(s) from {doi_file}")
        arts = ingest.fetch_dois(dois)
        cap = max(cap, len(dois))   # don't cap a deliberate curated list
    else:
        arts = ingest.gather(q, sources, from_year, n)
    # R-CLM-12: for lipedema, ALWAYS also search the author's own library so his work is considered/cited,
    # even on reading-list runs. De-dup by DOI. (Skip if gather already searched the library this run.)
    lib_already = (not doi_file) and ("library" in sources)
    if ingest.domain_of(qid) == "LIP" and ingest.bib_available() and not lib_already:
        seen_d = {(a.get("doi") or "").lower() for a in arts if a.get("doi")}
        extra = [a for a in ingest.bib_search(q["text"], max(n, 12)) if (a.get("doi") or "").lower() not in seen_d]
        if extra:
            print(f"  + {len(extra)} candidate(s) from the author's library (semantic)")
        arts = arts + extra
    # R-AI-12: ALWAYS run a contradiction-seeking retrieval pass (null/negative/opposing), in EVERY mode
    # (including reading-list runs) — so the evidence base is not confirmation-biased.
    seen_d = {(a.get("doi") or "").lower() for a in arts if a.get("doi")}
    contra = [a for a in ingest.gather_contra(q, from_year, max(n, 10)) if (a.get("doi") or "").lower() not in seen_d]
    if contra:
        print(f"  + {len(contra)} contradiction-seeking candidate(s) (null/negative/opposing)")
    arts = arts + contra
    # PER-QUESTION dedup (R-OBJ-4 graph): skip a paper already cited under THIS question, but allow a
    # paper used under OTHER questions to be ingested here — it yields this question's specific finding.
    dois, pmids = set(), set()
    for l in q.get("claims", []):
        for ev in by_id.get(l["id"], {}).get("evidence", []):
            r = (ev.get("ref") or "")
            if r.upper().startswith("DOI:"): dois.add(r[4:].lower())
            elif r.upper().startswith("PMID:"): pmids.add(r[5:])
    excl = ingest.excluded_set()
    new = [a for a in arts if ((a.get("doi") or "").lower() not in dois) and ((a.get("pmid") or "") not in pmids)
           and ((a.get("doi") or "").lower() not in excl)]
    print(f"  {len(arts)} candidates · {len(new)} not yet indexed\n")

    # CROSS-QUESTION dedup index (R-OBJ-7): DOI -> claim ids anywhere in the registry, so a paper already
    # claimed under another question can be LINKED here (graph) instead of minting a parallel duplicate.
    doi_index = {}
    for c in claims:
        for ev in c.get("evidence", []):
            r = (ev.get("ref") or "")
            if r.upper().startswith("DOI:"):
                doi_index.setdefault(r[4:].lower(), []).append(c["id"])

    promoted, merged, added = [], [], []
    for a in new:
        if len(promoted) + len(merged) >= cap:
            break
        cl = ingest.classify(q, a)
        if not cl.get("relevant"):
            print(f"  ·skip       {(a.get('title') or '')[:70]}"); continue
        ref = verify_ref(a.get("doi"), a.get("pmid"))
        if not ref:
            print(f"  ⚠ no verifiable ref (skipped)  {(a.get('doi') or a.get('pmid') or '?')}"); continue
        # R-AI-13/14: independent, adversarial verification of the extracted stance + sentence-level
        # provenance BEFORE the evidence enters. Disputed items are still recorded (registra, não
        # arbitra) but flagged needs_review and never allowed to read as confident fact.
        ver = ingest.verify_extraction(q, a, cl)
        vmark = {"verified": "✓verified", "disputed": "⚠DISPUTED", "unverified": "?unverified"}.get(ver["verdict"], "?")
        gq = "grounded" if ver.get("quote_grounded") else "NOT-grounded"
        if ver["verdict"] != "verified":
            print(f"    [{vmark}] stance_agreed={ver.get('stance_agreed')} quote={gq} "
                  f"(verifier={ingest.model_label(ver.get('verifier_model'))}): {ver.get('reason','')[:80]}")
        # try to CORROBORATE an existing linked claim before minting a new one
        existing = [{"id": l["id"], "statement": by_id.get(l["id"], {}).get("statement", ""), "role": l["role"]}
                    for l in q.get("claims", []) if l["id"] in by_id]
        m = match_existing(q, cl, existing)
        if m.get("match") and m.get("claim_id") in by_id:
            tgt = by_id[m["claim_id"]]
            add_evidence(tgt, a, cl, ref, ver)
            print(f"  ⇗ corroborates {tgt['id']}  +{ref}  [{vmark}]  ({(m.get('reason') or '')[:60]})")
            merged.append(tgt["id"]); added.append({"role": "supporting", "statement": cl.get("statement", "")})
            continue
        # CROSS-QUESTION dedup (R-OBJ-7): same paper already a claim under ANOTHER question with the SAME
        # finding? LINK it to this question (graph) instead of minting a parallel duplicate.
        adoi = (a.get("doi") or "").lower()
        qids_here = {l["id"] for l in q.get("claims", [])}
        xpaper = [{"id": cx, "statement": by_id.get(cx, {}).get("statement", ""), "role": "context"}
                  for cx in doi_index.get(adoi, []) if cx not in qids_here and cx in by_id]
        if xpaper:
            mx = match_existing(q, cl, xpaper)
            if mx.get("match") and mx.get("claim_id") in by_id and mx["claim_id"] not in qids_here:
                role = STANCE_ROLE.get(cl.get("stance"), "context")
                q.setdefault("claims", []).append({"id": mx["claim_id"], "role": role})
                print(f"  ⇄ links existing {mx['claim_id']} → {qid} (same finding under another question)")
                merged.append(mx["claim_id"]); added.append({"role": role, "statement": by_id[mx["claim_id"]].get("statement", "")})
                continue
        cid = next_claim_id(claims, domain)
        role = STANCE_ROLE.get(cl.get("stance"), "context")
        claim = make_claim(cid, qid, a, cl, ref, ver)
        print(f"  ✓ {cid}  [{role}]  [{vmark}]  {ref}")
        print(f"      {claim['statement']}")
        claims.append(claim); by_id[cid] = claim
        q.setdefault("claims", []).append({"id": cid, "role": role})
        promoted.append(cid); added.append({"role": role, "statement": claim["statement"]})

    if not promoted and not merged:
        print("\nNo new claims or corroborations."); return

    prior = q.get("current_answer", "")
    new_ver = bump(q.get("version", "1.0"))
    parts_en, parts_pt = [], []
    if promoted:
        parts_en.append(f"{len(promoted)} new claim(s) ({', '.join(promoted)})")
        parts_pt.append(f"{len(promoted)} claim(s) novo(s) ({', '.join(promoted)})")
    if merged:
        ms = ", ".join(sorted(set(merged)))
        parts_en.append(f"corroborated {len(set(merged))} claim(s) with new evidence ({ms})")
        parts_pt.append(f"corroborou {len(set(merged))} claim(s) com nova evidência ({ms})")
    change_en = "Layer 1 surveillance: " + "; ".join(parts_en) + "."
    change_pt = "Vigilância da Layer 1: " + "; ".join(parts_pt) + "."
    if recompile_on:
        rc = recompile(q, q["claims"], by_id, prior, added)
        if rc:
            q["current_answer"] = rc.get("current_answer", prior)
            q["current_answer_pt"] = rc.get("current_answer_pt", q.get("current_answer_pt"))
            if rc.get("major_uncertainty"): q["major_uncertainty"] = rc["major_uncertainty"]
            if rc.get("major_uncertainty_pt"): q["major_uncertainty_pt"] = rc["major_uncertainty_pt"]
            if rc.get("bottom_line"): q["bottom_line"] = rc["bottom_line"]  # R-SITE-14
            if rc.get("bottom_line_pt"): q["bottom_line_pt"] = rc["bottom_line_pt"]
            if rc.get("outcomes") is not None: q["outcomes"] = rc["outcomes"]  # R-Q-7 outcome breakdown
            change_en = rc.get("what_changed", change_en)
            change_pt = rc.get("what_changed_pt", change_pt)
            print("\n  ↻ recompiled answer:")
            print(f"      {q['current_answer']}")

    q["version"] = new_ver
    q["updated"] = TODAY
    q["compiled_by"] = compiled_by()  # R-AI-9: public AI provenance
    q.setdefault("history", [])
    q["history"].insert(0, {"version": new_ver, "date": TODAY, "change": change_en, "change_pt": change_pt,
                            "engine": q["compiled_by"]["model"]})
    # ensure the founding v1.0 is recorded in history (so the snapshot list is complete)
    if not any(h["version"] == "1.0" for h in q["history"]):
        q["history"].append({"version": "1.0", "date": qdata.get("date", "2026-05-30"),
                             "change": None, "change_pt": None})

    print(f"\n  → version {q['version']}  ·  what changed: {change_en}")
    if not commit:
        print("\n(dry-run — re-run with --commit to write claims.json + questions.json)")
        return
    cdata["count"] = len(claims)
    json.dump(cdata, open(CJSON, "w"), ensure_ascii=False, indent=2)
    json.dump(qdata, open(QJSON, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
    print(f"\n✓ {qid} → v{q['version']}: {len(promoted)} new claim(s), {len(set(merged))} corroborated. DB synced. "
          "Next: build_questions.py + build_site.py → rsync → purge.")


if __name__ == "__main__":
    main()
