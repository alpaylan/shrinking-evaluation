#!/usr/bin/env bash
# Pull R2 progress for every pending lean task in `store.<wl>.det.jsonl`
# and print one line per task: offset, partial-store row count, Failed
# row count. Useful for verifying that re-dispatches are actually
# advancing state.
#
# Usage: scripts/lean_r2_snapshot.sh [workload]   # default: rbt
#
# Reads CF creds from cf.token and cf.id at repo root (gitignored).

set -euo pipefail

WL="${1:-rbt}"
BUCKET=etna-lean-state

repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

[ -f cf.token ] || { echo "cf.token missing at $repo_root" >&2; exit 1; }
[ -f cf.id    ] || { echo "cf.id missing at $repo_root"    >&2; exit 1; }
export CLOUDFLARE_API_TOKEN=$(tr -d '\n\r ' < cf.token)
export CLOUDFLARE_ACCOUNT_ID=$(tr -d '\n\r ' < cf.id)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# Optional second arg: write the snapshot to this CSV path (for diffing
# across time). The script prints the human-readable table either way.
csv_out="${2:-}"

pending_json=$(python3 scripts/lean_pending_tasks.py "$WL")
n=$(echo "$pending_json" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["include"]))')
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "=== R2 snapshot for $WL @ $ts (pending=$n) ==="
printf "%-25s %-22s %12s %8s %8s\n" "MUTATION" "PROPERTY" "OFFSET" "ROWS" "FAILED"
printf -- "---------------------------------------------------------------------------------\n"

[ -n "$csv_out" ] && echo "ts,mutation,property,offset,rows,failed" > "$csv_out"

# Emit `MUT<TAB>PROP` lines for the pending list.
echo "$pending_json" | python3 -c '
import json,sys
for t in json.load(sys.stdin)["include"]:
    print(t["mutation"] + "\t" + t["property"])
' > "$tmpdir/pending.tsv"

sum_offset=0
sum_rows=0
done_count=0
while IFS=$'\t' read -r MUT PROP; do
  CKPT_KEY="state/lean/$WL/${MUT}_${PROP}.txt"
  STORE_KEY="partial-stores/lean-$WL-$MUT-$PROP.jsonl"
  CKPT_FILE="$tmpdir/${MUT}_${PROP}.ckpt"
  STORE_FILE="$tmpdir/${MUT}_${PROP}.jsonl"
  wrangler r2 object get "$BUCKET/$CKPT_KEY"  --file "$CKPT_FILE"  --remote >/dev/null 2>&1 || true
  wrangler r2 object get "$BUCKET/$STORE_KEY" --file "$STORE_FILE" --remote >/dev/null 2>&1 || true
  OFFSET=0
  ROWS=0
  FAILED=0
  if [ -s "$CKPT_FILE" ];  then OFFSET=$(tr -d '\n\r ' < "$CKPT_FILE"); fi
  if [ -s "$STORE_FILE" ]; then
    ROWS=$(awk 'END{print NR}' "$STORE_FILE")
    FAILED=$(awk '/"status":"Failed"/ {c++} END {print c+0}' "$STORE_FILE")
  fi
  printf "%-25s %-22s %12s %8s %8s\n" "$MUT" "$PROP" "$OFFSET" "$ROWS" "$FAILED"
  [ -n "$csv_out" ] && echo "$ts,$MUT,$PROP,$OFFSET,$ROWS,$FAILED" >> "$csv_out"
  sum_offset=$(( sum_offset + OFFSET ))
  sum_rows=$(( sum_rows + ROWS ))
  [ "$FAILED" -gt 0 ] && done_count=$(( done_count + 1 ))
done < "$tmpdir/pending.tsv"

printf -- "---------------------------------------------------------------------------------\n"
printf "%-48s %12s %8s %8s\n" "TOTAL ($n tasks, $done_count done)" "$sum_offset" "$sum_rows" "$done_count"
