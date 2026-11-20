#!/usr/bin/env python3
"""Apply consolidation results (registry/consolidation/<qid>.json, made by consolidate.py) to the registry seeds.
R-CLM-19: the claim becomes a general proposition; each study's result becomes `finding` on its evidence row.

For every proposition of a consolidated question:
- one NEW claim per shared-store key (G-xxxxx). A proposition reused by several questions is ONE claim (claim
  graph, R-OBJ-7); its evidence is the union of the findings placed under it.
- every evidence row is COPIED from the old claim (ref, quote, verification, grade… kept intact) and gets the new
  `stance`, `finding` and, for a review that only re-reports another item, `secondary_of`.
- the question's links are replaced by the new claims (role = proposition role).
- the old claims are NEVER deleted (R-CLM-9): they get `superseded_by` and a history event, and once no question
  links them any more `status: "superseded"`. Items dropped by the consolidation keep their evidence in the old
  claim, with the reason in its history.
- knowledge_state of a new claim = the most frequent state among the old claims behind its supporting findings
  (ties → the lower one): the curated state is carried over, never invented (R-CLM-5).
Only `status: clean` results are applied unless --include-review. Mapping G-key → claim id: consolidation/applied.json.

  python3 apply_consolidation.py [SQ-...] [--all] [--include-review] [--commit]     (without --commit: dry run)"""
import json, os, sys, copy, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CDIR = os.path.join(HERE, "consolidation")
CF, QF = os.path.join(HERE, "claims.json"), os.path.join(HERE, "questions.json")
MAPF = os.path.join(CDIR, "applied.json")
TODAY = datetime.date.today().isoformat()
STATES = ["no_evidence", "speculative", "emerging", "probable", "established", "foundational"]
GRADES = ["very_low", "low", "moderate", "high"]
COMMIT = "--commit" in sys.argv


def norm(r):
    return (r or "").strip().lower()


def main():
    cdata, qdata = json.load(open(CF)), json.load(open(QF))
    C = {c["id"]: c for c in cdata["claims"]}
    Q = {q["id"]: q for q in qdata["questions"]}
    amap = json.load(open(MAPF)) if os.path.exists(MAPF) else {}
    ids = [a for a in sys.argv[1:] if a.startswith("SQ-")]
    if "--all" in sys.argv:
        ids = sorted(f[:-5] for f in os.listdir(CDIR) if f.startswith("SQ-") and f.endswith(".json"))
    seq = max(int(c["id"].split("-")[-1]) for c in cdata["claims"])
    created, applied = [], []
    for qid in ids:
        res = json.load(open(os.path.join(CDIR, f"{qid}.json")))
        q = Q[qid]
        if q.get("consolidation", {}).get("applied"):
            print(f"{qid}: already applied"); continue
        if res["status"] != "clean" and "--include-review" not in sys.argv:
            print(f"{qid}: status {res['status']} — skipped ({len(res['major_problems'])} major problem(s))"); continue
        byE = {i["e"]: i for i in res["items"]}
        old_ids = [l["id"] for l in q["claims"]]
        moved = collections.defaultdict(set)   # old claim → new claims its items went to
        links = []
        for p in res["propositions"]:
            gk = p["store_key"]
            if gk in amap and amap[gk] in C:
                nc = C[amap[gk]]
            else:
                seq += 1
                cid = f"SCR-LIP-{seq:06d}"
                olds = [C[o] for x in p["evidence"] for o in byE[x["e"]]["old_claims"] if o in C]
                ctype = collections.Counter(o["claim_type"] for o in olds).most_common(1)[0][0]
                nc = {"id": cid, "statement": p["statement"], "claim_type": ctype,
                      "context": copy.deepcopy(olds[0].get("context", {})) if olds else {},
                      "knowledge_state": "emerging", "evidence_confidence": p.get("grade") or "very_low",
                      "evidence": [], "relations": [], "gaps": "",
                      "curators": copy.deepcopy(olds[0].get("curators", [])) if olds else [],
                      "created": TODAY, "updated": TODAY, "license": "CC-BY-4.0",
                      "consolidated_from": [], "questions_consolidated": [],
                      "provenance": {"method": "consolidation (R-CLM-19)", "store_key": gk,
                                     "models": res.get("models")},
                      "history": [{"date": TODAY, "event": "created_by_consolidation",
                                   "detail": f"general proposition consolidated from {qid}"}]}
                cdata["claims"].append(nc); C[cid] = nc; amap[gk] = cid; created.append(cid)
            have = {norm(e.get("ref")) for e in nc["evidence"]}
            sup_states = []
            for x in p["evidence"]:
                it = byE[x["e"]]
                for o in it["old_claims"]:
                    moved[o].add(nc["id"])
                    if o not in nc["consolidated_from"]:
                        nc["consolidated_from"].append(o)
                    if x["stance"] == "supporting" and o in C:
                        sup_states.append(C[o]["knowledge_state"])
                if norm(it["ref"]) in have:
                    continue
                src = next((e for o in it["old_claims"] if o in C for e in C[o]["evidence"]
                            if norm(e.get("ref")) == norm(it["ref"])), None)
                if src is None:
                    continue
                ev = copy.deepcopy(src)
                ev["stance_in_source_claim"] = ev.get("stance")
                ev["stance"], ev["finding"] = x["stance"], x["finding"]
                ev["from_claims"] = list(it["old_claims"])
                if x.get("secondary_of"):
                    ev["secondary_of"] = byE[x["secondary_of"]]["ref"]
                nc["evidence"].append(ev); have.add(norm(it["ref"]))
            if sup_states:
                cnt = collections.Counter(sup_states)
                top = max(cnt.values())
                nc["knowledge_state"] = min((s for s in cnt if cnt[s] == top), key=STATES.index)
            # GRADE: when a proposition is reused, keep the higher-certainty one (R-CLM-11 computed per question).
            g = p.get("grade")
            if g and GRADES.index(g) > GRADES.index(nc.get("evidence_confidence") or "very_low"):
                nc["evidence_confidence"] = g
            if qid not in nc["questions_consolidated"]:
                nc["questions_consolidated"].append(qid)
            nc["updated"] = TODAY
            links.append({"id": nc["id"], "role": p["role"]})
        # Old claims: never deleted. Mark where their evidence went; dropped items noted.
        dropped = {d["e"]: d.get("reason", "") for d in res.get("dropped", [])}
        for e, reason in dropped.items():
            for o in byE[e]["old_claims"]:
                if o in C:
                    C[o].setdefault("history", []).append({"date": TODAY, "event": "consolidation_dropped",
                        "detail": f"{byE[e]['ref']} not carried into {qid}'s propositions: {reason}"})
        q["claims"] = links
        q["consolidation"] = {"applied": TODAY, "from_claims": old_ids, "result": f"consolidation/{qid}.json",
                              "status": res["status"]}
        q.setdefault("history", []).insert(0, {"version": q.get("version"), "date": TODAY,
            "change": f"Claims consolidated (R-CLM-19): {len(old_ids)} single-paper claims → {len(links)} general "
                      f"propositions; study results kept as findings.",
            "change_pt": f"Claims consolidados (R-CLM-19): {len(old_ids)} claims de artigo único → {len(links)} "
                         f"proposições gerais; os resultados de cada estudo ficam como achados."})
        for o in old_ids:
            if o in C:
                C[o]["superseded_by"] = sorted(set(C[o].get("superseded_by", [])) | moved.get(o, set()))
                C[o].setdefault("history", []).append({"date": TODAY, "event": "consolidated",
                    "detail": f"{qid}: evidence moved to {', '.join(sorted(moved.get(o, set()))) or '(dropped only)'}"})
        applied.append(qid)
        print(f"{qid}: {len(old_ids)} old claims → {len(links)} claims ({sum(1 for l in links if l['id'] in created)} new)")
    # Old claims no question links any more are superseded (kept, never deleted).
    linked = {l["id"] for q in qdata["questions"] for l in q["claims"]}
    n_sup = 0
    for c in cdata["claims"]:
        if c.get("superseded_by") and c["id"] not in linked and c.get("status") != "superseded":
            c["status"] = "superseded"; n_sup += 1
    cdata["count"] = len(cdata["claims"]); cdata["date"] = TODAY
    print(f"applied {len(applied)} question(s); {len(created)} new claim(s); {n_sup} old claim(s) now superseded")
    if not COMMIT:
        print("(dry run — add --commit to write)"); return
    json.dump(cdata, open(CF, "w"), ensure_ascii=False, indent=2)
    json.dump(qdata, open(QF, "w"), ensure_ascii=False, indent=2)
    json.dump(amap, open(MAPF, "w"), ensure_ascii=False, indent=1)
    import db
    db.sync(verbose=False)
    print("✓ written + DB synced")


if __name__ == "__main__":
    main()
