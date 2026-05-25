#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

CR_PATHS_PY="$EXTENSION_ROOT/scripts/python/change_requests_paths.py"
_CR_PATHS_OUT=$(python3 "$CR_PATHS_PY" "$EXTENSION_ROOT" "$REPO_ROOT")
SPECS_DIR=$(printf '%s\n' "$_CR_PATHS_OUT" | sed -n '1p')
REGISTRY_FILE=$(printf '%s\n' "$_CR_PATHS_OUT" | sed -n '2p')
CR_TEMPLATE="$EXTENSION_ROOT/templates/change-request-template.md"
REGISTRY_TEMPLATE="$EXTENSION_ROOT/templates/change-request-registry-template.md"
UPDATE_REGISTRY_PY="$EXTENSION_ROOT/scripts/python/update_cr_registry.py"
FORMAT_TITLE_PY="$EXTENSION_ROOT/scripts/python/format_feature_title.py"

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
  echo "Usage: $0 \"Change Request Title\" [--feature XXX-feature-name] [--feature-title \"override heading\"] [--short-name slug]"
  exit 1
fi

mkdir -p "$SPECS_DIR"
if [ ! -f "$REGISTRY_FILE" ]; then
  if [ -f "$REGISTRY_TEMPLATE" ]; then
    cp "$REGISTRY_TEMPLATE" "$REGISTRY_FILE"
    echo "Initialized change request registry from template."
  else
    echo "Error: Registry template not found at $REGISTRY_TEMPLATE"
    exit 1
  fi
fi

HIGHEST_ID=$(grep -oE 'CR[0-9]{3}' "$REGISTRY_FILE" 2>/dev/null | sed 's/CR//' | sort -rn | head -n 1 || true)
# Also scan existing CR files so ids stay monotonic if registry rows were removed
while IFS= read -r -d '' f; do
  bn=$(basename "$f")
  if [[ "$bn" =~ ^CR([0-9]{3})- ]]; then
    n="${BASH_REMATCH[1]}"
    if [ -z "$HIGHEST_ID" ] || [ "$((10#$n))" -gt "$((10#$HIGHEST_ID))" ]; then
      HIGHEST_ID="$n"
    fi
  fi
done < <(find "$SPECS_DIR" -type f -name 'CR*.md' -print0 2>/dev/null || true)

HIGHEST_ID="${HIGHEST_ID:-000}"
NEXT_ID_NUM=$((10#$HIGHEST_ID + 1))
NEXT_ID=$(printf "CR%03d" $NEXT_ID_NUM)

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

CR_FILENAME="${NEXT_ID}-${SHORT_NAME}.md"
CR_FILEPATH="$TARGET_DIR/$CR_FILENAME"
REL_CR_PATH="${FEATURE_ID}/${CR_FILENAME}"

if [ -f "$CR_TEMPLATE" ]; then
  python3 - "$CR_TEMPLATE" "$CR_FILEPATH" "$NEXT_ID" "$TITLE" <<'PY'
import sys
from datetime import date
from pathlib import Path

tpl_path, out_path, cr_id, title = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
text = tpl_path.read_text(encoding="utf-8")
text = text.replace("CRXXX", cr_id)
text = text.replace("[Title]", title)
text = text.replace("YYYY-MM-DD", date.today().strftime("%Y-%m-%d"))
out_path.write_text(text, encoding="utf-8")
PY
  echo "Created change request: $CR_FILEPATH"
else
  touch "$CR_FILEPATH"
  echo "Created empty change request (template missing): $CR_FILEPATH"
fi

TOTAL=0
COMPLETED=0
DRAFT=0
APPR=0
_tot=$(grep -oE '\*\*[0-9]+ total\*\*' "$REGISTRY_FILE" | head -n 1 || true)
if [[ "$_tot" =~ \*\*([0-9]+)\ total\*\* ]]; then
  TOTAL="${BASH_REMATCH[1]}"
fi
_comp=$(grep -oE '✅[[:space:]]+[0-9]+[[:space:]]+completed' "$REGISTRY_FILE" | head -n 1 || true)
if [[ "$_comp" =~ ✅[[:space:]]+([0-9]+)[[:space:]]+completed ]]; then
  COMPLETED="${BASH_REMATCH[1]}"
fi
_draft=$(grep -oE '🔴[[:space:]]+[0-9]+[[:space:]]+draft / in flight' "$REGISTRY_FILE" | head -n 1 || true)
if [[ "$_draft" =~ 🔴[[:space:]]+([0-9]+)[[:space:]]+draft ]]; then
  DRAFT="${BASH_REMATCH[1]}"
fi
_appr=$(grep -oE '🟡[[:space:]]+[0-9]+[[:space:]]+approved or in progress' "$REGISTRY_FILE" | head -n 1 || true)
if [[ "$_appr" =~ 🟡[[:space:]]+([0-9]+)[[:space:]]+approved ]]; then
  APPR="${BASH_REMATCH[1]}"
fi

NEW_TOTAL=$((TOTAL + 1))
NEW_DRAFT=$((DRAFT + 1))

TEMP_REGISTRY=$(mktemp)
sed \
  -e "s/\*\*${TOTAL} total\*\*/\*\*${NEW_TOTAL} total\*\*/" \
  -e "s/✅ ${COMPLETED} completed/✅ ${COMPLETED} completed/" \
  -e "s/🔴 ${DRAFT} draft/🔴 ${NEW_DRAFT} draft/" \
  -e "s/🟡 ${APPR} approved/🟡 ${APPR} approved/" \
  "$REGISTRY_FILE" > "$TEMP_REGISTRY"

if grep -qE "^## ${FEATURE_PREFIX}([^0-9]|\$)" "$TEMP_REGISTRY"; then
  python3 "$UPDATE_REGISTRY_PY" "$TEMP_REGISTRY" "$FEATURE_ID" "$NEXT_ID" "$REL_CR_PATH" "$TITLE" "$FEATURE_TITLE"
else
  {
    echo ""
    echo "## $FEATURE_TITLE"
    echo ""
    echo "| ID | Title | Summary | Status |"
    echo "|----|-------|---------|--------|"
    echo "| [$NEXT_ID]($REL_CR_PATH) | $TITLE | — | 🔴 |"
  } >> "$TEMP_REGISTRY"
fi

mv "$TEMP_REGISTRY" "$REGISTRY_FILE"
echo "Updated registry: $REGISTRY_FILE"

echo "Success: $NEXT_ID created."
