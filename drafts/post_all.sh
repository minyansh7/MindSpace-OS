#!/usr/bin/env bash
# post_all.sh — Substack draft → publish (manual) → Twitter post (auto)
#
# Flow:
#   1. Runs post_to_substack.py which opens the Substack editor with your
#      draft pre-filled. You review, click Publish MANUALLY, copy the URL.
#   2. You paste the URL here.
#   3. Runs post_to_twitter.py with --link <URL>, substituting [link]
#      placeholders, and auto-posts the tweet (or thread).
#
# Usage:
#   ./drafts/post_all.sh                         # default: option A
#   ./drafts/post_all.sh B                       # tweet option B
#   ./drafts/post_all.sh C                       # single tweet C
#   ./drafts/post_all.sh thread                  # full thread
#   ./drafts/post_all.sh A --review              # review mode (no auto-post)
#
# Requires: prior `python3 drafts/post_to_substack.py --login`
#       and `python3 drafts/post_to_twitter.py  --login`
#
# Safety: the Substack publish click stays MANUAL. The Twitter auto-post
# happens after you've typed the URL — if you abort (Ctrl+C) before pasting,
# nothing is posted.

set -euo pipefail

# Resolve the repo root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PY=python3
DRAFT="drafts/launch-post.md"

# Parse first positional arg: A | B | C | thread (default A)
MODE="${1:-A}"
shift || true
EXTRA_ARGS=("$@")

TWITTER_CMD=("$PY" drafts/post_to_twitter.py --draft "$DRAFT")
case "$MODE" in
    A|B|C)
        TWITTER_CMD+=(--option "$MODE")
        ;;
    thread)
        TWITTER_CMD+=(--thread)
        ;;
    *)
        echo "ERROR: unknown mode '$MODE'. Use A, B, C, or thread." >&2
        exit 1
        ;;
esac

# Pass through any extra flags like --review
TWITTER_CMD+=("${EXTRA_ARGS[@]}")

echo "────────────────────────────────────────────────────────────"
echo "Step 1/2  Substack draft → editor"
echo "────────────────────────────────────────────────────────────"
echo "Opening Substack. Review the inserted draft, click Publish"
echo "manually, then COPY THE LIVE POST URL and come back here."
echo
"$PY" drafts/post_to_substack.py --draft "$DRAFT"

echo
echo "────────────────────────────────────────────────────────────"
echo "Step 2/2  Twitter"
echo "────────────────────────────────────────────────────────────"
read -r -p "Paste the published Substack URL (or blank to skip tweeting): " URL

if [[ -z "$URL" ]]; then
    echo "No URL provided — skipping tweet. Drafts remain in $DRAFT."
    exit 0
fi

# Sanity-check: URL should start with https://
if [[ ! "$URL" =~ ^https?:// ]]; then
    echo "ERROR: that doesn't look like a URL: $URL" >&2
    exit 1
fi

echo "Using link: $URL"
TWITTER_CMD+=(--link "$URL")

echo
echo "Command: ${TWITTER_CMD[*]}"
"${TWITTER_CMD[@]}"

echo
echo "Done."
