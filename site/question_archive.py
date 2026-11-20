"""Render citable question versions from the registry's frozen records."""
import html
import json
from pathlib import Path

from scrlib import cite_link


def load_archives(registry):
    archives = {}
    for path in sorted((Path(registry) / "question_versions").glob("*/v*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        qid, version = record["id"], record["version"]
        if path.parent.name != qid or path.stem != f"v{version}":
            raise ValueError(f"Archive identity does not match {path}")
        archives.setdefault(qid, {})[version] = (record, path)
    for versions in archives.values():
        for record, path in versions.values():
            change = record.get("change")
            if not change:
                continue
            if change["previous_version"] not in versions:
                raise ValueError(f"Previous version missing for {path}")
            for link in change["evidence"]:
                evidence_anchor(record, link)
    return archives


def evidence_anchor(record, link):
    for claim in record["claims"]:
        if claim["id"] == link["claim_id"]:
            for index, row in enumerate(claim["evidence"], 1):
                if row.get("ref") == link["ref"] and row.get("quote"):
                    return f'{claim["id"]}-evidence-{index}'
    raise ValueError(f'Archived evidence with a source excerpt missing: {link}')


def change_section(record, lang, prefix):
    change = record.get("change")
    if not change:
        return ""
    esc = html.escape
    pt = lang == "pt"
    suffix = "_pt" if pt else ""
    base = f'{prefix}/q/{record["id"]}/v'
    previous = f'{base}{change["previous_version"]}.html'
    version = record["version"]
    current = f'{base}{version}.html'
    sources = " · ".join(
        f'<a href="{current}#{evidence_anchor(record, link)}">{esc(link["claim_id"])}</a>'
        for link in change["evidence"]
    )
    return f'''<section class="whatsnew" aria-labelledby="archived-change">
  <h2 class="wn-h" id="archived-change">{"O que mudou" if pt else "What changed"} · v{esc(version)}</h2>
  <p>{esc(change["summary" + suffix])}</p>
  <p><strong>{"População" if pt else "Population"}</strong> · {esc(change["population" + suffix])}</p>
  <p><strong>{"Desfecho" if pt else "Outcome"}</strong> · {esc(change["outcome" + suffix])}</p>
  <p><a href="{previous}">{"Versão anterior" if pt else "Previous version"} · v{esc(change["previous_version"])}</a>
  · {"Achados e trechos" if pt else "Findings and excerpts"} · {sources}</p>
</section>'''


def archive_body(record, lang, prefix, url):
    esc = html.escape
    pt = lang == "pt"
    suffix = "_pt" if pt else ""
    qid, version, date = (record[key] for key in ("id", "version", "date"))
    question = record["question"]
    title = question.get("text" + suffix) or question["text"]
    answer = question.get("current_answer" + suffix) or question["current_answer"]
    uncertainty = question.get("major_uncertainty" + suffix) or question.get("major_uncertainty", "")
    claims = []
    for claim in record["claims"]:
        rows = []
        for index, evidence in enumerate(claim["evidence"], 1):
            finding = evidence.get("finding")
            quote = evidence.get("quote")
            location = evidence.get("quote_location")
            citation = cite_link(evidence) if evidence.get("ref") else esc(evidence.get("title") or "")
            labels = ("Grau", "Risco de viés", "Verificação") if pt else ("Grade", "Risk of bias", "Verification")
            metadata = " · ".join(
                f"{label} {esc(evidence[key])}"
                for label, key in zip(labels, ("grade", "risk_of_bias", "verification_verdict"))
                if evidence.get(key)
            )
            rows.append(
                f'<li id="{claim["id"]}-evidence-{index}">{citation}'
                + (f'<p class="small muted">{metadata}</p>' if metadata else "")
                + (f'<p>{esc(finding)}</p>' if finding else "")
                + (f'<blockquote>{esc(quote)}</blockquote>' if quote else "")
                + (f'<p class="small muted">{esc(location)}</p>' if isinstance(location, str) else "")
                + "</li>"
            )
        statement = claim.get("statement" + suffix) or claim["statement"]
        role = {"supporting": "favorável", "contradicting": "contraditório",
                "refines": "refina", "context": "contextual"}.get(claim["role"], claim["role"]) if pt else claim["role"]
        claims.append(f'<li><strong>{esc(claim["id"])}</strong> · {esc(role)}'
                      f'<p>{esc(statement)}</p><ol>{"".join(rows)}</ol></li>')
    label = "Versão arquivada" if pt else "Archived version"
    return f'''<main class="qpage wrap">
  <p class="qid mono">{esc(qid)} · v{esc(version)} · {esc(date)} · {label}</p>
  <p><a href="{prefix}/q/{qid}.html">{"Pergunta atual" if pt else "Current question"}</a>
  · <a href="/q/{qid}/v{version}.json">JSON</a></p>
  <h1 class="qtitle">{esc(title)}</h1>
  <div class="answer"><p>{esc(answer)}</p></div>
  {change_section(record, lang, prefix)}
  <h2>{"Principal incerteza" if pt else "Major uncertainty"}</h2>
  <p>{esc(uncertainty)}</p>
  <h2>{"Proposições e evidências registradas" if pt else "Recorded propositions and evidence"}</h2>
  <ol class="qclaims">{"".join(claims)}</ol>
  <h2>{"Como citar" if pt else "How to cite"}</h2>
  <p>Scientific Claim Registry. {esc(title)}. {esc(qid)} v{esc(version)}. {esc(date)}.
  <a href="{esc(url)}">{esc(url)}</a></p>
</main>'''
