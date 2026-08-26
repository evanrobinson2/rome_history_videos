#!/usr/bin/env bash
# Vercel "Ignored Build Step".
#
#   exit 0      -> SKIP the build
#   exit non-0  -> RUN the build
#
# Why this exists: on 2026-08-26 the hive pushed 80 commits to main in one day and
# 49 of them touched only `mind/` — pure memory sync with no app code in them.
# Every push triggered a production build, and the free tier's 100-deploys-per-day
# limit was exhausted, blocking deployment for 24 hours. The hivemind spent the
# deployment budget on thinking.
#
# Paths listed below cannot affect the built Next.js app. A commit that touches
# only those is skipped — BUT only when nothing app-relevant is pending since the
# previously deployed SHA.
#
# Race this also fixes: Vercel cancels in-flight builds when a newer commit lands.
# If an app commit is followed quickly by a mind-only tip, comparing only HEAD^..HEAD
# skips the tip and the canceled app build never ships. Diff against
# VERCEL_GIT_PREVIOUS_SHA (last deployment's commit) so pending app changes still build.
#
# Fails safe: if we cannot work out what changed, we build.

set -uo pipefail

# Directories that never affect the deployed app.
MEMORY_ONLY=(mind sessions)

EXCLUDES=()
for p in "${MEMORY_ONLY[@]}"; do
  EXCLUDES+=(":(exclude)${p}")
done

# Prefer the SHA of the last deployment when Vercel provides it.
BASE="${VERCEL_GIT_PREVIOUS_SHA:-}"
if [[ -z "$BASE" ]] || ! git rev-parse --verify "${BASE}^{commit}" >/dev/null 2>&1; then
  if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
    BASE="HEAD^"
  else
    echo "vercel-ignore-build: no previous SHA reachable — building to be safe"
    exit 1
  fi
fi

echo "vercel-ignore-build: comparing ${BASE} → HEAD"

if git diff --quiet "$BASE" HEAD -- . "${EXCLUDES[@]}"; then
  echo "vercel-ignore-build: only ${MEMORY_ONLY[*]}/ changed since ${BASE} — skipping build"
  exit 0
fi

echo "vercel-ignore-build: app-relevant changes present since ${BASE} — building"
git diff --name-only "$BASE" HEAD -- . "${EXCLUDES[@]}" | head -20
exit 1
