#!/bin/bash
# Weekly hygiene (launchd): (1) retraction scan + auto-ban; (2) rotating CONTRADICTION SWEEP (R-AI-12) —
# the loop always runs a contradiction-seeking retrieval pass (Europe PMC null/negative), here applied to
# 2 rotating questions/week so the evidence base keeps hunting disconfirming evidence automatically;
# (3) rebuild + deploy + purge ONLY if anything changed; (4) quality audit (report); (5) commit the
# week's evidence change to the public repo, so the history shows WHICH evidence moved. See the .plist.
# Uses system tools (python3 stdlib, rsync, curl, ssh) + the OpenRouter key (~/.config). bib is optional.
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
set -u
# Resolve o diretório raiz do projeto dinamicamente (Fase 1/2 de Descentralização)
BIO="$(cd "$(dirname "$0")/.."; pwd)"
LOG="$BIO/registry/retractions.log"
ZONE="d3acb1b294cdbd9c19e801ab83b495a5"
DEST="alexandre@91.98.19.157:/home/alexandre/web/scientificclaims.org/public_html/"

cd "$BIO/registry" || exit 1
echo "===== $(date '+%Y-%m-%d %H:%M') weekly hygiene =====" >> "$LOG"
BEFORE="$(md5 -q claims.json 2>/dev/null)$(md5 -q questions.json 2>/dev/null)"
# Corpus size before the run, so step (5) can state what this week actually added.
COUNTS_BEFORE="$(python3 -c "import json;c=json.load(open('claims.json'));cl=c['claims'] if isinstance(c,dict) else c;print(len(cl),sum(len(x.get('evidence',[])) for x in cl))" 2>/dev/null || echo '? ?')"

# (1) Retraction hygiene (R-CLM-10)
python3 curate.py check-retractions --ban >> "$LOG" 2>&1

# (1b) Evidence-title self-heal (R-CLM-16): backfill any DOI/PMID evidence missing a title, so the
# 'Evidence over time' hover / refs never regress to a bare DOI. Idempotent; then assert the guard.
python3 enrich_evidence.py >> "$LOG" 2>&1
if ! python3 enrich_evidence.py --check >> "$LOG" 2>&1; then
  echo "  ⚠ TITLE GUARD: DOI/PMID evidence without a title remains (see above) — R-CLM-16." >> "$LOG"
fi

# (2) Rotating contradiction sweep (R-AI-12): 2 questions/week, cycling through all.
QIDS=( $(python3 -c "import json;print(' '.join(sorted(q['id'] for q in json.load(open('questions.json'))['questions'])))") )
N=${#QIDS[@]}
PTR=$(cat .contra_rotation 2>/dev/null || echo 0)
SWEPT=""
for i in 0 1; do
  idx=$(( (PTR + i) % N )); qid="${QIDS[$idx]}"; SWEPT="$SWEPT $qid"
  python3 loop.py "$qid" --source all --accept 4 --commit >> "$LOG" 2>&1
done
echo $(( (PTR + 2) % N )) > .contra_rotation
echo "  contradiction sweep:$SWEPT" >> "$LOG"

# (2b) Language-leak guard (R-SITE-16): the sweep recompiles answers, which can drift to the wrong
# language (a bottom_line_pt in Spanish, a change_pt in English). Flag it before it ships.
if ! python3 lang_check.py >> "$LOG" 2>&1; then
  echo "  ⚠ LANG GUARD: field(s) in the wrong language (see above) — R-SITE-16." >> "$LOG"
fi

# (3) Rebuild + deploy ONLY if the retraction scan or the sweep changed the registry.
AFTER="$(md5 -q claims.json 2>/dev/null)$(md5 -q questions.json 2>/dev/null)"
if [ "$BEFORE" != "$AFTER" ]; then
  echo "  changes → rebuild + deploy" >> "$LOG"
  cd "$BIO/site" || exit 1
  python3 build_questions.py >> "$LOG" 2>&1
  python3 build_site.py >> "$LOG" 2>&1
  python3 build_home.py >> "$LOG" 2>&1
  rsync -az --delete --exclude='.inbox' --exclude='*.py' --exclude='deploy.md' --exclude='CLAUDE.md' \
        --exclude='.git' --exclude='.claude' -e "ssh -p 22 -o StrictHostKeyChecking=accept-new" \
        ./ "$DEST" >> "$LOG" 2>&1
  CF="${SCR_CF_TOKEN:-$( [ -f "$HOME/.config/scr_cf_token" ] && cat "$HOME/.config/scr_cf_token" )}"
  if [ -n "$CF" ]; then
    curl -s -X POST -H "Authorization: Bearer $CF" \
      -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$ZONE/purge_cache" \
      --data '{"purge_everything":true}' >> "$LOG" 2>&1
  fi
  echo "  deployed." >> "$LOG"
else
  echo "  no changes; nothing to deploy." >> "$LOG"
fi

# (4) Quality audit (R-CLM-13 safety net) — report-only.
cd "$BIO/registry" || exit 1
OVER=$(python3 audit_quality.py 2>/dev/null | sed -n 's/^=== OVER-GRADED.*(\([0-9]*\)).*/\1/p')
if [ -n "$OVER" ] && [ "$OVER" -gt 0 ]; then
  echo "  ⚠ QUALITY AUDIT: $OVER over-graded evidence item(s) vs curated bib grau — run audit_quality.py --fix + recompile." >> "$LOG"
else
  echo "  quality audit: clean (no over-grading)." >> "$LOG"
fi

# (5) Public provenance: record the week in the public repo, so the git history shows WHICH evidence
# moved — the project's own thesis (versioned memory) demonstrated in the repository, not just
# described in it.
#
# This commit is PATHSPEC-SCOPED and never touches the author's staging area. Both matter, because
# this runs unattended against a PUBLIC repo: `git commit` without a pathspec commits the WHOLE index,
# so anything left staged from an interrupted session would be published on Sunday at 04:30. With the
# pathspec, git builds a temporary index from HEAD + these two paths only; whatever else the author had
# staged stays staged and unpublished. The emptiness check is scoped the same way and compares the
# WORKING TREE against HEAD, so no `git add` is needed at all — the author's index is left untouched.
#
# Never fatal and never interactive — the deploy already succeeded above, so a network or credential
# failure may only become a log line. GIT_TERMINAL_PROMPT=0 makes git RETURN an error instead of
# blocking the cron forever on a password prompt (macOS ships no `timeout`), and the low-speed limits
# abort a transfer stalled under 1 KB/s for 30 s. NOTE: the push carries the whole branch, so any
# commit the author left unpushed on `main` goes out with it — that is git, not a leak, but it means
# `main` should not be used to park work that is not meant to be public.
if [ "$BEFORE" != "$AFTER" ] && [ -d "$BIO/.git" ]; then
  cd "$BIO" || exit 1
  COUNTS_AFTER="$(python3 -c "import json;c=json.load(open('registry/claims.json'));cl=c['claims'] if isinstance(c,dict) else c;print(len(cl),sum(len(x.get('evidence',[])) for x in cl))" 2>/dev/null || echo '? ?')"
  read -r CB EB <<< "$COUNTS_BEFORE"; read -r CA EA <<< "$COUNTS_AFTER"
  DELTA="claims $CB -> $CA, evidence $EB -> $EA"
  export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/usr/bin/true
  export GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=30
  SEEDS="registry/claims.json registry/questions.json"
  if git diff --quiet HEAD -- $SEEDS 2>/dev/null; then
    echo "  git: nothing to commit (seeds unchanged)." >> "$LOG"
  else
    git commit -q \
      -m "Weekly sweep $(date '+%Y-%m-%d'):$SWEPT" \
      -m "Layer 1 surveillance: rotating contradiction sweep (R-AI-12) over the questions above; new evidence verified on ingest (R-AI-13/14). Corpus: $DELTA." \
      -m "Automated by registry/cron_retractions.sh" \
      -- $SEEDS >> "$LOG" 2>&1
    if git push -q origin main >> "$LOG" 2>&1; then
      echo "  git: committed + pushed ($DELTA)." >> "$LOG"
    else
      echo "  ⚠ git: commit ok, PUSH FAILED — it will go out next run (or run: git -C \"$BIO\" push origin main)." >> "$LOG"
    fi
  fi
fi
