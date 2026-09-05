#!/bin/bash
# Weekly hygiene (launchd): (1) retraction scan + auto-ban; (2) rotating CONTRADICTION SWEEP (R-AI-12) —
# the loop always runs a contradiction-seeking retrieval pass (Europe PMC null/negative), here applied to
# 2 rotating questions/week so the evidence base keeps hunting disconfirming evidence automatically;
# (3) rebuild + deploy + purge ONLY if anything changed; (4) quality audit (report). See the .plist.
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
