#!/usr/bin/env python3
"""Human curation (Layer 2) — the ARTICLE BAN SYSTEM. Ban a reference (retracted, very low quality,
off-topic, predatory…) so it is removed from the registry AND never re-ingested by the loop.
Also auto-detects RETRACTED articles across the whole registry via Crossref.

Run from registry/:
  python3 curate.py ban 10.3390/biomedicines14010122 "off-topic scoping review" off_topic
  python3 curate.py check-retractions            # scan every evidence DOI; report retractions
  python3 curate.py check-retractions --ban      # …and auto-ban the retracted ones
  python3 curate.py list
  python3 curate.py unban 10.xxxx/yyyy

Categories: retracted | low_quality | off_topic | predatory | superseded | duplicate.
After banning, rebuild + deploy. The loop reads exclude.json and skips banned refs (ingest.excluded_set).
"""
import json, os, sys, datetime, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
CF, QF = os.path.join(HERE, "claims.json"), os.path.join(HERE, "questions.json")
XF = os.path.join(HERE, "exclude.json")
UA = {"User-Agent": "SCR/0.1 (https://scientificclaims.org; mailto:alexandre@amato.com.br)"}
CATEGORIES = ("retracted", "low_quality", "off_topic", "predatory", "superseded", "duplicate")

def norm(ref): return (ref or "").replace("DOI:", "").replace("doi:", "").strip().lower()

def load_x():
    if os.path.exists(XF):
        return json.load(open(XF))
    return {"note": "Banned references (retracted / low-quality / off-topic / predatory). The surveillance "
                    "loop skips these (ingest.excluded_set); curate.py manages this file. Layer-2 human curation.",
            "excluded": []}

def save_x(x): json.dump(x, open(XF, "w"), ensure_ascii=False, indent=2)

def all_evidence_dois():
    dois = {}
    for c in json.load(open(CF))["claims"]:
        for ev in c.get("evidence", []):
            r = norm(ev.get("ref", ""))
            if r.startswith("10."):
                dois.setdefault(r, []).append(c["id"])
    return dois

def is_retracted(doi):
    """Return the retraction-notice DOI if `doi` has been retracted (Crossref), else None."""
    try:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            m = json.loads(r.read())["message"]
        for u in m.get("updated-by", []):
            if u.get("type") == "retraction":
                return u.get("DOI")
    except Exception:
        pass
    return None

def ban(ref, reason, category="low_quality"):
    refn = norm(ref); x = load_x()
    if category not in CATEGORIES:
        category = "low_quality"
    if refn not in {norm(e["ref"]) for e in x["excluded"]}:
        x["excluded"].append({"ref": refn, "category": category, "reason": reason or "",
                              "date": datetime.date.today().isoformat()})
        save_x(x)
    cd, qd = json.load(open(CF)), json.load(open(QF))
    removed = []
    for c in list(cd["claims"]):
        kept = [ev for ev in c["evidence"] if norm(ev.get("ref", "")) != refn]
        if len(kept) != len(c["evidence"]):
            c["evidence"] = kept
            if not kept:
                cd["claims"].remove(c); removed.append(c["id"])
    for q in qd["questions"]:
        q["claims"] = [l for l in q.get("claims", []) if l["id"] not in removed]
    cd["count"] = len(cd["claims"])
    json.dump(cd, open(CF, "w"), ensure_ascii=False, indent=2)
    json.dump(qd, open(QF, "w"), ensure_ascii=False, indent=2)
    import db; db.sync(verbose=False)  # keep scr.db in lockstep (R-DATA-1)
    print(f"  ✗ banned {refn} [{category}]. Removed orphaned claim(s): {removed or 'none'}. DB synced.")
    return removed

def check_retractions(do_ban=False):
    dois = all_evidence_dois()
    print(f"Scanning {len(dois)} evidence DOIs against Crossref for retractions…")
    found = []
    for d in dois:
        rdoi = is_retracted(d)
        if rdoi:
            found.append((d, rdoi, dois[d]))
            print(f"  ⚠ RETRACTED: {d}  (notice {rdoi})  used in {dois[d]}")
    if not found:
        print("No retracted articles found. ✓"); return
    if do_ban:
        for d, rdoi, _ in found:
            ban(d, f"retracted (notice {rdoi})", "retracted")
        print(f"Banned {len(found)} retracted article(s). Rebuild + deploy.")
    else:
        print(f"\n{len(found)} retracted. Re-run with --ban to remove them.")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] in ("ban", "exclude") and len(a) >= 2:
        ban(a[1], a[2] if len(a) > 2 else "", a[3] if len(a) > 3 else "low_quality")
    elif a and a[0] == "check-retractions":
        check_retractions("--ban" in a)
    elif a and a[0] in ("unban", "unexclude") and len(a) >= 2:
        x = load_x(); x["excluded"] = [e for e in x["excluded"] if norm(e["ref"]) != norm(a[1])]
        save_x(x); print(f"Unbanned {norm(a[1])}.")
    elif a and a[0] == "list":
        for e in load_x()["excluded"]:
            print(f"  [{e.get('category','?')}] {e['ref']}  ({e.get('date','')}) — {e.get('reason','')}")
    else:
        print(__doc__)
