#!/usr/bin/env bash
# Idempotent: creates .project subfolders and .gitkeep placeholders only when missing.
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

SUBDIRS=(assets backlog context documents crs bugs)

mkdir -p ".project"
for d in "${SUBDIRS[@]}"; do
  mkdir -p ".project/${d}"
  if [[ ! -f ".project/${d}/.gitkeep" ]]; then
    touch ".project/${d}/.gitkeep"
  fi
done

echo "OK: .project layout ensured under $(pwd)"
