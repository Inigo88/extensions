#!/usr/bin/env python3
"""Rewrite the bug registry summary line from table row counts and YAML markers."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from bugs_paths import load_config  # noqa: E402

BUG_ROW_LINK = re.compile(r"\[\s*B\d{3}\s*\]\s*\(")
SUMMARY_LINE_RE = re.compile(r"^> \*\*\d+ total\*\*.*$", re.MULTILINE)


def is_separator_table_line(line: str) -> bool:
    stripped = line.strip()
    if "|" not in stripped:
        return False
    parts = [p.strip() for p in stripped.split("|") if p.strip() != ""]
    if not parts:
        return False
    return all(re.fullmatch(r"[-:]+", p) for p in parts)


def is_bug_table_row(line: str) -> bool:
    if "|" not in line or is_separator_table_line(line):
        return False
    return bool(BUG_ROW_LINK.search(line))


def status_cell(line: str) -> str:
    cells = [c.strip() for c in line.strip().split("|")]
    cells = [c for c in cells if c]
    return cells[-1] if cells else ""


def count_bug_rows(text: str, markers: dict[str, str]) -> tuple[int, int, int, int]:
    """Return total bug rows, resolved count, open count, in-progress (non-open, non-resolved)."""
    total = 0
    n_resolved = 0
    n_open = 0
    n_in_progress = 0
    mr = markers.get("resolved", "")
    mo = markers.get("open", "")
    for line in text.splitlines():
        if not is_bug_table_row(line):
            continue
        total += 1
        st = status_cell(line)
        if st == mr:
            n_resolved += 1
        elif st == mo:
            n_open += 1
        else:
            n_in_progress += 1
    return total, n_resolved, n_open, n_in_progress


def build_summary_line(
    markers: dict[str, str], total: int, nr: int, no: int, nfp: int
) -> str:
    mr = markers.get("resolved", "✅")
    mo = markers.get("open", "🔴")
    mfp = markers.get("fix_proposed", "🟡")
    return (
        f"> **{total} total** · {mr} {nr} resolved · {mo} {no} open · {mfp} {nfp} fix proposed"
    )


def reconcile_registry_header(registry_path: Path, extension_root: Path) -> None:
    _, markers = load_config(extension_root)
    text = registry_path.read_text(encoding="utf-8")
    total, nr, no, nfp = count_bug_rows(text, markers)
    new_line = build_summary_line(markers, total, nr, no, nfp)
    if SUMMARY_LINE_RE.search(text):
        text = SUMMARY_LINE_RE.sub(new_line, text, count=1)
    else:
        needle = "# Bug registry"
        idx = text.find(needle)
        if idx != -1:
            insert_at = idx + len(needle)
            text = text[:insert_at] + "\n\n" + new_line + text[insert_at:]
        else:
            text = new_line + "\n\n" + text
    registry_path.write_text(text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "usage: reconcile_registry_header.py <registry_path> <extension_root>",
            file=sys.stderr,
        )
        sys.exit(2)
    reconcile_registry_header(
        Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    )


if __name__ == "__main__":
    main()
