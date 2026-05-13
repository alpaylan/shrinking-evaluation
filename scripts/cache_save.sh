#!/usr/bin/env bash
# Save files to GitHub Actions Cache via the internal REST API.
# This is what `actions/cache/save@v4` does under the hood, exposed
# here so we can call it from a watchdog loop mid-step (the standard
# action only runs once, and only at the end of a step).
#
# Usage:
#   ACTIONS_RUNTIME_TOKEN=... ACTIONS_CACHE_URL=... \
#   cache_save.sh <cache-key> <file1> [<file2> ...]
#
# Files are tarred with paths relative to $GITHUB_WORKSPACE so a
# matching `actions/cache/restore@v4` step (using the same paths)
# extracts them back to the right place.
#
# Exits 0 on success, prints a warning and exits 0 if the cache
# already exists for this key (idempotent, harmless), exits non-zero
# only on transport/auth errors.

set -euo pipefail

KEY="${1:?cache key required}"
shift
FILES=("$@")
if [ "${#FILES[@]}" -eq 0 ]; then
  echo "cache_save: no files provided" >&2
  exit 2
fi

if [ -z "${ACTIONS_RUNTIME_TOKEN:-}" ] || [ -z "${ACTIONS_CACHE_URL:-}" ]; then
  echo "cache_save: ACTIONS_RUNTIME_TOKEN / ACTIONS_CACHE_URL not set; runner must expose these" >&2
  exit 3
fi

VERSION="lean-state-v1-tar"
WS="${GITHUB_WORKSPACE:-$PWD}"
BASE_URL="${ACTIONS_CACHE_URL%/}/_apis/artifactcache"

TARFILE=$(mktemp /tmp/cache-XXXXXX.tar)
trap 'rm -f "$TARFILE"' EXIT

# Tar with relative paths so the matching restore lands files
# back in $GITHUB_WORKSPACE without absolute-path surprises.
( cd "$WS" && tar -cf "$TARFILE" "${FILES[@]}" )
SIZE=$(wc -c < "$TARFILE" | tr -d ' ')

auth_hdr=(-H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
          -H "Accept: application/json;api-version=6.0-preview.1")

# 1. Reserve a cache slot for this key.
reserve_resp=$(curl -sS -w '\n%{http_code}' \
  "${auth_hdr[@]}" \
  -H "Content-Type: application/json" \
  -X POST "${BASE_URL}/caches" \
  -d "{\"key\":\"$KEY\",\"version\":\"$VERSION\",\"cacheSize\":$SIZE}")
reserve_code=$(echo "$reserve_resp" | tail -n1)
reserve_body=$(echo "$reserve_resp" | sed '$d')

if [ "$reserve_code" = "409" ]; then
  echo "cache_save: key already exists ($KEY) — skipping" >&2
  exit 0
fi
if [ "$reserve_code" != "201" ] && [ "$reserve_code" != "200" ]; then
  echo "cache_save: reserve failed (HTTP $reserve_code): $reserve_body" >&2
  exit 4
fi
CACHE_ID=$(echo "$reserve_body" | sed -n 's/.*"cacheId":[[:space:]]*\([0-9]*\).*/\1/p')
if [ -z "$CACHE_ID" ]; then
  echo "cache_save: could not parse cacheId from: $reserve_body" >&2
  exit 5
fi

# 2. Upload the tarball bytes.
upload_code=$(curl -sS -o /dev/null -w '%{http_code}' \
  "${auth_hdr[@]}" \
  -H "Content-Type: application/octet-stream" \
  -H "Content-Range: bytes 0-$((SIZE-1))/*" \
  -X PATCH "${BASE_URL}/caches/${CACHE_ID}" \
  --data-binary "@$TARFILE")
if [ "$upload_code" != "204" ] && [ "$upload_code" != "200" ]; then
  echo "cache_save: upload failed (HTTP $upload_code)" >&2
  exit 6
fi

# 3. Commit (finalise) the cache entry.
commit_code=$(curl -sS -o /dev/null -w '%{http_code}' \
  "${auth_hdr[@]}" \
  -H "Content-Type: application/json" \
  -X POST "${BASE_URL}/caches/${CACHE_ID}" \
  -d "{\"size\":$SIZE}")
if [ "$commit_code" != "204" ] && [ "$commit_code" != "200" ]; then
  echo "cache_save: commit failed (HTTP $commit_code)" >&2
  exit 7
fi

echo "cache_save: ok key=$KEY size=${SIZE}B id=$CACHE_ID"
