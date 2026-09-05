#!/usr/bin/env python3
"""For each question, find the FIRST time its topic appears in the literature (oldest Europe PMC
match) and store it as `first_mention` {year, ref, title}. The timeline then anchors its left edge
there (a hollow ring), so the evidence timeline spans from the topic's origin to now.
Idempotent (skips questions that already have first_mention). Run from registry/:
  python3 first_mention.py [--force]"""
import json, os, sys, urllib.request, urllib.parse, datetime
import ingest
HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
THIS_YEAR = datetime.date.today().year
FORCE = "--force" in sys.argv

def oldest(query):
    q = f'({query})'
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": q, "format": "json", "pageSize": 15,
                                     "resultType": "core", "sort": "P_PDATE_D asc"}))
    req = urllib.request.Request(url, headers={"User-Agent": "SCR/0.1 (scientificclaims.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read()).get("resultList", {}).get("result", [])
    except Exception as e:
        print(f"   [error {e}]"); return None
    for x in res:
        yr = int(x.get("pubYear") or 0)
        if 1930 <= yr <= THIS_YEAR and (x.get("doi") or x.get("pmid") or x.get("title")):
            ref = (f"DOI:{x['doi'].lower()}" if x.get("doi") else
                   (f"PMID:{x['pmid']}" if x.get("pmid") else None))
            return {"year": yr, "ref": ref, "title": (x.get("title") or "").rstrip("."), "via": "europepmc"}
    return None

def main():
    data = json.load(open(QF)); n = 0
    for q in data["questions"]:
        if q.get("first_mention") and not FORCE:
            continue
        query = ingest.build_query(q)
        fm = oldest(query)
        if fm:
            q["first_mention"] = fm; n += 1
            print(f"  {q['id']}  first mention {fm['year']}  ·  {fm['title'][:60]}")
        else:
            print(f"  {q['id']}  (no first mention found for: {query})")
    json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
    print(f"Done. {n} question(s) got a first_mention.")

if __name__ == "__main__":
    main()
