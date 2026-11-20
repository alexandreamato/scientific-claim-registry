#!/usr/bin/env python3
"""Consolidate single-paper claims into GENERAL propositions (claims) backed by study-level findings.

Why: by 2026-11 87% of claims had exactly one source and read as paper abstracts (median 43 words, with n, %,
p-values). A claim should be a short proposition that several papers can support or contradict; the
study-specific result belongs in the evidence row under it. See RULES R-CLM-19.

Pipeline per question (fully automatic; only residual problems are left for a human):
  1. items      — the question's evidence, one item per distinct paper (same DOI/PMID merged).
  2. consolidate— PRIMARY model groups items into a few propositions (may REUSE propositions already created
                  for other questions that share papers: the claim graph, R-OBJ-4/7).
  3. validate   — deterministic: every item placed exactly once, no invented keys, <=25 words, no numbers,
                  valid labels. Failure → the model is told the exact errors and retries.
  4. verify     — INDEPENDENT model from another vendor (R-AI-14) checks each proposition against the union of
                  its findings AND the set as a whole (contradictions between propositions, caveats superseded by
                  stronger evidence elsewhere, two ideas in one sentence, the same study counted twice).
  5. repair     — verifier report goes back to the primary model; re-validate, re-verify (max REPAIR_ROUNDS).
  6. grade      — deterministic GRADE per proposition from its findings (R-CLM-11: strong outweighs weak).
Writes registry/consolidation/<qid>.json and the shared store registry/consolidation/propositions.json.
Nothing touches claims.json/questions.json (applying is a separate step).

  python3 consolidate.py SQ-LIP-000007 [more ids] | --all     [--force]
Models: SCR_CONSOLIDATE_MODEL (default anthropic/claude-opus-5.5), SCR_CONSOLIDATE_VERIFIER (openai/gpt-5.5)."""
import json, os, re, sys, datetime
import ingest

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "consolidation")
STORE = os.path.join(OUTDIR, "propositions.json")
PRIMARY = os.environ.get("SCR_CONSOLIDATE_MODEL", "anthropic/claude-opus-5.5")
VERIFIER = os.environ.get("SCR_CONSOLIDATE_VERIFIER", "openai/gpt-5.5")
REPAIR_ROUNDS = 2
FORMAT_RETRIES = 3
MAX_WORDS = 25
# A number, not a digit inside a gene or locus name (AKR1C1, HLA-DQ2 are allowed; "stage 3", "50%" are not).
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?![A-Za-z])")
STANCES = {"supporting", "contradicting", "refines", "context"}
ROLES = STANCES
GRADES = ["very_low", "low", "moderate", "high"]
STUDY_DESC = re.compile(r"^\s*(one|a|an|the|this|single|in (a|an|one|this))\b[^,.]{0,60}\b(study|studies|series|"
                        r"cohort|trial|report|review|meta-analysis|survey|analysis|patient|case)\b", re.I)

# Consolidation answers are long; the shared helper's 120 s timeout is too short for them.
_uo = ingest.urllib.request.urlopen
ingest.urllib.request.urlopen = lambda req, timeout=None: _uo(req, timeout=900)

SYS_CONS = """You restructure a scientific claim registry. Today each claim summarises ONE paper. Turn the evidence
for ONE question into a few GENERAL propositions that several papers can support or contradict.

A proposition (the "claim"):
- At most 25 words, ONE idea (never "X and also Y is durable": durability, safety, pain, QoL are separate ideas
  when their evidence differs). No digits at all: no sample sizes, percentages, p-values, ratios, years, stages
  written as numbers ("stage I-III" → "early and advanced stages"), no study names or countries.
- About the condition, not about a study. Testable: a future study could support or contradict it.
- Strength matches the evidence: descriptive/cross-sectional → "is frequently reported", "is associated with";
  causal or certain wording only if randomised/strong evidence licenses it. Add nothing absent from the findings.
- Never describe a study ("One cohort reported…", "A case report described…", "In a series…"). A result that
  only ONE study reports is normally placed under a broader proposition (stance refines/supporting); it becomes a
  proposition of its own only when it is a genuinely distinct idea, and then it is hedged ("may", "is reported").
- FEW propositions (typically 3-8). Merge findings that say the same thing in other populations.
- A finding that disagrees on the SAME outcome goes UNDER the proposition it challenges (stance contradicting/
  refines). A finding that qualifies the whole association on a DIFFERENT axis — an adjusted analysis showing no
  independent effect, confounding, controlled vs uncontrolled evidence — gets its OWN proposition (role refines or
  contradicting), so the caveat is visible and not buried.
- Never write a caveat that stronger evidence among the items already overturns (e.g. "controlled trials are
  lacking" when an RCT is among the items). Check the WHOLE item list before writing any caveat.
- REUSE: if an EXISTING proposition (key G-...) states the same idea, place items under it by its key instead of
  creating a twin. Do not reword existing propositions.

Every item E# goes exactly once, using ONLY the keys given (never invent keys such as "E12b"):
- under a proposition: {"e","stance","finding"} — stance relative to THAT proposition; finding = max 40 words,
  the study-specific result (numbers allowed), faithful to the old statement/quote. If the item only re-reports a
  result of ANOTHER item (a review quoting a primary study that is itself an item), add "secondary_of":"E#" and
  use stance "context"; or
- in "dropped" with a reason, ONLY if it is not a finding at all (states what a paper does NOT contain, a
  truncated abstract with no result, off-topic for the question). Weak or small is NOT a reason to drop.
Each proposition: {"key": new "P1".. or existing "G-...", "statement", "role" (relative to the question:
supporting|contradicting|refines|context), "rationale" (one sentence), "evidence":[...]}.
Return strict JSON: {"propositions":[...], "dropped":[{"e":"E7","reason":"..."}]}"""

SYS_VER = """You are an independent, adversarial verifier of a scientific claim registry. You get one question, its
evidence items (with quotes) and a proposed set of general propositions with findings placed under them.
Judge ONLY from the items. Check each proposition AND the set as a whole.
Per proposition (key):
- "supported": "yes"|"partly"|"no" — do its SUPPORTING findings, together, support the statement as worded?
- "overgeneralized": true if wording claims more than the findings license (causal/certain from descriptive data,
  population/outcome not covered, a fact in none of the findings, a single study stated as a general rule).
- "compound": true if it bundles two ideas whose evidence differs.
- "stance_errors": [E#] wrongly labelled for this proposition; "misplaced": [E#] that belong elsewhere.
- "suggested_statement": corrected wording (<=25 words, no digits) when any problem above, else "". It must stay a
  GENERAL proposition about the condition, hedged if the support is thin ("may", "is reported", "limited
  evidence suggests"); NEVER a description of a study ("One series reported…", "A case report…").
- "severity": "major" if the statement is unsupported, overgeneralized, contradicted by an item, or contains
  wrong stances that change its meaning; "minor" for wording, style or bookkeeping; "none" if fine.
NOT issues (never flag): a meta-analysis or systematic review placed alongside primary studies it may pool — this
overlap is normal in evidence synthesis; only flag double counting when a NARRATIVE review re-reports one specific
primary study that is itself an item.
Set level ("set_issues": list of {"issue","severity":"major"|"minor"}, empty if none): contradictions between propositions; a caveat or
negative proposition that a stronger item elsewhere overturns; the same study counted twice (a review re-reporting
an included primary study without "secondary_of"); an important finding with no proposition; twin propositions.
Return strict JSON: {"verdicts":[{"key","supported","overgeneralized","compound","stance_errors","misplaced",
"suggested_statement","severity","note"}],"set_issues":[]}"""

SYS_REPAIR = SYS_CONS + """

You are now REVISING your earlier proposal. You get it plus an independent verifier's report. Fix every problem the
report raises (rewrite, split, merge, move or relabel), unless the report is clearly wrong about the items — then
keep your version and say why in that proposition's "rationale". Return the full corrected JSON in the same format."""


def _norm_ref(r):
    return (r or "").strip().lower()


def load():
    Q = {q["id"]: q for q in json.load(open(os.path.join(HERE, "questions.json")))["questions"]}
    C = {c["id"]: c for c in json.load(open(os.path.join(HERE, "claims.json")))["claims"]}
    return Q, C


def build_items(q, C):
    by_ref, items = {}, []
    for link in q["claims"]:
        c = C.get(link["id"])
        if not c:
            continue
        for ev in c["evidence"]:
            key = _norm_ref(ev.get("ref")) or f"{c['id']}:{len(items)}"
            if key in by_ref:
                it = by_ref[key]
                if c["id"] not in it["old_claims"]:
                    it["old_claims"].append(c["id"])
                    it["old_statements"].append(c["statement"])
                continue
            it = {"e": f"E{len(items) + 1}", "ref": ev.get("ref"), "title": ev.get("title"),
                  "year": ev.get("year"), "design": ev.get("study_design"), "n": ev.get("n"),
                  "grade": ev.get("grade"), "risk_of_bias": ev.get("risk_of_bias"),
                  "quote": ev.get("quote"), "note": ev.get("note"),
                  "old_claims": [c["id"]], "old_statements": [c["statement"]],
                  "old_role_in_question": link["role"]}
            by_ref[key] = it
            items.append(it)
    return items


def related_store(store, items):
    refs = {_norm_ref(i["ref"]) for i in items}
    return [{"key": k, "statement": p["statement"], "questions": p["questions"]}
            for k, p in store.items() if refs & {_norm_ref(r) for r in p["refs"]}]


def validate(cons, items, store_keys):
    errs, keys = [], {i["e"] for i in items}
    props = cons.get("propositions")
    if not isinstance(props, list) or not props:
        return ["no propositions"]
    placed = []
    for p in props:
        k, s = p.get("key", "?"), p.get("statement", "")
        if not (re.fullmatch(r"P\d+", k) or k in store_keys):
            errs.append(f"{k}: invalid key (use P1.. or an existing G- key)")
        if len(s.split()) > MAX_WORDS:
            errs.append(f"{k}: statement has {len(s.split())} words (max {MAX_WORDS})")
        if STUDY_DESC.match(s):
            errs.append(f"{k}: statement describes a study instead of stating a proposition: {s!r}")
        if NUMBER.search(s):
            errs.append(f"{k}: statement contains a digit: {s!r}")
        if p.get("role") not in ROLES:
            errs.append(f"{k}: invalid role {p.get('role')!r}")
        if not p.get("evidence"):
            errs.append(f"{k}: no evidence placed")
        for x in p.get("evidence", []):
            if x.get("e") not in keys:
                errs.append(f"{k}: unknown item key {x.get('e')!r} — use only the given keys")
            if x.get("stance") not in STANCES:
                errs.append(f"{k}/{x.get('e')}: invalid stance {x.get('stance')!r}")
            if not (x.get("finding") or "").strip() or "placeholder" in (x.get("finding") or "").lower():
                errs.append(f"{k}/{x.get('e')}: empty finding")
            so = x.get("secondary_of")
            if so and so not in keys:
                errs.append(f"{k}/{x.get('e')}: secondary_of {so!r} is not an item")
            placed.append(x.get("e"))
    for d in cons.get("dropped", []):
        if d.get("e") not in keys:
            errs.append(f"dropped: unknown item key {d.get('e')!r}")
        placed.append(d.get("e"))
    for e in sorted(keys - set(placed), key=lambda s: int(s[1:])):
        errs.append(f"{e}: not placed anywhere")
    for e in sorted({e for e in placed if placed.count(e) > 1 and e in keys}):
        errs.append(f"{e}: placed more than once")
    return errs


def call_valid(system, user, items, store_keys, log):
    msg = user
    for attempt in range(FORMAT_RETRIES):
        cons = ingest._chat_json(system, msg, model=PRIMARY)
        errs = validate(cons, items, store_keys)
        log.append({"step": "format_check", "attempt": attempt + 1, "errors": errs})
        if not errs:
            return cons
        msg = (user + "\n\nYOUR PREVIOUS ANSWER WAS REJECTED by the format checker. Fix exactly these errors and "
               "return the full JSON again:\n- " + "\n- ".join(errs) +
               "\n\nPrevious answer:\n" + json.dumps(cons, ensure_ascii=False))
    raise RuntimeError(f"format still invalid after {FORMAT_RETRIES} attempts: {errs}")


def verify(q, items, cons, store):
    byE = {i["e"]: i for i in items}
    props = []
    for p in cons["propositions"]:
        props.append({"key": p["key"], "statement": p["statement"], "role": p["role"],
                      "findings": [{"e": x["e"], "stance": x["stance"], "finding": x["finding"],
                                    "secondary_of": x.get("secondary_of")} for x in p["evidence"]]})
    payload = {"question": q["text"],
               "items": [{k: byE[e][k] for k in ("e", "ref", "title", "year", "design", "n", "grade", "quote")}
                         | {"old_statement": byE[e]["old_statements"][0]} for e in byE],
               "propositions": props, "dropped": cons.get("dropped", [])}
    return ingest._chat_json(SYS_VER, json.dumps(payload, ensure_ascii=False, indent=1), model=VERIFIER)


def problems(ver, major_only=False):
    out = []
    for si in ver.get("set_issues") or []:
        sev = si.get("severity", "major") if isinstance(si, dict) else "major"
        txt = si.get("issue") if isinstance(si, dict) else str(si)
        if not major_only or sev == "major":
            out.append(f"[{sev}] set: {txt}")
    for v in ver.get("verdicts", []):
        sev = v.get("severity") or "major"
        if sev == "none" or (major_only and sev != "major"):
            continue
        flags = [f for f, bad in (("not fully supported", v.get("supported") != "yes"),
                                  ("overgeneralized", v.get("overgeneralized")),
                                  ("two ideas", v.get("compound")),
                                  (f"stance errors {v.get('stance_errors')}", v.get("stance_errors")),
                                  (f"misplaced {v.get('misplaced')}", v.get("misplaced"))) if bad]
        if flags:
            out.append(f"[{sev}] {v.get('key')}: " + "; ".join(flags) +
                       (f" — suggested: {v['suggested_statement']}" if v.get("suggested_statement") else "") +
                       (f" ({v['note']})" if v.get("note") else ""))
    return out


def grade_of(p, byE):
    """R-CLM-11: the proposition's certainty is the best certainty among its own (non-secondary) supporting
    findings, one level down when a finding of equal or higher certainty contradicts it."""
    def g(e):
        return GRADES.index(byE[e]["grade"]) if byE[e].get("grade") in GRADES else 0
    sup = [x["e"] for x in p["evidence"] if x["stance"] == "supporting" and not x.get("secondary_of")]
    con = [x["e"] for x in p["evidence"] if x["stance"] == "contradicting" and not x.get("secondary_of")]
    if not sup:
        return None
    best = max(g(e) for e in sup)
    if con and max(g(e) for e in con) >= best:
        best = max(best - 1, 0)
    return GRADES[best]


def consolidate(qid, Q, C, store):
    q = Q[qid]
    items = build_items(q, C)
    byE = {i["e"]: i for i in items}
    existing = related_store(store, items)
    store_keys = {x["key"] for x in existing}
    user = (f"QUESTION {qid}: {q['text']}\n\nEXISTING PROPOSITIONS that share papers with this question "
            f"(reuse by key when the idea is the same):\n{json.dumps(existing, ensure_ascii=False, indent=1)}\n\n"
            f"ITEMS ({len(items)}):\n{json.dumps(items, ensure_ascii=False, indent=1)}")
    log = []
    cons = call_valid(SYS_CONS, user, items, store_keys, log)
    ver = verify(q, items, cons, store)
    probs = problems(ver)
    log.append({"step": "verify", "round": 0, "problems": probs})
    for rnd in range(1, REPAIR_ROUNDS + 1):
        if not problems(ver, major_only=True):
            break  # only minor points left: not worth another rewrite
        rep_user = (user + "\n\nYOUR EARLIER PROPOSAL:\n" + json.dumps(cons, ensure_ascii=False) +
                    "\n\nINDEPENDENT VERIFIER REPORT:\n- " + "\n- ".join(probs))
        cons = call_valid(SYS_REPAIR, rep_user, items, store_keys, log)
        ver = verify(q, items, cons, store)
        probs = problems(ver)
        log.append({"step": "verify", "round": rnd, "problems": probs})
    major = problems(ver, major_only=True)
    if major:
        # Final arbitration (automatic): adopt the verifier's more cautious wording for propositions it still
        # flags as major, keep it only if it passes the format checker, and confirm with one last verification.
        sugg = {v["key"]: v.get("suggested_statement") for v in ver.get("verdicts", [])
                if v.get("severity") == "major" and v.get("suggested_statement")}
        changed = False
        for p in cons["propositions"]:
            new = sugg.get(p["key"])
            if new and len(new.split()) <= MAX_WORDS and not NUMBER.search(new) and not STUDY_DESC.match(new):
                p["statement_before_arbitration"] = p["statement"]
                p["statement"], p["wording_source"], changed = new, "verifier", True
        if changed:
            ver = verify(q, items, cons, store)
            log.append({"step": "verify", "round": "arbitration", "problems": problems(ver)})
        major = problems(ver, major_only=True)
    probs = problems(ver)
    for p in cons["propositions"]:
        p["grade"] = grade_of(p, byE)
        p["n_findings"] = sum(1 for x in p["evidence"] if not x.get("secondary_of"))
    out = {"question": qid, "text": q["text"], "n_old_claims": len(q["claims"]), "n_items": len(items),
           "status": "needs_review" if major else "clean", "major_problems": major, "minor_problems":
           [x for x in probs if x not in major],
           "models": {"primary": PRIMARY, "verifier": VERIFIER},
           "created": datetime.date.today().isoformat(),
           "items": items, "propositions": cons["propositions"], "dropped": cons.get("dropped", []),
           "verification": ver, "log": log}
    json.dump(out, open(os.path.join(OUTDIR, f"{qid}.json"), "w"), ensure_ascii=False, indent=1)
    # Register propositions in the shared store so later questions can reuse them (claim graph).
    nxt = 1 + max([int(k[2:]) for k in store] or [0])
    for p in cons["propositions"]:
        refs = [byE[x["e"]]["ref"] for x in p["evidence"] if x["e"] in byE]
        if p["key"].startswith("G-"):
            sp = store[p["key"]]
            sp["questions"] = sorted(set(sp["questions"]) | {qid})
            sp["refs"] = sorted(set(sp["refs"]) | set(r for r in refs if r))
        else:
            gk = f"G-{nxt:05d}"; nxt += 1
            store[gk] = {"statement": p["statement"], "questions": [qid], "refs": sorted(r for r in refs if r)}
            p["store_key"] = gk
    json.dump(out, open(os.path.join(OUTDIR, f"{qid}.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(store, open(STORE, "w"), ensure_ascii=False, indent=1)
    rounds = sum(1 for l in log if l["step"] == "verify") - 1
    print(f"{qid}: {len(q['claims'])} claims / {len(items)} papers → {len(cons['propositions'])} propositions, "
          f"{len(cons.get('dropped', []))} dropped, {rounds} repair round(s), status={out['status']}"
          + f" ({len(major)} major, {len(probs) - len(major)} minor left)")
    return out


# ---------------------------------------------------------------------------------------------------------------
# Agent mode (no API spend): the same pipeline, but the thinking is done by Claude Code subagents that read the
# prompt files below and write JSON answers. Everything deterministic (items, validation, store, GRADE, status)
# stays here, so the result is identical in shape and checked by the same code.
#   prep QID              → work/QID.cons_prompt.md   (system + user prompt for the consolidator)
#   check QID CONS.json   → format errors, or OK
#   prep-verify QID CONS  → work/QID.ver_prompt.md    (for an independent verifier with a fresh context)
#   repair-prompt QID CONS VER → work/QID.repair_prompt.md (only if major problems)
#   finish QID CONS VER [primary_label verifier_label] → consolidation/QID.json + store
WORK = os.path.join(OUTDIR, "work")


def _ctx(qid):
    Q, C = load()
    store = json.load(open(STORE)) if os.path.exists(STORE) else {}
    q = Q[qid]
    items = build_items(q, C)
    return q, items, store


def _user_prompt(qid, q, items, store):
    existing = related_store(store, items)
    return existing, (f"QUESTION {qid}: {q['text']}\n\nEXISTING PROPOSITIONS that share papers with this question "
                      f"(reuse by key when the idea is the same):\n{json.dumps(existing, ensure_ascii=False, indent=1)}"
                      f"\n\nITEMS ({len(items)}):\n{json.dumps(items, ensure_ascii=False, indent=1)}")


def agent_prep(qid):
    os.makedirs(WORK, exist_ok=True)
    q, items, store = _ctx(qid)
    existing, user = _user_prompt(qid, q, items, store)
    p = os.path.join(WORK, f"{qid}.cons_prompt.md")
    open(p, "w").write(f"# SYSTEM\n\n{SYS_CONS}\n\n# INPUT\n\n{user}\n")
    json.dump({"existing_keys": [x["key"] for x in existing]}, open(os.path.join(WORK, f"{qid}.keys.json"), "w"))
    print(p)


def _load_cons(path):
    """Reused G- propositions keep the store's wording verbatim (never reworded), so fill it in from the store."""
    cons = json.load(open(path))
    store = json.load(open(STORE)) if os.path.exists(STORE) else {}
    for p in cons.get("propositions", []):
        k = p.get("key", "")
        if k.startswith("G-") and k in store:
            p["statement"] = store[k]["statement"]
    return cons


def _keys(qid):
    kp = os.path.join(WORK, f"{qid}.keys.json")
    return set(json.load(open(kp))["existing_keys"]) if os.path.exists(kp) else set()


def agent_check(qid, cons_path):
    q, items, store = _ctx(qid)
    errs = validate(_load_cons(cons_path), items, _keys(qid))
    print("OK" if not errs else "ERRORS:\n- " + "\n- ".join(errs))
    return not errs


def agent_prep_verify(qid, cons_path):
    q, items, store = _ctx(qid)
    cons = _load_cons(cons_path)
    byE = {i["e"]: i for i in items}
    props = [{"key": p["key"], "statement": p["statement"], "role": p["role"],
              "findings": [{"e": x["e"], "stance": x["stance"], "finding": x["finding"],
                            "secondary_of": x.get("secondary_of")} for x in p["evidence"]]}
             for p in cons["propositions"]]
    payload = {"question": q["text"],
               "items": [{k: byE[e][k] for k in ("e", "ref", "title", "year", "design", "n", "grade", "quote")}
                         | {"old_statement": byE[e]["old_statements"][0]} for e in byE],
               "propositions": props, "dropped": cons.get("dropped", [])}
    p = os.path.join(WORK, f"{qid}.ver_prompt.md")
    open(p, "w").write(f"# SYSTEM\n\n{SYS_VER}\n\n# INPUT\n\n{json.dumps(payload, ensure_ascii=False, indent=1)}\n")
    print(p)


def agent_repair_prompt(qid, cons_path, ver_path):
    q, items, store = _ctx(qid)
    _, user = _user_prompt(qid, q, items, store)
    probs = problems(json.load(open(ver_path)))
    p = os.path.join(WORK, f"{qid}.repair_prompt.md")
    open(p, "w").write(f"# SYSTEM\n\n{SYS_REPAIR}\n\n# INPUT\n\n{user}\n\nYOUR EARLIER PROPOSAL:\n"
                       f"{open(cons_path).read()}\n\nINDEPENDENT VERIFIER REPORT:\n- " + "\n- ".join(probs) + "\n")
    print(p)


def agent_finish(qid, cons_path, ver_path, primary="claude-code-subagent", verifier="claude-code-subagent"):
    Q, C = load()
    store = json.load(open(STORE)) if os.path.exists(STORE) else {}
    q = Q[qid]
    items = build_items(q, C)
    byE = {i["e"]: i for i in items}
    cons, ver = _load_cons(cons_path), json.load(open(ver_path))
    errs = validate(cons, items, _keys(qid))
    if errs:
        sys.exit("format invalid:\n- " + "\n- ".join(errs))
    # A G- key may have been created by a question finished in parallel; only accept keys that exist now.
    major, probs = problems(ver, major_only=True), problems(ver)
    for p in cons["propositions"]:
        p["grade"] = grade_of(p, byE)
        p["n_findings"] = sum(1 for x in p["evidence"] if not x.get("secondary_of"))
    out = {"question": qid, "text": q["text"], "n_old_claims": len(q["claims"]), "n_items": len(items),
           "status": "needs_review" if major else "clean", "major_problems": major,
           "minor_problems": [x for x in probs if x not in major],
           "models": {"primary": primary, "verifier": verifier, "mode": "agent"},
           "created": datetime.date.today().isoformat(),
           "items": items, "propositions": cons["propositions"], "dropped": cons.get("dropped", []),
           "verification": ver, "log": [{"step": "agent_mode", "cons": os.path.basename(cons_path),
                                         "ver": os.path.basename(ver_path)}]}
    for k in [k for k, p in store.items() if qid in p["questions"]]:
        store[k]["questions"].remove(qid)
        if not store[k]["questions"]:
            del store[k]
    nxt = 1 + max([int(k[2:]) for k in store] or [0])
    for p in cons["propositions"]:
        refs = [byE[x["e"]]["ref"] for x in p["evidence"] if x["e"] in byE]
        if p["key"].startswith("G-") and p["key"] in store:
            sp = store[p["key"]]
            sp["questions"] = sorted(set(sp["questions"]) | {qid})
            sp["refs"] = sorted(set(sp["refs"]) | set(r for r in refs if r))
            p["store_key"] = p["key"]
        else:
            gk = f"G-{nxt:05d}"; nxt += 1
            store[gk] = {"statement": p["statement"], "questions": [qid], "refs": sorted(r for r in refs if r)}
            p["store_key"] = gk
    json.dump(out, open(os.path.join(OUTDIR, f"{qid}.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(store, open(STORE, "w"), ensure_ascii=False, indent=1)
    print(f"{qid}: {len(q['claims'])} claims / {len(items)} papers → {len(cons['propositions'])} propositions, "
          f"{len(cons.get('dropped', []))} dropped, status={out['status']} ({len(major)} major, "
          f"{len(probs) - len(major)} minor)")


def store_listing(out_path):
    """All store propositions, for a twin-detection pass (written to a file an agent can read)."""
    store = json.load(open(STORE))
    lines = [f"{k}\t{','.join(v['questions'])}\t{v['statement']}" for k, v in sorted(store.items())]
    open(out_path, "w").write("key\tquestions\tstatement\n" + "\n".join(lines) + "\n")
    print(f"{len(lines)} propositions → {out_path}")


def merge_twins(map_path):
    """map: {"G-x": "G-y", ...} — x states the same idea as y. y keeps its wording; x's questions, refs and
    findings move to y; a question that had both gets one proposition (evidence unioned). R-OBJ-7: no twins."""
    mp = json.load(open(map_path))
    store = json.load(open(STORE))
    for x, y in mp.items():
        if x not in store or y not in store or x == y:
            print(f"skip {x}→{y}"); continue
        store[y]["questions"] = sorted(set(store[y]["questions"]) | set(store[x]["questions"]))
        store[y]["refs"] = sorted(set(store[y]["refs"]) | set(store[x]["refs"]))
        store[y].setdefault("merged_twins", []).append({"key": x, "statement": store[x]["statement"]})
        for qid in store[x]["questions"]:
            f = os.path.join(OUTDIR, f"{qid}.json")
            res = json.load(open(f))
            keep = None
            for p in [p for p in res["propositions"] if p.get("store_key") in (x, y)]:
                if keep is None:
                    keep = p
                    if p["store_key"] == x:
                        p["statement_before_twin_merge"] = p["statement"]
                    p["store_key"], p["statement"] = y, store[y]["statement"]
                else:
                    keep["evidence"] += p["evidence"]
                    res["propositions"].remove(p)
            if keep is not None:
                byE = {i["e"]: i for i in res["items"]}
                keep["grade"] = grade_of(keep, byE)
                keep["n_findings"] = sum(1 for e in keep["evidence"] if not e.get("secondary_of"))
            res.setdefault("log", []).append({"step": "merge_twins", "from": x, "into": y})
            json.dump(res, open(f, "w"), ensure_ascii=False, indent=1)
        del store[x]
        print(f"{x} → {y}")
    json.dump(store, open(STORE, "w"), ensure_ascii=False, indent=1)


def agent_arbitrate(qid, cons_path, ver_path):
    """Automatic tiebreak after the repair round (same rule as API mode): for each proposition still flagged
    major, adopt the verifier's suggested wording if it passes the format checks. Writes <qid>.consA/.verA.json.
    Recorded as arbitration, not re-verified."""
    cons, ver = _load_cons(cons_path), json.load(open(ver_path))
    sug = {v["key"]: v.get("suggested_statement") for v in ver.get("verdicts", []) if v.get("severity") == "major"}
    done = []
    for p in cons["propositions"]:
        new = sug.get(p["key"])
        if new and not p["key"].startswith("G-") and len(new.split()) <= MAX_WORDS and not NUMBER.search(new) \
                and not STUDY_DESC.match(new):
            p["statement_before_arbitration"], p["statement"], p["wording_source"] = p["statement"], new, "verifier"
            done.append(p["key"])
    for v in ver.get("verdicts", []):
        if v["key"] in done:
            v["severity"], v["resolution"] = "minor", "arbitration: verifier wording adopted (not re-verified)"
    for si in ver.get("set_issues") or []:
        if isinstance(si, dict) and si.get("severity") == "major" and any(k in si.get("issue", "") for k in done):
            si["severity"], si["resolution"] = "minor", "resolved by arbitration on " + ", ".join(done)
    base = os.path.join(WORK, qid)
    json.dump(cons, open(base + ".consA.json", "w"), ensure_ascii=False, indent=1)
    json.dump(ver, open(base + ".verA.json", "w"), ensure_ascii=False, indent=1)
    print(f"{qid}: arbitration on {done or 'nothing'}; left major: {problems(ver, major_only=True)}")


AGENT_CMDS = {"arbitrate": agent_arbitrate, "store-listing": store_listing, "merge-twins": merge_twins, "prep": agent_prep, "check": agent_check, "prep-verify": agent_prep_verify,
              "repair-prompt": agent_repair_prompt, "finish": agent_finish}


def openrouter_balance():
    """Remaining OpenRouter credit in US$, or None if it cannot be read."""
    try:
        tok = open(os.path.expanduser("~/.config/scr_openrouter_token")).read().strip()
        req = ingest.urllib.request.Request("https://openrouter.ai/api/v1/credits",
                                            headers={"Authorization": f"Bearer {tok}"})
        d = json.loads(_uo(req, timeout=30).read())["data"]
        return d["total_credits"] - d["total_usage"]
    except Exception:
        return None


# Stop before the balance drops below this floor, so the weekly cron still has credit to run.
MIN_BALANCE = float(os.environ.get("SCR_CONSOLIDATE_MIN_BALANCE", "3"))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[1] in AGENT_CMDS:
        r = AGENT_CMDS[sys.argv[1]](*sys.argv[2:])
        sys.exit(0 if r is not False else 1)
    Q, C = load()
    store = json.load(open(STORE)) if os.path.exists(STORE) else {}
    ids = sorted(Q) if "--all" in sys.argv else [a for a in sys.argv[1:] if a.startswith("SQ-")]
    for qid in ids:
        if os.path.exists(os.path.join(OUTDIR, f"{qid}.json")) and "--force" not in sys.argv:
            print(f"{qid}: already consolidated (use --force)"); continue
        bal = openrouter_balance()
        if bal is not None and bal < MIN_BALANCE:
            print(f"STOP: OpenRouter balance US$ {bal:.2f} < floor US$ {MIN_BALANCE:.2f}. "
                  f"Recharge and rerun; finished questions are skipped."); break
        for k in [k for k, p in store.items() if qid in p["questions"]]:
            store[k]["questions"].remove(qid)
            if not store[k]["questions"]:
                del store[k]
        try:
            consolidate(qid, Q, C, store)
        except Exception as e:
            print(f"{qid}: FAILED — {e}")


if __name__ == "__main__":
    main()
