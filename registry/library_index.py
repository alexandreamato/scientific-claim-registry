#!/usr/bin/env python3
"""Index the local lipedema library into library.db (SQLite + FTS5) so the surveillance
loop can SEARCH it. The library is the largest monitored corpus for lipedema.

Incremental: skips files whose mtime is unchanged, so re-running picks up only new/edited PDFs
(= "monitoring"). Uses pdftotext (first 2 pages) to get title / DOI / year / abstract.

Usage:
  python3 library_index.py                 # index the whole library (incremental)
  python3 library_index.py --folder Pessoal --limit 80   # subset (fast test)
  python3 library_index.py --reset         # rebuild from scratch
Then `from library_index import search` to query it.
"""
import os, re, sqlite3, subprocess, sys, datetime
DIR = os.path.dirname(os.path.abspath(__file__))
LIBDIR = "/Users/alexandreamato/Library/CloudStorage/SynologyDrive-aamato/artigos lipedema"
DB = os.path.join(DIR, "library.db")
SKIP = {".venv", "__pycache__", "tools", "graph", "scripts", "scripts_temporarios",
        ".claude", ".git", "node_modules", ".bib", "figuras", "figures"}
DOI_RE = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
YEAR_RE = re.compile(r'\b(19[89]\d|20[0-3]\d)\b')

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.executescript("""
      CREATE TABLE IF NOT EXISTS library(
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT UNIQUE, folder TEXT, filename TEXT,
        mtime REAL, title TEXT, doi TEXT, pmid TEXT, year INTEGER, abstract TEXT, indexed_at TEXT);
      CREATE VIRTUAL TABLE IF NOT EXISTS library_fts USING fts5(path UNINDEXED, title, filename, abstract);
    """)
    return c

def pdftext(path, pages=2):
    try:
        out = subprocess.run(["pdftotext", "-f", "1", "-l", str(pages), "-q", path, "-"],
                             capture_output=True, timeout=25)
        return out.stdout.decode("utf-8", "replace")
    except Exception:
        return ""

def parse(path, text):
    fn = os.path.basename(path)
    dm = DOI_RE.search(text); doi = dm.group(0).rstrip('.').lower() if dm else None
    ym = re.search(r'(19[89]\d|20[0-3]\d)', fn) or YEAR_RE.search(text)
    year = int(ym.group(0)) if ym else None
    title = None
    for line in (l.strip() for l in text.splitlines()):
        if len(line) > 25 and not line.lower().startswith(("doi", "http", "www", "abstract", "received", "©")):
            title = line[:300]; break
    if not title:
        title = os.path.splitext(fn)[0].replace('_', ' ')
    m = re.search(r'\babstract\b', text, re.I)
    abstract = (text[m.end():m.end()+1600] if m else text[:1200]).strip()
    abstract = re.sub(r'\s+', ' ', abstract)
    return title, doi, None, year, abstract

def walk(base):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
        for f in files:
            if f.lower().endswith('.pdf'):
                yield os.path.join(root, f)

def main():
    args = sys.argv[1:]
    if "--reset" in args and os.path.exists(DB):
        os.remove(DB)
    folder = args[args.index("--folder")+1] if "--folder" in args else None
    limit = int(args[args.index("--limit")+1]) if "--limit" in args else None
    base = os.path.join(LIBDIR, folder) if folder else LIBDIR
    c = db(); cur = c.cursor()
    have = {r["path"]: r["mtime"] for r in c.execute("SELECT path,mtime FROM library")}
    n = skip = 0
    for path in walk(base):
        try: mt = os.path.getmtime(path)
        except OSError: continue
        if path in have and abs(have[path] - mt) < 1:
            skip += 1; continue
        title, doi, pmid, year, abstract = parse(path, pdftext(path))
        fold = os.path.relpath(path, LIBDIR).split(os.sep)[0]
        cur.execute("DELETE FROM library WHERE path=?", (path,))
        cur.execute("""INSERT INTO library(path,folder,filename,mtime,title,doi,pmid,year,abstract,indexed_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (path, fold, os.path.basename(path), mt, title, doi, pmid, year, abstract,
                     datetime.date.today().isoformat()))
        cur.execute("DELETE FROM library_fts WHERE path=?", (path,))
        cur.execute("INSERT INTO library_fts(path,title,filename,abstract) VALUES(?,?,?,?)",
                    (path, title, os.path.basename(path), abstract))
        n += 1
        if n % 250 == 0:
            c.commit(); print(f"  indexed {n} new (skipped {skip})...", flush=True)
        if limit and n >= limit:
            break
    c.commit()
    total = c.execute("SELECT COUNT(*) FROM library").fetchone()[0]
    print(f"Done. {n} new/changed, {skip} unchanged. Library total: {total}.")
    c.close()

def search(query, limit=20):
    """FTS search over the library; returns candidate dicts in the ingest shape. `query` may be a
    valid FTS5 boolean expression (e.g. 'lipedema AND (joint OR hypermobility)'); if it fails to
    parse, fall back to an OR-of-keywords (FTS operator words stripped)."""
    c = db()
    def _q(expr):
        return c.execute("""SELECT l.* FROM library_fts f JOIN library l ON l.path=f.path
                            WHERE library_fts MATCH ? ORDER BY l.year DESC LIMIT ?""", (expr, limit)).fetchall()
    try:
        rows = _q(query)
    except sqlite3.OperationalError:
        terms = [t for t in re.findall(r'[A-Za-z]{3,}', query.lower()) if t not in ("and", "or", "not", "near")]
        try:
            rows = _q(" OR ".join(dict.fromkeys(terms))) if terms else []
        except sqlite3.OperationalError:
            rows = []
    c.close()
    return [{"source": "library", "id": r["path"], "doi": r["doi"], "pmid": r["pmid"],
             "title": r["title"], "pubYear": r["year"], "abstractText": r["abstract"],
             "path": r["path"], "folder": r["folder"]} for r in rows]

if __name__ == "__main__":
    main()
