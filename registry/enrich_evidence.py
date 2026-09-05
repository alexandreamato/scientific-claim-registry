#!/usr/bin/env python3
"""Backfill human-readable citation metadata (title, authors, journal) onto each evidence entry,
so the UI shows 'Title — Authors (Year)' instead of a raw DOI (R-CLM-16). Idempotent: skips
entries that already have a title. DOIs → Crossref, with a Europe PMC fallback for DOIs Crossref
does not index (eurrev, Clin Ter, German Med Sci…); PMIDs → Europe PMC. Syncs scr.db at the end
(R-DATA-1). Run from registry/:
  python3 enrich_evidence.py [--force]   # backfill (──force re-fetches even titled entries)
  python3 enrich_evidence.py --check     # GUARD: report DOI/PMID evidence still missing a title;
                                         #        exit 1 if any (so cron/CI can flag a regression)
"""
import json, os, sys, time, urllib.request, urllib.parse
import ingest  # canonical clean_text() — sanitize metadata on write (R-CLM-14)
import db      # keep scr.db in lockstep (R-DATA-1)
HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.join(HERE, "claims.json")
UA = {"User-Agent": "SCR/0.1 (https://scientificclaims.org; mailto:alexandre@amato.com.br)"}
FORCE = "--force" in sys.argv
CHECK = "--check" in sys.argv

def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.loads(r.read())

def fmt_authors(families):
    a = [x for x in families if x]
    if not a: return ""
    if len(a) == 1: return a[0]
    if len(a) == 2: return f"{a[0]} & {a[1]}"
    return f"{a[0]} et al."

def from_crossref(doi):
    m = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    title = (m.get("title") or [""])[0]
    authors = fmt_authors([a.get("family") for a in m.get("author", [])])
    journal = (m.get("container-title") or [""])[0]
    yr = None
    for k in ("published-print", "published-online", "published", "issued"):
        try:
            yr = m[k]["date-parts"][0][0]; break
        except Exception:
            pass
    return title, authors, journal, yr

def _epmc(query):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": query, "format": "json", "resultType": "core"}))
    res = _get(url).get("resultList", {}).get("result", [])
    if not res:
        return None
    r = res[0]
    auth = r.get("authorString", "")
    fam = [a.split()[0] for a in auth.split(",") if a.strip()][:3]
    return r.get("title", "").rstrip("."), fmt_authors(fam), r.get("journalTitle", ""), r.get("pubYear")

def from_pmid(pmid):
    return _epmc(f"EXT_ID:{pmid} AND SRC:MED")

def from_doi(doi):
    """Crossref first; fall back to Europe PMC for DOIs Crossref doesn't index."""
    try:
        title, authors, journal, yr = from_crossref(doi)
        if (title or "").strip():
            return title, authors, journal, yr
    except Exception:
        pass
    return _epmc(f'DOI:"{doi}"')

def resolvable_without_title(data):
    """The GUARD predicate: evidence whose ref resolves (DOI/PMID) but has no title — the exact
    state that produced bare-DOI hovers. Citation-string refs are excluded (already readable)."""
    out = []
    for c in data["claims"]:
        for ev in c.get("evidence", []):
            if (ev.get("title") or "").strip():
                continue
            if (ev.get("ref") or "").upper().startswith(("DOI:", "PMID:")):
                out.append((c["id"], ev["ref"]))
    return out

def main():
    data = json.load(open(CF))

    if CHECK:
        gaps = resolvable_without_title(data)
        if gaps:
            print(f"✗ GUARD: {len(gaps)} DOI/PMID evidence entr(ies) without a title (R-CLM-16):")
            for cid, ref in gaps[:20]:
                print(f"    {cid}  {ref}")
            print("  → run: python3 enrich_evidence.py")
            sys.exit(1)
        print("✓ GUARD: every DOI/PMID evidence entry has a title (R-CLM-16).")
        return

    done = fail = 0
    for c in data["claims"]:
        for ev in c.get("evidence", []):
            ref = (ev.get("ref") or "")
            if ev.get("title") and not FORCE:
                continue
            try:
                if ref.upper().startswith("DOI:"):
                    got = from_doi(ref[4:])
                elif ref.upper().startswith("PMID:"):
                    got = from_pmid(ref[5:])
                else:
                    continue  # bibliographic string / "Amato ACM, YYYY" — already human-readable
                if not got:
                    fail += 1; continue
                title, authors, journal, yr = got
                title = ingest.clean_text(title)  # R-CLM-14: strip JATS/HTML markup on write
                if title:
                    ev["title"] = title[:300]
                    if authors: ev["authors"] = ingest.clean_text(authors)
                    if journal: ev["journal"] = ingest.clean_text(journal)
                    if yr and not ev.get("year"):
                        try: ev["year"] = int(str(yr)[:4])
                        except Exception: pass
                    done += 1
                    if done % 20 == 0:
                        json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)
                        print(f"  …{done} enriched", flush=True)
                time.sleep(0.2)
            except Exception:
                fail += 1
    json.dump(data, open(CF, "w"), ensure_ascii=False, indent=2)
    db.sync(verbose=False)  # R-DATA-1: rebuild scr.db from the updated seeds
    remaining = len(resolvable_without_title(data))
    print(f"Done. {done} enriched, {fail} failed/skipped; {remaining} DOI/PMID entr(ies) still without title.")

if __name__ == "__main__":
    main()
