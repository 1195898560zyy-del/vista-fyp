#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$repo_dir"

git_status=$(git status -sb)
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "[deploy] Working tree has uncommitted changes. Commit first."
  echo "$git_status"
  exit 1
fi

echo "[deploy] Pulling latest..."
git pull --rebase

branch=$(git rev-parse --abbrev-ref HEAD)

echo "[deploy] Pushing $branch..."
git push origin "$branch"

cat <<'MSG'
[deploy] Done. GitHub Pages will update shortly.
MSG
