#!/usr/bin/env bash

set -e

# Extension root: .../bugs/scripts/bash -> bugs/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

BUGS_PATHS_PY="$EXTENSION_ROOT/scripts/python/bugs_paths.py"
_BUGS_PATHS_OUT=$(python3 "$BUGS_PATHS_PY" "$EXTENSION_ROOT" "$REPO_ROOT")
SPECS_DIR=$(printf '%s\n' "$_BUGS_PATHS_OUT" | sed -n '1p')
REGISTRY_FILE=$(printf '%s\n' "$_BUGS_PATHS_OUT" | sed -n '2p')
STATUS_OPEN=$(printf '%s\n' "$_BUGS_PATHS_OUT" | sed -n '3p')
BUG_TEMPLATE="$EXTENSION_ROOT/templates/bug-template.md"
REGISTRY_TEMPLATE="$EXTENSION_ROOT/templates/bug-report-registry-template.md"
UPDATE_REGISTRY_PY="$EXTENSION_ROOT/scripts/python/update_registry.py"
RECONCILE_HEADER_PY="$EXTENSION_ROOT/scripts/python/reconcile_registry_header.py"
FORMAT_TITLE_PY="$EXTENSION_ROOT/scripts/python/format_feature_title.py"

# Arguments
TITLE=""
FEATURE_ID=""
FEATURE_TITLE=""
SHORT_NAME=""

while [ $# -gt 0 ]; do
  case "$1" in
    --feature) FEATURE_ID="$2"; shift 2 ;;
    --feature-title) FEATURE_TITLE="$2"; shift 2 ;;
    --short-name) SHORT_NAME="$2"; shift 2 ;;
    *) TITLE="$1"; shift ;;
  esac
done

if [ -z "$TITLE" ]; then
  echo "Usage: $0 \"Bug Title\" [--feature XXX-feature-name] [--feature-title \"override heading\"] [--short-name slug]"
  exit 1
fi

mkdir -p "$SPECS_DIR"
if [ ! -f "$REGISTRY_FILE" ]; then
  if [ -f "$REGISTRY_TEMPLATE" ]; then
    cp "$REGISTRY_TEMPLATE" "$REGISTRY_FILE"
    echo "Initialized bug registry from template."
  else
    echo "Error: Registry template not found at $REGISTRY_TEMPLATE"
    exit 1
  fi
fi

HIGHEST_ID=$(grep -oE 'B[0-9]{3}' "$REGISTRY_FILE" 2>/dev/null | sed 's/B//' | sort -rn | head -n 1 || true)
HIGHEST_ID="${HIGHEST_ID:-000}"
NEXT_ID_NUM=$((10#$HIGHEST_ID + 1))
NEXT_ID=$(printf "B%03d" $NEXT_ID_NUM)

if [ -z "$FEATURE_ID" ]; then
  FEATURE_ID="000-general"
fi

if [[ "$FEATURE_ID" =~ ^[0-9]{3}$ ]]; then
  if [ -d "$REPO_ROOT/specs" ]; then
    MATCHING_DIR=$(find "$REPO_ROOT/specs" -maxdepth 1 -type d -name "$FEATURE_ID-*" -exec basename {} \; 2>/dev/null | head -n 1)
    if [ -n "$MATCHING_DIR" ]; then
      FEATURE_ID="$MATCHING_DIR"
    fi
  fi
fi

FEATURE_PREFIX="${FEATURE_ID:0:3}"
if [ -z "$FEATURE_TITLE" ]; then
  FEATURE_TITLE=$(python3 "$FORMAT_TITLE_PY" "$FEATURE_ID")
fi

TARGET_DIR="$SPECS_DIR/$FEATURE_ID"
mkdir -p "$TARGET_DIR"

if [ -z "$SHORT_NAME" ]; then
  SHORT_NAME=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)
fi

BUG_FILENAME="${NEXT_ID}-${SHORT_NAME}.md"
BUG_FILEPATH="$TARGET_DIR/$BUG_FILENAME"
REL_BUG_PATH="${FEATURE_ID}/${BUG_FILENAME}"

if [ -f "$BUG_TEMPLATE" ]; then
  python3 - "$BUG_TEMPLATE" "$BUG_FILEPATH" "$NEXT_ID" "$TITLE" <<'PY'
import sys
from datetime import date
from pathlib import Path

tpl_path, out_path, bug_id, title = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
text = tpl_path.read_text(encoding="utf-8")
text = text.replace("BXXX", bug_id)
text = text.replace("[Title]", title)
text = text.replace("YYYY-MM-DD", date.today().strftime("%Y-%m-%d"))
out_path.write_text(text, encoding="utf-8")
PY
  echo "Created bug report: $BUG_FILEPATH"
else
  touch "$BUG_FILEPATH"
  echo "Created empty bug report (template missing): $BUG_FILEPATH"
fi

TEMP_REGISTRY=$(mktemp)
cp "$REGISTRY_FILE" "$TEMP_REGISTRY"

if grep -qE "^## ${FEATURE_PREFIX}([^0-9]|\$)" "$TEMP_REGISTRY"; then
  python3 "$UPDATE_REGISTRY_PY" "$TEMP_REGISTRY" "$FEATURE_ID" "$NEXT_ID" "$REL_BUG_PATH" "$TITLE" "$FEATURE_TITLE" "$STATUS_OPEN"
else
  {
    echo ""
    echo "## $FEATURE_TITLE"
    echo ""
    echo "| ID | Title | Fix | Status |"
    echo "|----|-------|-----|--------|"
    echo "| [$NEXT_ID]($REL_BUG_PATH) | $TITLE | — | $STATUS_OPEN |"
  } >> "$TEMP_REGISTRY"
fi

python3 "$RECONCILE_HEADER_PY" "$TEMP_REGISTRY" "$EXTENSION_ROOT"

mv "$TEMP_REGISTRY" "$REGISTRY_FILE"
echo "Updated registry: $REGISTRY_FILE"

echo "Success: $NEXT_ID created."
