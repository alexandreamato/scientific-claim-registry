#!/usr/bin/env python3
"""submit.py — the contribution door (R-CONTRIB-1…4). The technical realization of the SCR Protocol's
open-creation + suggestion-only contribution surface (docs/spec/PROTOCOL.md §12).

SAFETY INVARIANT (R-CONTRIB-2): this tool NEVER writes a claim or an answer into the published registry.
It only writes to a QUEUE (`submissions.json`). Content enters the registry exclusively through the
neutral compiler (the surveillance loop) at the `process` step — so a contribution is an *input*, never
an *output*. Worst case of abuse = wasted compute, not a corrupted claim.

What a contributor may do:
  • PROPOSE A QUESTION  → identity-gated (dedup judge, R-Q-5); mints a TEMP id or links to an existing SQ.
  • SUGGEST AN ARTICLE  → a DOI/PMID "to be considered" for a question; verified to resolve; queued.
Both are attributable (ORCID, R-CONTRIB-3). Processing runs on whatever LLM key is configured — the
contributor's/institution's own key works (BYO-compute, R-CONTRIB-4).

Usage (run from registry/):
  submit.py question --text "..." [--text-pt "..."] [--domain LIP] --orcid 0000-0000-0000-0000 [--commit]
  submit.py suggest  --doi 10.x/y (or --pmid N) (--question SQ-LIP-000001 | --question-text "...")
                     --orcid 0000-... [--note "why"] [--commit]
  submit.py list [--status pending|duplicate|promoted|processed]
  submit.py process [--id SUB-000001] [--commit]
"""
import json, os, re, sys, subprocess, tempfile, datetime
import ingest, phrasings, db

HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
CF = os.path.join(HERE, "claims.json")
DF = os.path.join(HERE, "domains.json")
SF = os.path.join(HERE, "submissions.json")
TODAY = datetime.date.today().isoformat()
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


# ── small IO helpers ─────────────────────────────────────────────────────────
def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default

def save(p, data):
    json.dump(data, open(p, "w"), ensure_ascii=False, indent=2)

def queue():
    return load(SF, {"submissions": []})

def save_queue(q):
    save(SF, q)

def active_domains():
    return {d["code"]: d for d in load(DF, {"domains": []})["domains"] if d.get("status") == "active"}

def arg(args, name, default=None):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

def require_orcid(orcid):
    if not orcid or not ORCID_RE.match(orcid):
        sys.exit("✗ a valid --orcid is required (R-CONTRIB-3), e.g. 0000-0003-4008-4029")
    return orcid


# ── id allocation (R-ID / R-ALLOC) ───────────────────────────────────────────
def _seqs(ids, prefix, domain, temp):
    out = []
    for i in ids:
        m = re.match(rf"^{prefix}-{domain}-(D?)(\d+)$", i)
        if m and bool(m.group(1)) == temp:
            out.append(int(m.group(2)))
    return out

def next_final(prefix, domain, ids):
    s = _seqs(ids, prefix, domain, temp=False)
    return f"{prefix}-{domain}-{(max(s) + 1 if s else 1):06d}"

def next_temp(prefix, domain, ids):
    s = _seqs(ids, prefix, domain, temp=True)
    return f"{prefix}-{domain}-D{(max(s) + 1 if s else 1):06d}"


# ── identity gate for questions (R-ALLOC-4: identity, not truth) ──────────────
def resolve_question(text, questions):
    """Returns (verdict, sq_id_or_None). 'same'→link to existing; else novel/related→new."""
    if not ingest.provider():
        return {"verdict": "novel", "sq_id": None, "confidence": 0.0, "reason": "no LLM; cannot dedup"}, None
    v = phrasings.judge_same(text, questions)
    if phrasings.is_auto_merge(v):
        return v, v.get("sq_id")
    return v, None


# ── commands ─────────────────────────────────────────────────────────────────
def cmd_question(args):
    text = arg(args, "--text"); text_pt = arg(args, "--text-pt", "")
    domain = (arg(args, "--domain", "LIP") or "LIP").upper()
    orcid = require_orcid(arg(args, "--orcid"))
    commit = "--commit" in args
    if not text:
        sys.exit("✗ --text is required")
    doms = active_domains()
    if domain not in doms:
        sys.exit(f"✗ domain '{domain}' is not in the canonical dictionary (R-ID-8). "
                 f"Active: {', '.join(sorted(doms))}. Add it to domains.json first.")
    questions = load(QF, {"questions": []})["questions"]
    q = queue()
    verdict, sq_id = resolve_question(text, questions)
    print(f"identity check → {verdict.get('verdict')} (conf {verdict.get('confidence')}) {verdict.get('reason','')}")
    if sq_id:
        existing = next((x for x in questions if x["id"] == sq_id), None)
        print(f"⇄ already exists as {sq_id}: {existing['text'] if existing else ''}")
        rec = {"type": "question", "status": "duplicate", "resolved_id": sq_id,
               "text": text, "orcid": orcid, "verdict": verdict, "created": TODAY}
    else:
        existing_ids = [x["id"] for x in questions] + [s.get("temp_id", "") for s in q["submissions"]]
        temp = next_temp("SQ", domain, existing_ids)
        print(f"+ new question → TEMP {temp} (status pending until processed)")
        rec = {"type": "question", "status": "pending", "temp_id": temp, "domain": domain,
               "text": text, "text_pt": text_pt, "orcid": orcid, "verdict": verdict, "created": TODAY}
    rec["id"] = f"SUB-{len(q['submissions']) + 1:06d}"
    if commit:
        q["submissions"].append(rec); save_queue(q)
        print(f"✓ queued {rec['id']} ({rec['status']}).")
    else:
        print(f"(dry-run; add --commit to queue {rec['id']})")


def cmd_suggest(args):
    doi = arg(args, "--doi"); pmid = arg(args, "--pmid")
    qid = arg(args, "--question"); qtext = arg(args, "--question-text")
    note = arg(args, "--note", ""); orcid = require_orcid(arg(args, "--orcid"))
    commit = "--commit" in args
    if not (doi or pmid):
        sys.exit("✗ one of --doi / --pmid is required")
    if not (qid or qtext):
        sys.exit("✗ a target is required: --question SQ-… or --question-text \"…\"")
    ref = (f"DOI:{doi.strip().lower()}" if doi else f"PMID:{pmid.strip()}")

    # R-CONTRIB-2 / R-AI-4: the suggested reference MUST resolve before it can be queued.
    print(f"verifying {ref} resolves…")
    art = ingest.fetch_dois([doi])[0] if doi else None
    if doi and not (art and (art.get("title") or art.get("doi"))):
        sys.exit(f"✗ {ref} did not resolve (Crossref/Europe PMC). Not queued.")
    if art:
        print(f"  ✓ {(art.get('title') or '')[:80]}")

    questions = load(QF, {"questions": []})["questions"]
    q = queue()
    target, qstatus = qid, None
    if not target:                       # suggestion carries a (possibly new) question
        verdict, sq = resolve_question(qtext, questions)
        if sq:
            target = sq; print(f"⇄ target question resolved to existing {sq}")
        else:
            existing_ids = [x["id"] for x in questions] + [s.get("temp_id", "") for s in q["submissions"]]
            target = next_temp("SQ", "LIP", existing_ids)
            qstatus = {"new_question": qtext, "verdict": verdict, "temp_id": target}
            print(f"+ target is a NEW question → TEMP {target}")
    elif not any(x["id"] == target for x in questions):
        # a TEMP id is valid if it names a not-yet-processed proposed question in the queue
        is_temp_in_queue = (str(target).split("-")[-1].startswith("D")
                            and any(s.get("temp_id") == target for s in q["submissions"]))
        if not is_temp_in_queue:
            sys.exit(f"✗ --question {target} not found (neither a published SQ nor a queued TEMP).")

    rec = {"id": f"SUB-{len(q['submissions']) + 1:06d}", "type": "suggestion", "status": "pending",
           "ref": ref, "question": target, "note": note, "orcid": orcid, "created": TODAY,
           "article": {"title": (art or {}).get("title"), "doi": (art or {}).get("doi")}}
    if qstatus:
        rec["proposes_question"] = qstatus
    if commit:
        q["submissions"].append(rec); save_queue(q)
        print(f"✓ queued {rec['id']} — suggestion for {target}.")
    else:
        print(f"(dry-run; add --commit to queue {rec['id']})")


def cmd_list(args):
    status = arg(args, "--status")
    subs = queue()["submissions"]
    subs = [s for s in subs if not status or s.get("status") == status]
    if not subs:
        print("(queue empty)"); return
    for s in subs:
        tgt = s.get("resolved_id") or s.get("temp_id") or s.get("question") or "—"
        what = s.get("text") or s.get("ref") or ""
        print(f"  {s['id']}  {s['type']:<10} {s['status']:<9} {tgt:<18} {s.get('orcid','')}  {what[:54]}")


def cmd_process(args):
    only = arg(args, "--id"); commit = "--commit" in args
    q = queue()
    pend = [s for s in q["submissions"] if s.get("status") == "pending" and (not only or s["id"] == only)]
    if not pend:
        print("(nothing pending)"); return
    qdata = load(QF, {"questions": []})
    questions = qdata["questions"]

    for s in pend:
        print(f"\n▶ {s['id']} ({s['type']})  by {s.get('orcid')}")
        if s["type"] == "question":
            domain = s.get("domain", "LIP")
            final = next_final("SQ", domain, [x["id"] for x in questions])
            print(f"  promote {s['temp_id']} → {final}  ·  {s['text'][:70]}")
            if commit:
                questions.append({
                    "id": final, "text": s["text"], "text_pt": s.get("text_pt", ""),
                    "phrasings": [], "phrasings_pt": [], "knowledge_state": "emerging",
                    "tags": [], "keywords": [], "claims": [],
                    "current_answer": "Pending compilation from the indexed evidence.",
                    "current_answer_pt": "Compilação pendente a partir da evidência indexada.",
                    "version": "1.0", "created": TODAY, "updated": TODAY,
                    "history": [{"version": "1.0", "date": TODAY,
                                 "change": f"Created via contribution {s['id']} (ORCID {s['orcid']}).",
                                 "change_pt": f"Criada via contribuição {s['id']} (ORCID {s['orcid']})."}],
                    "contributors": [s["orcid"]], "alias_temp": s["temp_id"]})
                s["status"] = "promoted"; s["resolved_id"] = final
                print(f"  ✓ question {final} created (neutral stub; fill via loop/suggestions).")
        elif s["type"] == "suggestion":
            target = s["resolved_id"] if s.get("resolved_id") else s["question"]
            # if the suggestion proposed a NEW question, that question must be promoted first
            if str(target).split("-")[-1].startswith("D"):
                print(f"  ⤷ target {target} is still a TEMP question — promote it first "
                      f"(process its question submission), then re-run.")
                continue
            print(f"  hand {s['ref']} to the neutral compiler for {target} (BYO-compute: "
                  f"{ingest.provider() or 'no-LLM'} {ingest.MODEL})")
            if commit:
                with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
                    tf.write(s["ref"].split(":", 1)[1] + "\n"); tmp = tf.name
                cmd = [sys.executable, os.path.join(HERE, "loop.py"), target,
                       "--doi-file", tmp, "--accept", "4", "--commit"]
                print(f"  $ {' '.join(cmd[1:])}")
                rc = subprocess.run(cmd, cwd=HERE).returncode
                os.unlink(tmp)
                s["status"] = "processed" if rc == 0 else "error"
                s["processed"] = TODAY
                print(f"  {'✓ processed' if rc == 0 else '✗ loop error'} (claims compiled by the neutral loop).")

    if commit:
        save(QF, qdata)   # only question stubs were added here; loop already wrote its own changes + synced
        db.sync(verbose=False)
        save_queue(q)
        print("\n✓ queue + registry updated.")
    else:
        print("\n(dry-run; add --commit to apply)")


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    {"question": cmd_question, "suggest": cmd_suggest, "list": cmd_list,
     "process": cmd_process}.get(cmd, lambda a: print(__doc__))(args[1:] if args else [])


if __name__ == "__main__":
    main()
