#!/usr/bin/env python3
"""For each question, find the FIRST time its topic appears in the literature and store it as
`first_mention` {year, ref, title, via}. The timeline anchors its left edge there (a hollow ring),
so the evidence timeline spans from the topic's origin to now.

How the anchor is chosen (fixed 2026-11-18, see RULES changelog):
- Europe PMC, matching the topic in TITLE/ABSTRACT only. A full-text match let a 1934 obesity paper
  that mentions the word in passing become the "first mention" of 13 questions.
- Preprints (SRC:PPR) and undated records are excluded, and the oldest is computed HERE over every
  hit. Europe PMC's `sort=... asc` puts undated records and fresh preprints first, which is how
  2025-2026 preprints became the "origin" of several questions.
- The registry's own evidence for the question also competes: the anchor can never be younger than
  the oldest evidence already shown on the timeline.
- Excluded DOIs (exclude.json) and banned authors (R-CLM-10) are skipped. A hand-curated anchor
  (`via: "curated"`) is never overwritten.

Run from registry/:  python3 first_mention.py [--force] [--dry-run]"""
import json, os, re, sys, time, urllib.request, urllib.parse, datetime
import ingest
HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
CF = os.path.join(HERE, "claims.json")
THIS_YEAR = datetime.date.today().year
FORCE = "--force" in sys.argv
DRY = "--dry-run" in sys.argv
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
SYNONYMS = {"lipedema": "(lipedema OR lipoedema)"}
PREPRINT_DOI = re.compile(r"^10\.(20944|21203|1101|31219|2196/preprints)/", re.I)


def topic_query(q):
    """Same topic words the loop uses, but restricted to title/abstract and with spelling variants."""
    base = ingest.build_query(q)
    for k, v in SYNONYMS.items():
        base = re.sub(rf"\b{k}\b", v, base)
    return (f"TITLE_ABS:({base}) AND PUB_YEAR:[1930 TO {THIS_YEAR}] NOT SRC:PPR "
            f"NOT PUB_TYPE:preprint")


def fetch_all(query, cap=5000):
    """Every hit (lite records), paged with cursorMark; retries transient 5xx."""
    out, cursor = [], "*"
    while len(out) < cap:
        url = API + urllib.parse.urlencode({"query": query, "format": "json", "pageSize": 1000,
                                            "resultType": "lite", "cursorMark": cursor})
        req = urllib.request.Request(url, headers={"User-Agent": "SCR/0.1 (scientificclaims.org)"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read())
                break
            except Exception as e:
                if attempt == 4:
                    print(f"   [error {e}]")
                    return None
                time.sleep(3 * (attempt + 1))
        res = data.get("resultList", {}).get("result", [])
        out += res
        nxt = data.get("nextCursorMark")
        if not res or not nxt or nxt == cursor:
            break
        cursor = nxt
    return out


def oldest_epmc(q, excl):
    hits = fetch_all(topic_query(q))
    if hits is None:
        return None
    best = None
    for x in hits:
        doi = (x.get("doi") or "").lower()
        if doi in excl or (x.get("pmid") and x["pmid"] in excl) or PREPRINT_DOI.match(doi):
            continue
        if ingest.banned_author(x):
            continue
        try:
            yr = int(x.get("pubYear") or 0)
        except ValueError:
            continue
        if not (1930 <= yr <= THIS_YEAR) or not (doi or x.get("pmid")):
            continue
        key = (yr, x.get("firstPublicationDate") or "9999")
        if best is None or key < best[0]:
            best = (key, x)
    if not best:
        return None
    x = best[1]
    ref = f"DOI:{x['doi'].lower()}" if x.get("doi") else f"PMID:{x['pmid']}"
    return {"year": best[0][0], "ref": ref, "title": (x.get("title") or "").rstrip(".").strip(),
            "via": "europepmc", "hits": len(hits)}


def oldest_registry(q, claims, excl):
    """Oldest non-preprint evidence already linked to this question."""
    best = None
    for cid in q.get("claims") or []:
        cid = cid if isinstance(cid, str) else (cid.get("id") or cid.get("claim"))
        for ev in (claims.get(cid) or {}).get("evidence", []):
            ref = (ev.get("ref") or "").strip()
            r = ref.split(":", 1)[-1].lower()
            if not ev.get("year") or r in excl or PREPRINT_DOI.match(r):
                continue
            if ingest.banned_author(ev):
                continue
            if best is None or ev["year"] < best["year"]:
                # Pre-DOI classics (e.g. Allen & Hines 1940) carry a free-text citation as `ref`.
                is_id = ref.upper().startswith(("DOI:", "PMID:"))
                best = {"year": int(ev["year"]), "ref": ref if is_id else None,
                        "title": (ev.get("title") or ("" if is_id else ref)).rstrip("."),
                        "via": "registry_evidence"}
    return best


def main():
    data = json.load(open(QF))
    claims = {c["id"]: c for c in json.load(open(CF))["claims"]}
    excl = ingest.excluded_set()
    n = 0
    for q in data["questions"]:
        cur = q.get("first_mention") or {}
        if cur.get("via") == "curated":
            print(f"  {q['id']}  keep curated {cur.get('year')}")
            continue
        if cur and not FORCE:
            continue
        cands = [c for c in (oldest_epmc(q, excl), oldest_registry(q, claims, excl)) if c]
        if not cands:
            print(f"  {q['id']}  (no first mention found: {topic_query(q)})")
            q.pop("first_mention", None)
            continue
        fm = min(cands, key=lambda c: c["year"])
        fm.pop("hits", None)
        old = f"{cur.get('year')} {cur.get('ref')}" if cur else "—"
        print(f"  {q['id']}  {old}  →  {fm['year']} {fm['ref']} [{fm['via']}]  {fm['title'][:55]}")
        q["first_mention"] = fm
        n += 1
        time.sleep(0.3)
    if DRY:
        print(f"Dry run. {n} question(s) would change; nothing written.")
        return
    json.dump(data, open(QF, "w"), ensure_ascii=False, indent=2)
    print(f"Done. {n} question(s) got a first_mention.")


if __name__ == "__main__":
    main()
