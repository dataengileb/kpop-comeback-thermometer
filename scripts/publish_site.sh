#!/usr/bin/env bash
# Publishes site/ as it is committed on the current branch to the gh-pages branch, which
# GitHub Pages serves. Run ./scripts/fetch_export.sh and commit site/data/ first.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! git diff --quiet HEAD -- site; then
  echo "site/ has uncommitted changes; commit them first." >&2
  exit 1
fi
git push origin "$(git subtree split --prefix site):refs/heads/gh-pages" --force
