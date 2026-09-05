#!/bin/zsh
# Scale the R-AI-13/14 audit across ALL questions, committing per question so progress is saved
# incrementally (a failure loses at most one question). Already-verified evidence is skipped
# (no --reverify), so this is idempotent and resumable — re-running only audits what's left.
cd "$(dirname "$0")"
QIDS=$(python3 -c "import json;[print(q['id']) for q in json.load(open('questions.json'))['questions']]")
total=$(echo "$QIDS" | wc -l | tr -d ' ')
i=0
for qid in ${(f)QIDS}; do
  i=$((i+1))
  echo "############### [$i/$total] $qid ###############"
  python3 verify_claims.py "$qid" --commit 2>&1 | grep -E "to audit|verified:|FABRICATION|DISPUTED|DB synced" || echo "  (no output)"
done
echo "=== AUDIT-ALL COMPLETE ==="
