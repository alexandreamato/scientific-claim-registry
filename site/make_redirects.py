#!/usr/bin/env python3
"""Emit redirect stubs at the OLD question paths (SQR-LIP-*) pointing to the NEW ids (SQ-LIP-*),
for the prefix rename. Covers main page + frozen snapshot, EN + PT. Stubs are noindex and use
canonical + meta-refresh + JS so old links/citations keep resolving. Run from site/."""
import os
SITE = os.path.dirname(os.path.abspath(__file__))
IDS = [f"{i:06d}" for i in range(1, 20)]  # 000001..000019
VER = "1.0"

def stub(new_path):
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">\n'
            f'<title>Moved</title>\n'
            f'<link rel="canonical" href="https://scientificclaims.org{new_path}">\n'
            f'<meta name="robots" content="noindex,follow">\n'
            f'<meta http-equiv="refresh" content="0; url={new_path}">\n'
            f'<script>location.replace("{new_path}"+location.search+location.hash);</script>\n'
            f'</head><body>Moved to <a href="{new_path}">{new_path}</a></body></html>\n')

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(content)

n = 0
for num in IDS:
    old = f"SQR-LIP-{num}"; new = f"SQ-LIP-{num}"
    # EN main + snapshot
    write(os.path.join(SITE, "q", f"{old}.html"), stub(f"/q/{new}.html")); n += 1
    write(os.path.join(SITE, "q", old, f"v{VER}.html"), stub(f"/q/{new}/v{VER}.html")); n += 1
    # PT main + snapshot
    write(os.path.join(SITE, "pt", "q", f"{old}.html"), stub(f"/pt/q/{new}.html")); n += 1
    write(os.path.join(SITE, "pt", "q", old, f"v{VER}.html"), stub(f"/pt/q/{new}/v{VER}.html")); n += 1
print(f"Wrote {n} redirect stubs (SQR-LIP-* -> SQ-LIP-*, EN+PT, main+snapshot).")
