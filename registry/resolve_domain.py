#!/usr/bin/env python3
"""Resolve a disease name to authoritative cross-references and (optionally) write them into
registry/domains.json — so adding a domain never requires typing or inventing a code.

Strategy: MONDO is the hub. We find the MONDO term (EBI OLS4, no key), harvest its built-in
xrefs (MeSH / OMIM / Orphanet / UMLS / SNOMED-CT / MedDRA / HPO), and — if WHO credentials are
present — fetch the ICD-11 MMS code from the WHO ICD-API (MONDO's ICD coverage is partial).
Nothing is fabricated: anything not found stays null.

WHO ICD-11 (optional): set env ICD_CLIENT_ID + ICD_CLIENT_SECRET, or a file
~/.config/scr_icd_token containing 'client_id:client_secret'. Register free at https://icd.who.int.

Usage (from registry/):
  python3 resolve_domain.py "Lymphedema"                 # resolve + print (dry run)
  python3 resolve_domain.py "Lymphedema" --code LYM --write   # write/merge into domains.json
  python3 resolve_domain.py "Lipedema" --code LIP --pick 0    # choose candidate 0 if ambiguous
"""
import json, os, sys, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DOMAINS = os.path.join(HERE, "domains.json")
OLS = "https://www.ebi.ac.uk/ols4/api"
# OLS database label -> our field name
XMAP = {"MESH": "mesh", "OMIM": "omim", "Orphanet": "orphanet", "ORPHANET": "orphanet",
        "UMLS": "umls", "SCTID": "snomedct", "MedDRA": "meddra", "MEDDRA": "meddra",
        "HP": "hp", "HPO": "hp", "MEDGEN": "medgen"}


def _get(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def mondo_candidates(name):
    url = f"{OLS}/search?q={urllib.parse.quote(name)}&ontology=mondo&rows=8"
    docs = _get(url).get("response", {}).get("docs", [])
    out = []
    for d in docs:
        oid = d.get("obo_id")
        if oid and oid.startswith("MONDO:"):
            out.append({"id": oid, "iri": d.get("iri"), "label": d.get("label", ""),
                        "defining": d.get("is_defining_ontology", False)})
    # exact (case-insensitive) label match first, then defining-ontology, preserve order otherwise
    out.sort(key=lambda c: (c["label"].lower() != name.lower(), not c["defining"]))
    return out


def mondo_xrefs(iri):
    url = f"{OLS}/ontologies/mondo/terms?iri={urllib.parse.quote(iri, safe='')}"
    term = _get(url)["_embedded"]["terms"][0]
    label = term.get("label", "")
    syns = [s for s in (term.get("obo_synonym") or []) if isinstance(s, str)]
    if not syns:
        syns = [s.get("name") for s in (term.get("obo_synonym") or []) if isinstance(s, dict) and s.get("name")]
    fields = {}
    for x in term.get("obo_xref") or []:
        db, xid = x.get("database"), x.get("id")
        if not db or not xid:
            continue
        key = XMAP.get(db) or XMAP.get(db.upper())
        if key:
            if key == "hp" and not str(xid).upper().startswith("HP:"):
                xid = "HP:" + str(xid)
            fields.setdefault(key, str(xid))
    return label, syns[:6], fields


def icd11_code(name):
    """Return ICD-11 MMS code via WHO ICD-API, or None if no credentials / not found."""
    cid = os.environ.get("ICD_CLIENT_ID"); sec = os.environ.get("ICD_CLIENT_SECRET")
    if not (cid and sec):
        p = os.path.expanduser("~/.config/scr_icd_token")
        if os.path.exists(p) and ":" in open(p).read():
            cid, sec = open(p).read().strip().split(":", 1)
    if not (cid and sec):
        return None, "no-credentials"
    try:
        data = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid,
                                       "client_secret": sec, "scope": "icdapi_access"}).encode()
        req = urllib.request.Request("https://icdaccessmanagement.who.int/connect/token", data=data,
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        tok = json.loads(urllib.request.urlopen(req, timeout=40).read())["access_token"]
        url = f"https://id.who.int/icd/release/11/2024-01/mms/search?q={urllib.parse.quote(name)}&flatResults=true"
        res = _get(url, headers={"Authorization": f"Bearer {tok}", "Accept": "application/json",
                                 "Accept-Language": "en", "API-Version": "v2"})
        ents = res.get("destinationEntities") or []
        if ents:
            import re as _re
            code = ents[0].get("theCode")
            title = _re.sub("<[^>]+>", "", ents[0].get("title", ""))
            return code, title
        return None, "not-found"
    except Exception as ex:
        return None, f"error:{ex}"


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        sys.exit("Usage: resolve_domain.py \"<disease name>\" [--code XXX] [--pick N] [--write]")
    name = args[0]
    code = args[args.index("--code") + 1].upper() if "--code" in args else None
    pick = int(args[args.index("--pick") + 1]) if "--pick" in args else None
    do_write = "--write" in args

    cands = mondo_candidates(name)
    if not cands:
        sys.exit(f"No MONDO term found for '{name}'.")
    print("MONDO candidates:")
    for i, c in enumerate(cands):
        print(f"  [{i}] {c['id']}  {c['label']}{'  (defining)' if c['defining'] else ''}")
    chosen = cands[pick] if pick is not None else cands[0]
    print(f"→ using {chosen['id']} ({chosen['label']})")

    label, syns, fields = mondo_xrefs(chosen["iri"])
    icd, icd_note = icd11_code(name)

    resolved = {"mondo": chosen["id"], "icd11": icd, "mesh": fields.pop("mesh", None),
                "xrefs": fields, "name": label, "aliases": syns}
    print("\nResolved cross-references:")
    print(f"  MONDO    {resolved['mondo']}")
    print(f"  ICD-11   {icd or '—'}  ({icd_note})")
    print(f"  MeSH     {resolved['mesh'] or '—'}")
    for k, v in resolved["xrefs"].items():
        print(f"  {k:8s} {v}")

    if not do_write:
        print("\n(dry run — add --code XXX --write to persist into domains.json)")
        return
    if not code:
        sys.exit("\n--write requires --code XXX (the namespace shard, 2-4 uppercase letters).")

    data = json.load(open(DOMAINS))
    entry = next((d for d in data["domains"] if d["code"] == code), None)
    new = entry is None
    if new:
        entry = {"code": code, "name": label, "aliases": syns, "status": "proposed",
                 "search_term": name.lower(), "created": data.get("date", "2026-05-30")}
        data["domains"].append(entry)
    entry["mondo"] = resolved["mondo"]
    entry["mesh"] = resolved["mesh"] or entry.get("mesh")
    entry["icd11"] = icd or entry.get("icd11")        # never clobber a manual ICD with null
    entry["xrefs"] = {**(entry.get("xrefs") or {}), **resolved["xrefs"]}
    if not entry.get("aliases"):
        entry["aliases"] = syns
    json.dump(data, open(DOMAINS, "w"), ensure_ascii=False, indent=2)
    print(f"\n{'Added' if new else 'Updated'} domain '{code}' in domains.json"
          + ("" if icd else "  (ICD-11 left as-is — set WHO creds to auto-fill)"))


if __name__ == "__main__":
    main()
