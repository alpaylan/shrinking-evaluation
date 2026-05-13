#!/usr/bin/env bash
# Mirror the lean-state objects from Cloudflare R2 into the local
# workspace, then run the dedup script to fold partial stores into
# the master `store.<wl>.det.jsonl`.
#
# Expects these env vars in your shell (`source ~/.r2-env` or similar):
#   R2_ACCOUNT_ID, R2_BUCKET,
#   R2_ACCESS_KEY_ID -> exported as AWS_ACCESS_KEY_ID,
#   R2_SECRET_ACCESS_KEY -> exported as AWS_SECRET_ACCESS_KEY
#
# Usage: scripts/lean_pull_r2.sh <workload-short>     # e.g. rbt

set -euo pipefail

WL="${1:?workload short name required, e.g. rbt}"
: "${R2_ACCOUNT_ID:?set R2_ACCOUNT_ID}"
: "${R2_BUCKET:?set R2_BUCKET}"
: "${R2_ACCESS_KEY_ID:?set R2_ACCESS_KEY_ID}"
: "${R2_SECRET_ACCESS_KEY:?set R2_SECRET_ACCESS_KEY}"

export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION=auto
ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

echo "Syncing state/lean/${WL}/ <- s3://${R2_BUCKET}/state/lean/${WL}/"
aws s3 sync --endpoint-url "$ENDPOINT" \
  "s3://${R2_BUCKET}/state/lean/${WL}/" "state/lean/${WL}/" \
  --no-progress

echo "Syncing partial-stores/ (workload prefix '${WL}') from R2"
aws s3 sync --endpoint-url "$ENDPOINT" \
  "s3://${R2_BUCKET}/partial-stores/" "partial-stores/" \
  --exclude "*" --include "lean-${WL}-*" --no-progress

MASTER="store.${WL}.det.jsonl"
touch "$MASTER"
shopt -s nullglob
fragments=(partial-stores/lean-"${WL}"-*.jsonl)
if [ "${#fragments[@]}" -gt 0 ]; then
  echo "Appending ${#fragments[@]} partial store fragment(s) to $MASTER"
  cat "${fragments[@]}" >> "$MASTER"
  python3 scripts/lean_dedup_store.py "$MASTER"
else
  echo "No partial stores to merge."
fi
