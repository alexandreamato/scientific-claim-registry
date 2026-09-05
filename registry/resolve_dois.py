#!/usr/bin/env python3
"""Canonical Crossref title->DOI resolver for Consensus reading-list ingestion (R-AI-10).

The Consensus MCP returns titles/authors/years, not DOIs. Subagents that build reading lists
call this to turn (title, author, year) tuples into a VERIFIED DOI file the loop ingests via
`loop.py <SQ> --doi-file <file>`. Centralizing it here keeps every reading-list run identical.

  python3 resolve_dois.py papers.json out.dois
papers.json = JSON array of [title, author_surname, year] (year optional) OR
              [{"title":..., "author":..., "year":...}, ...]
Writes one DOI per line (deduped, order-preserving) to out.dois; prints the count.
"""
import sys, json, urllib.request, urllib.parse, time

UA = {"User-Agent": "SCR/0.3 (mailto:alexandre@amato.com.br)"}


def resolve(title, author="", year=""):
    q = urllib.parse.urlencode({"query.bibliographic": f"{title} {author} {year}".strip(), "rows": 1})
    req = urllib.request.Request("https://api.crossref.org/works?" + q, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            items = json.load(r)["message"]["items"]
        return items[0].get("DOI") if items else None
    except Exception:
        return None


def resolve_all(papers):
    dois = []
    for p in papers:
        if isinstance(p, dict):
            t, a, y = p.get("title", ""), p.get("author", ""), p.get("year", "")
        else:
            t, a, y = (list(p) + ["", ""])[:3]
        d = resolve(t, a, y); time.sleep(0.6)
        if d and d not in dois:
            dois.append(d)
    return dois


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: resolve_dois.py papers.json [out.dois]")
    papers = json.load(open(sys.argv[1]))
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/dev/stdout"
    dois = resolve_all(papers)
    open(out_path, "w").write("\n".join(dois) + "\n")
    print(f"{len(dois)} DOIs -> {out_path}")


if __name__ == "__main__":
    main()
