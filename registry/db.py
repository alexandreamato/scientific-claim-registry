#!/usr/bin/env python3
"""SCR registry database (SQLite) — the canonical store.

Pipeline:  scr.db  --(export)-->  claims.json  --(site/build_site.py)-->  claims.html

The DB is a deterministic, LOSSLESS rebuild of the JSON seeds: every claim/question object is stored
verbatim in a raw_json column (export reproduces it exactly), with queryable projections alongside.
`sync` is THE standardized way to (re)populate it — every tool that edits the seeds calls db.sync().

Commands:
  python3 db.py sync         # STANDARD: lossless rebuild from seeds + parity check (use this)
  python3 db.py build        # rebuild scr.db from schema.sql + claims.json + questions.json
  python3 db.py export        # write the JSON seeds back FROM the DB (lossless, via raw_json)
  python3 db.py verify        # assert the DB mirrors the seeds exactly (no drift)
  python3 db.py stats         # quick counts
  python3 db.py query "SQL"   # run an arbitrary read query
"""
import sqlite3, json, os, sys, re, datetime
DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(DIR, "scr.db")
CLAIMS_JSON = os.path.join(DIR, "claims.json")
HELD_JSON = os.path.join(DIR, "_held_out_theory.json")
SCHEMA = os.path.join(DIR, "schema.sql")

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c

QJSON = os.path.join(DIR, "questions.json")

def _jd(x): return json.dumps(x, ensure_ascii=False) if x is not None else None

def build(verbose=True):
    """Deterministic, LOSSLESS rebuild of scr.db from the JSON seeds. Every field is preserved:
    the full claim/question object goes into raw_json (the export source of truth), and the queryable
    parts are projected into normalized columns/tables (incl. evidence.grade, phrasings, history)."""
    if os.path.exists(DB): os.remove(DB)
    c = conn(); c.executescript(open(SCHEMA).read())
    cdata = json.load(open(CLAIMS_JSON)); claims = cdata["claims"]
    c.execute("INSERT OR REPLACE INTO meta(file,wrapper_json) VALUES('claims',?)",
              (_jd({k: v for k, v in cdata.items() if k != "claims"}),))
    cur_ids = {}
    def curator(cu):
        key = cu.get("orcid") or cu.get("name")
        if key in cur_ids: return cur_ids[key]
        c.execute("INSERT OR IGNORE INTO curators(name,orcid,role) VALUES(?,?,?)",
                  (cu.get("name"), cu.get("orcid"), cu.get("role")))
        row = c.execute("SELECT id FROM curators WHERE orcid IS ? OR name=?",
                        (cu.get("orcid"), cu.get("name"))).fetchone()
        cur_ids[key] = row["id"]; return row["id"]
    for cl in claims:
        ctx = cl.get("context", {})
        c.execute("""INSERT INTO claims(id,domain,version,claim_type,knowledge_state,evidence_confidence,
                     statement,statement_pt,population,condition,exposure,comparator,outcome,scope,gaps,
                     primary_source,in_registry,license,created,updated,history_json,provenance_json,raw_json)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?,?,?,?,?)""",
                  (cl["id"], cl["id"].split("-")[1] if "-" in cl["id"] else None,
                   cl.get("version", "1.0"), cl["claim_type"], cl["knowledge_state"], cl["evidence_confidence"],
                   cl["statement"], cl.get("statement_pt"),
                   ctx.get("population"), ctx.get("condition"), ctx.get("exposure"), ctx.get("comparator"),
                   ctx.get("outcome"), ctx.get("scope"), cl.get("gaps"),
                   cl.get("primary_amato_source"), cl.get("license", "CC-BY-4.0"),
                   cl.get("created"), cl.get("updated"),
                   _jd(cl.get("history")), _jd(cl.get("provenance")), _jd(cl)))
        for e in cl.get("evidence", []):
            v = e.get("verification") or {}
            c.execute("""INSERT INTO evidence(claim_id,ref,stance,study_design,n,risk_of_bias,year,amato_authored,
                         note,grade,grade_source,quote,extraction_confidence,verified,verify_verdict,verify_json,
                         title,authors,journal)
                         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (cl["id"], e.get("ref"), e.get("stance"), e.get("study_design"), e.get("n"),
                       e.get("risk_of_bias"), e.get("year"), 1 if e.get("amato_authored") else 0, e.get("note"),
                       e.get("grade"), (e.get("_prov") or {}).get("grade_source"),
                       e.get("quote"), e.get("extraction_confidence"),
                       1 if v.get("verdict") == "verified" else 0, v.get("verdict"),
                       (_jd(v) if v else None),
                       e.get("title"), e.get("authors"), e.get("journal")))
        for r in cl.get("relations", []):
            c.execute("INSERT INTO relations(claim_id,rel_type,target_id,target_hint,strength) VALUES(?,?,?,?,?)",
                      (cl["id"], r.get("type"), r.get("target"), r.get("target_hint"), r.get("strength")))
        for cu in cl.get("curators", []):
            c.execute("INSERT OR IGNORE INTO claim_curators(claim_id,curator_id) VALUES(?,?)", (cl["id"], curator(cu)))
    if os.path.exists(HELD_JSON):
        for it in json.load(open(HELD_JSON)).get("items", []):
            c.execute("INSERT INTO held_out_theory(topic,reason,ref) VALUES(?,?,?)",
                      (it.get("topic"), it.get("reason"), it.get("ref")))
    nq = 0
    if os.path.exists(QJSON):
        qdata = json.load(open(QJSON))
        c.execute("INSERT OR REPLACE INTO meta(file,wrapper_json) VALUES('questions',?)",
                  (_jd({k: v for k, v in qdata.items() if k != "questions"}),))
        for q in qdata.get("questions", []):
            nq += 1
            links = q.get("claims", [])
            sup = sum(1 for l in links if l.get("role") == "supporting")
            con = sum(1 for l in links if l.get("role") == "contradicting")
            oth = len(links) - sup - con
            dom = q["id"].split("-")[1] if "-" in q["id"] else None
            c.execute("""INSERT INTO questions(id,domain,text,text_pt,knowledge_state,current_answer,current_answer_pt,
                         major_uncertainty,major_uncertainty_pt,version,created,updated,tags_json,keywords_json,
                         first_mention_json,history_json,raw_json)
                         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (q["id"], dom, q["text"], q.get("text_pt"), q.get("knowledge_state"),
                       q.get("current_answer"), q.get("current_answer_pt"),
                       q.get("major_uncertainty"), q.get("major_uncertainty_pt"),
                       q.get("version", "1.0"), q.get("created"), q.get("updated"),
                       _jd(q.get("tags")), _jd(q.get("keywords")), _jd(q.get("first_mention")),
                       _jd(q.get("history")), _jd(q)))
            for lang, key in (("en", "phrasings"), ("pt", "phrasings_pt")):
                for i, ph in enumerate(q.get(key) or []):
                    c.execute("INSERT OR IGNORE INTO question_phrasings(question_id,lang,seq,text) VALUES(?,?,?,?)",
                              (q["id"], lang, i, ph))
            for h in (q.get("history") or [{"version": q.get("version", "1.0"), "date": q.get("updated"),
                                            "change": "Initial version."}]):
                c.execute("""INSERT INTO question_versions(question_id,version,date,knowledge_state,current_answer,
                             whats_changed,supporting_count,contradicting_count,other_count,major_uncertainty,reviewed_by_human)
                             VALUES(?,?,?,?,?,?,?,?,?,?,0)""",
                          (q["id"], h.get("version"), h.get("date"), q.get("knowledge_state"), q.get("current_answer"),
                           h.get("change"), sup, con, oth, q.get("major_uncertainty")))
            for l in links:
                c.execute("INSERT OR IGNORE INTO claim_questions(question_id,claim_id,role) VALUES(?,?,?)",
                          (q["id"], l["id"], l.get("role")))
    # seed id counters from current max seq per scope (canonical), drafts start at 1
    def _maxseq(table, prefix, domain):
        m = 0
        for (rid,) in c.execute(f"SELECT id FROM {table} WHERE id LIKE ?", (f"{prefix}-{domain}-%",)):
            mm = re.search(r"-(\d+)$", rid)
            if mm:
                m = max(m, int(mm.group(1)))
        return m
    for pref, table in (("SCR", "claims"), ("SQ", "questions")):
        c.execute("INSERT OR REPLACE INTO id_counters(scope,next_seq) VALUES(?,?)",
                  (f"{pref}-LIP", _maxseq(table, pref, "LIP") + 1))
        c.execute("INSERT OR IGNORE INTO id_counters(scope,next_seq) VALUES(?,1)", (f"{pref}-LIP-D",))
    c.commit()
    n = c.execute("SELECT COUNT(*) FROM claims WHERE in_registry=1").fetchone()[0]
    ne = c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
    if verbose:
        print(f"Built {DB}: {n} claims, {ne} evidence rows, {nq} questions.")
    c.close()
    return n, nq

def _export_list(c, table):
    """Reconstruct a seed file's record list from the LOSSLESS raw_json column."""
    return [json.loads(r["raw_json"]) for r in c.execute(f"SELECT raw_json FROM {table} ORDER BY id")]

def _wrapper(c, file):
    row = c.execute("SELECT wrapper_json FROM meta WHERE file=?", (file,)).fetchone()
    return json.loads(row["wrapper_json"]) if row and row["wrapper_json"] else {}

def export(verbose=True):
    """Write the JSON seeds back FROM the DB (raw_json), reproducing each wrapper verbatim. Lossless."""
    c = conn()
    for file, table, listkey, path in (("claims", "claims", "claims", CLAIMS_JSON),
                                       ("questions", "questions", "questions", QJSON)):
        recs = _export_list(c, table)
        out = dict(_wrapper(c, file))
        if "count" in out: out["count"] = len(recs)  # update only if the seed had it (stay faithful)
        out[listkey] = recs
        json.dump(out, open(path, "w"), ensure_ascii=False, indent=2)
        if verbose:
            print(f"Exported {len(recs)} {listkey} -> {path}")
    c.close()

def verify_parity(verbose=True):
    """Guarantee the DB == the JSON seeds (no silent drift, ever). Compares the seed record sets to
    what the DB would export. Returns (ok, detail)."""
    c = conn()
    problems = []
    for file, table, listkey, path in (("claims", "claims", "claims", CLAIMS_JSON),
                                       ("questions", "questions", "questions", QJSON)):
        seed = json.load(open(path)).get(listkey, [])
        db_recs = {r["id"]: json.loads(r["raw_json"]) for r in c.execute(f"SELECT id,raw_json FROM {table}")}
        seed_by = {r["id"]: r for r in seed}
        if set(db_recs) != set(seed_by):
            miss = set(seed_by) - set(db_recs); extra = set(db_recs) - set(seed_by)
            problems.append(f"{listkey}: missing in DB {sorted(miss)[:5]}; extra in DB {sorted(extra)[:5]}")
        diffs = [rid for rid in seed_by if rid in db_recs and db_recs[rid] != seed_by[rid]]
        if diffs:
            problems.append(f"{listkey}: {len(diffs)} record(s) differ, e.g. {diffs[:5]}")
    nc = c.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    nq = c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    ok = not problems
    c.execute("INSERT OR REPLACE INTO sync_state(id,last_sync,parity_ok,claims_n,questions_n,detail) "
              "VALUES(1,?,?,?,?,?)", (_now(), 1 if ok else 0, nc, nq, "; ".join(problems) or "ok"))
    c.commit(); c.close()
    if verbose:
        print("✓ parity OK — DB mirrors the JSON seeds exactly." if ok
              else "✗ PARITY MISMATCH:\n  " + "\n  ".join(problems))
    return ok, problems

def sync(verbose=True):
    """THE standardized, always-the-same way to populate the DB: deterministic lossless rebuild +
    parity check. Every tool that mutates the seeds calls this on commit (import db; db.sync(...))."""
    build(verbose=verbose)
    ok, problems = verify_parity(verbose=verbose)
    if not ok:
        raise SystemExit("DB sync parity FAILED: " + "; ".join(problems))
    return ok

def stats():
    c = conn()
    print("registry claims:", c.execute("SELECT COUNT(*) FROM claims WHERE in_registry=1").fetchone()[0])
    print("by knowledge_state:", dict(c.execute("SELECT knowledge_state,COUNT(*) FROM claims WHERE in_registry=1 GROUP BY knowledge_state")))
    print("by claim_type:", dict(c.execute("SELECT claim_type,COUNT(*) FROM claims WHERE in_registry=1 GROUP BY claim_type")))
    print("evidence rows:", c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
          "| Amato-authored:", c.execute("SELECT COUNT(*) FROM evidence WHERE amato_authored=1").fetchone()[0])
    print("claims with >=1 Amato evidence:", c.execute(
        "SELECT COUNT(DISTINCT claim_id) FROM evidence WHERE amato_authored=1").fetchone()[0])
    print("held-out theory items:", c.execute("SELECT COUNT(*) FROM held_out_theory").fetchone()[0])
    print("consensus votes:", c.execute("SELECT COUNT(*) FROM consensus_votes").fetchone()[0])
    c.close()

def query(sql):
    c = conn()
    rows = c.execute(sql).fetchall()
    for r in rows: print(" | ".join(str(r[k]) for k in r.keys()))
    print(f"({len(rows)} rows)")
    c.close()

# ---------- ID allocation (R-ALLOC): temp(draft) -> validated -> final ----------
def _now(): return datetime.date.today().isoformat()

def _next_seq(c, scope):
    row = c.execute("SELECT next_seq FROM id_counters WHERE scope=?", (scope,)).fetchone()
    if row is None:
        c.execute("INSERT INTO id_counters(scope,next_seq) VALUES(?,2)", (scope,)); return 1
    seq = row["next_seq"]; c.execute("UPDATE id_counters SET next_seq=? WHERE scope=?", (seq + 1, scope)); return seq

def request_id(prefix, domain, kind="claim", note="", source=""):
    """Emit a TEMP/draft code (does not consume a canonical number)."""
    c = conn(); seq = _next_seq(c, f"{prefix}-{domain}-D"); temp = f"{prefix}-{domain}-D{seq:06d}"
    c.execute("INSERT INTO id_requests(temp_id,prefix,domain,kind,status,note,source,created) VALUES(?,?,?,?,'draft',?,?,?)",
              (temp, prefix, domain, kind, note, source, _now()))
    c.commit(); c.close(); return temp

def promote_id(temp):
    """Validate -> allocate the next CANONICAL number + create alias (temp 301-> final)."""
    c = conn(); r = c.execute("SELECT * FROM id_requests WHERE temp_id=?", (temp,)).fetchone()
    if not r: c.close(); raise SystemExit(f"no such temp_id {temp}")
    seq = _next_seq(c, f"{r['prefix']}-{r['domain']}"); canon = f"{r['prefix']}-{r['domain']}-{seq:06d}"
    c.execute("UPDATE id_requests SET status='published',canonical_id=?,decided=? WHERE temp_id=?", (canon, _now(), temp))
    c.execute("INSERT OR REPLACE INTO id_aliases(from_code,to_code,kind,created) VALUES(?,?,'promote',?)", (temp, canon, _now()))
    c.commit(); c.close(); return canon

def merge_id(temp, canonical):
    c = conn()
    c.execute("UPDATE id_requests SET status='merged',canonical_id=?,decided=? WHERE temp_id=?", (canonical, _now(), temp))
    c.execute("INSERT OR REPLACE INTO id_aliases(from_code,to_code,kind,created) VALUES(?,?,'merge',?)", (temp, canonical, _now()))
    c.commit(); c.close(); return canonical

def reject_id(temp):
    c = conn(); c.execute("UPDATE id_requests SET status='rejected',decided=? WHERE temp_id=?", (_now(), temp)); c.commit(); c.close()

def resolve_id(code):
    c = conn(); seen = set()
    while True:
        a = c.execute("SELECT to_code FROM id_aliases WHERE from_code=?", (code,)).fetchone()
        if not a or code in seen: break
        seen.add(code); code = a["to_code"]
    c.close(); return code

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "build": build()
    elif cmd == "sync": sync()
    elif cmd == "verify": verify_parity()
    elif cmd == "export": export()
    elif cmd == "stats": stats()
    elif cmd == "query": query(sys.argv[2])
    elif cmd == "request": print(request_id(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "claim",
                                             sys.argv[5] if len(sys.argv) > 5 else ""))
    elif cmd == "promote": print(promote_id(sys.argv[2]))
    elif cmd == "merge": print(merge_id(sys.argv[2], sys.argv[3]))
    elif cmd == "reject": reject_id(sys.argv[2]); print("rejected", sys.argv[2])
    elif cmd == "resolve": print(resolve_id(sys.argv[2]))
    else: print(__doc__)
