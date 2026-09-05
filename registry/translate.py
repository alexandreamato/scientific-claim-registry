#!/usr/bin/env python3
"""Auto-fill missing Brazilian-Portuguese fields (*_pt) in questions.json and claims.json
using OpenAI. Idempotent: only translates items that are missing a *_pt field, so existing
(human-reviewed) translations are never overwritten. This is how NEW questions/claims added
by the surveillance loop get a PT version automatically before the bilingual site is built.

Key: env OPENAI_API_KEY, or a token file at ~/.config/scr_openai_token.
Usage (from registry/):
  python3 translate.py            # fill all missing *_pt
  python3 translate.py --dry      # report what's missing, call nothing
  python3 translate.py --model gpt-4o-mini
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
QF = os.path.join(HERE, "questions.json")
CF = os.path.join(HERE, "claims.json")
MODEL = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "gpt-4o-mini"
DRY = "--dry" in sys.argv

# (source field -> target *_pt field) per object type
Q_FIELDS = [("text", "text_pt"), ("current_answer", "current_answer_pt"), ("major_uncertainty", "major_uncertainty_pt")]
C_FIELDS = [("statement", "statement_pt")]

SYS = ("You are a medical/scientific translator. Translate English to Brazilian Portuguese (pt-BR) "
       "for a clinical evidence registry. Preserve meaning, hedging, numbers, percentages, units, study "
       "designs and technical terms exactly. Do not add, omit, or soften claims. Keep it concise and natural. "
       "Return ONLY a JSON object mapping each given key to its translated string.")

def key():
    k = os.environ.get("OPENAI_API_KEY")
    if k: return k
    p = os.path.expanduser("~/.config/scr_openai_token")
    if os.path.exists(p): return open(p).read().strip()
    sys.exit("No OpenAI key: set OPENAI_API_KEY or write ~/.config/scr_openai_token")

def translate(payload, api):
    """payload: {target_key: english_text}. Returns {target_key: pt_text}."""
    body = json.dumps({
        "model": MODEL, "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": "Translate the values of this JSON to pt-BR, "
                      "keeping the same keys:\n" + json.dumps(payload, ensure_ascii=False)}],
    }).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {api}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read())
    return json.loads(d["choices"][0]["message"]["content"])

def missing(obj, fields):
    return {tgt: obj.get(src) for src, tgt in fields if obj.get(src) and not obj.get(tgt)}

def run(path, list_key, fields, api):
    data = json.load(open(path))
    items = data[list_key]
    todo = [(it, missing(it, fields)) for it in items]
    todo = [(it, m) for it, m in todo if m]
    label = os.path.basename(path)
    if not todo:
        print(f"{label}: all {len(items)} items already bilingual."); return 0
    print(f"{label}: {len(todo)} item(s) missing PT.")
    if DRY:
        for it, m in todo: print("  -", it.get("id"), list(m.keys()))
        return 0
    for it, m in todo:
        pt = translate(m, api)
        for k in m:
            if pt.get(k): it[k] = pt[k]
        print("  translated", it.get("id"))
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
    return len(todo)

def main():
    api = None if DRY else key()
    n = run(QF, "questions", Q_FIELDS, api) + run(CF, "claims", C_FIELDS, api)
    print(f"Done. {n} item(s) translated." if not DRY else "Dry run.")

if __name__ == "__main__":
    main()
