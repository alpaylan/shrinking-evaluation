#!/usr/bin/env bash
# Diff two CSV snapshots written by scripts/lean_r2_snapshot.sh.
# Shows per-task offset delta and flags any task that newly acquired
# a Failed row.
#
# Usage: scripts/lean_r2_diff.sh OLD.csv NEW.csv
#
# With no args, diffs the two most recent snapshots in .r2-snapshots/.

set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

if [ $# -eq 0 ]; then
  shopt -s nullglob
  files=( $(ls -t .r2-snapshots/snap-*.csv 2>/dev/null) )
  [ "${#files[@]}" -ge 2 ] || { echo "need >=2 snapshots in .r2-snapshots/" >&2; exit 1; }
  NEW="${files[0]}"
  OLD="${files[1]}"
elif [ $# -eq 2 ]; then
  OLD="$1"; NEW="$2"
else
  echo "usage: $0 [OLD.csv NEW.csv]" >&2
  exit 1
fi

echo "OLD: $OLD"
echo "NEW: $NEW"
echo ""

python3 - "$OLD" "$NEW" <<'PY'
import csv, sys
old_path, new_path = sys.argv[1], sys.argv[2]

def load(p):
    out = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            key = (r["mutation"], r["property"])
            out[key] = (int(r["offset"]), int(r["rows"]), int(r["failed"]))
    return out

old = load(old_path)
new = load(new_path)
keys = sorted(set(old) | set(new))

print(f"{'MUTATION':25} {'PROPERTY':22} {'ΔOFFSET':>14} {'ΔROWS':>8} {'NEW_FAILED':>11}")
print("-"*84)
total_d_off = 0
total_d_rows = 0
newly_done = 0
for k in keys:
    o_off, o_rows, o_fail = old.get(k, (0,0,0))
    n_off, n_rows, n_fail = new.get(k, (0,0,0))
    d_off = n_off - o_off
    d_rows = n_rows - o_rows
    new_failed = "yes" if (n_fail > 0 and o_fail == 0) else ("done" if n_fail > 0 else "-")
    marker = " *" if (new_failed == "yes") else ""
    print(f"{k[0]:25} {k[1]:22} {d_off:>+14d} {d_rows:>+8d} {new_failed:>11}{marker}")
    total_d_off += d_off
    total_d_rows += d_rows
    if new_failed == "yes":
        newly_done += 1
print("-"*84)
print(f"{'TOTAL':48} {total_d_off:>+14d} {total_d_rows:>+8d} {newly_done:>11}")
PY
