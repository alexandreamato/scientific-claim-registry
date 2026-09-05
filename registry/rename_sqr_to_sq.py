#!/usr/bin/env python3
"""One-off migration: question prefix SQR- -> SQ- (claims stay SCR-). Safe because the token
'SQR' only ever denotes the question registry prefix in this project. Run from project root:
  python3 registry/rename_sqr_to_sq.py
Generated site/q/*.html are NOT touched here (they are rebuilt); redirects + db handled separately.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = [
  "registry/questions.json", "registry/claims.json", "registry/db.py", "registry/ingest.py",
  "registry/schema.sql", "registry/add_history.py", "registry/add_tags.py", "registry/seed_pt_questions.py",
  "registry/README.md", "site/build_questions.py", "site/index.html", "site/pt/index.html",
  "README.md", "CLAUDE.md", "docs/spec/RULES.md", "docs/spec/id-allocation.md", "docs/spec/surveillance.md",
  "docs/glossary.md", "docs/one-pager.md", "docs/11_quem-precisa-evidence-decay.md",
]
total = 0
for rel in SRC:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print(f"  (skip, missing) {rel}"); continue
    s = open(p, encoding="utf-8").read()
    n = s.count("SQR")
    if n:
        open(p, "w", encoding="utf-8").write(s.replace("SQR", "SQ"))
        total += n
        print(f"  {rel}: {n} replaced")
print(f"Done. {total} occurrences SQR->SQ across {len(SRC)} files.")
