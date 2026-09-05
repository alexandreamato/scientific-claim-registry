#!/usr/bin/env python3
"""Deposit SCR v0.4 to Zenodo as a NEW VERSION of the concept DOI. Token via env ZENODO_TOKEN.

  prepare : newversion draft → clear inherited files → upload v0.4 bundle+changelog → set metadata (REVERSIBLE)
  status  : show the current draft (reserved DOI, files, metadata title/version)
  publish : POST actions/publish — IRREVERSIBLE, mints the version DOI

State (the new draft id) is cached in osf/.zenodo_draft.json so prepare→publish are separate runs.
"""
import os, sys, json, urllib.request, urllib.error

TOKEN = os.environ.get("ZENODO_TOKEN")
BASE = "https://zenodo.org/api"
PREV_ID = "20476673"  # v0.3 record/deposition id (the latest published version)
HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.join(HERE, "SCR-v0.4-bundle.zip")
CHANGELOG = os.path.join(HERE, "deposit_v0.4", "CHANGELOG-v0.4.md")
META = os.path.join(HERE, "zenodo_deposit_v0.4.json")
STATE = os.path.join(HERE, ".zenodo_draft.json")


def req(method, url, data=None, raw=False):
    h = {"Authorization": f"Bearer {TOKEN}"}
    if data is not None and not raw:
        data = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    elif raw:
        h["Content-Type"] = "application/octet-stream"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            b = resp.read()
            return resp.status, (json.loads(b) if b else {})
    except urllib.error.HTTPError as ex:
        return ex.code, ex.read().decode()[:800]


def prepare():
    st, dep = req("POST", f"{BASE}/deposit/depositions/{PREV_ID}/actions/newversion")
    if st not in (200, 201):
        sys.exit(f"newversion failed [{st}]: {dep}")
    draft_url = dep["links"]["latest_draft"]
    st, draft = req("GET", draft_url)
    if st != 200:
        sys.exit(f"get draft failed [{st}]: {draft}")
    newid = draft["id"]
    bucket = draft["links"]["bucket"]
    print(f"draft id: {newid}")
    # clear inherited files
    for f in draft.get("files", []):
        req("DELETE", f"{BASE}/deposit/depositions/{newid}/files/{f['id']}")
        print(f"  removed inherited file: {f.get('filename')}")
    # upload v0.4 bundle + changelog
    for path in (BUNDLE, CHANGELOG):
        name = os.path.basename(path)
        st, _ = req("PUT", f"{bucket}/{name}", data=open(path, "rb").read(), raw=True)
        print(f"  uploaded {name} [{st}]")
    # set metadata
    meta = json.load(open(META))
    st, r = req("PUT", f"{BASE}/deposit/depositions/{newid}", data=meta)
    if st != 200:
        sys.exit(f"metadata PUT failed [{st}]: {r}")
    doi = (r.get("metadata", {}).get("prereserve_doi") or {}).get("doi") or r.get("doi")
    json.dump({"id": newid, "doi": doi, "html": r["links"]["html"]}, open(STATE, "w"), indent=2)
    print(f"\n✓ draft ready (NOT published)\n  reserved DOI: {doi}\n  edit/review: {r['links']['html']}")


def upload():
    """(Re)upload the v0.4 files to the EXISTING cached draft — does not create a new version."""
    s = json.load(open(STATE))
    st, draft = req("GET", f"{BASE}/deposit/depositions/{s['id']}")
    if st != 200:
        sys.exit(f"get draft failed [{st}]: {draft}")
    for f in draft.get("files", []):
        req("DELETE", f"{BASE}/deposit/depositions/{s['id']}/files/{f['id']}")
        print(f"  removed stale file: {f.get('filename')}")
    bucket = draft["links"]["bucket"]
    for path in (BUNDLE, CHANGELOG):
        name = os.path.basename(path)
        st, r = req("PUT", f"{bucket}/{name}", data=open(path, "rb").read(), raw=True)
        print(f"  uploaded {name} [{st}]" + ("" if st in (200, 201) else f" {r}"))


def status():
    s = json.load(open(STATE))
    st, r = req("GET", f"{BASE}/deposit/depositions/{s['id']}")
    m = r.get("metadata", {})
    print(f"id {s['id']} · state={r.get('state')} · submitted={r.get('submitted')}")
    print(f"  title: {m.get('title','')[:90]}…")
    print(f"  version: {m.get('version')} · reserved DOI: {s.get('doi')}")
    print(f"  files: {[f.get('filename') for f in r.get('files', [])]}")
    print(f"  edit: {r['links']['html']}")


def publish():
    s = json.load(open(STATE))
    st, r = req("POST", f"{BASE}/deposit/depositions/{s['id']}/actions/publish")
    if st not in (200, 202):
        sys.exit(f"publish failed [{st}]: {r}")
    print(f"✓ PUBLISHED\n  DOI: {r.get('doi')}\n  record: {r['links'].get('record_html')}")


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("set ZENODO_TOKEN")
    {"prepare": prepare, "upload": upload, "status": status, "publish": publish}[sys.argv[1]]()
