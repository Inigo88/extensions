#!/usr/bin/env python3
"""Append a bug row to the correct feature section in bug-report.md."""
import re
import sys


def usage() -> None:
    print(
        "Usage: python3 update_registry.py <registry_path> <feature_id> "
        "<next_id> <rel_path> <title> <feature_title> [<open_status_marker>]"
    )
    sys.exit(1)


def is_heading(line: str) -> bool:
    return line.startswith("## ")


def is_separator_table_line(line: str) -> bool:
    """True for markdown table separator rows like |----|---|."""
    stripped = line.strip()
    if "|" not in stripped:
        return False
    parts = [p.strip() for p in stripped.split("|") if p.strip() != ""]
    if not parts:
        return False
    return all(re.fullmatch(r"[-:]+", p) for p in parts)


def section_heading_matches(line: str, feature_prefix: str) -> bool:
    """Match ## 000 — Title but not ## 0001 other (prefix is 3-char feature id start)."""
    if not line.startswith("## " + feature_prefix):
        return False
    rest = line[3 + len(feature_prefix) :]
    if not rest:
        return True
    return not rest[0].isdigit()


def main() -> None:
    if len(sys.argv) < 7:
        usage()

    registry_path = sys.argv[1]
    feature_id = sys.argv[2]
    next_id = sys.argv[3]
    rel_path = sys.argv[4]
    title = sys.argv[5]
    feature_title = sys.argv[6]
    open_marker = sys.argv[7] if len(sys.argv) > 7 else "🔴"
    feature_prefix = feature_id[:3]

    new_row = (
        f"| [{next_id}]({rel_path}) | {title} | — | {open_marker} |\n"
    )
    table_header = "| ID | Title | Fix | Status |\n"
    table_sep = "|----|-------|-----|--------|\n"
    table_block = ["\n", table_header, table_sep, new_row]

    with open(registry_path, encoding="utf-8") as f:
        lines = f.readlines()

    section_start = None
    for i, line in enumerate(lines):
        if section_heading_matches(line, feature_prefix):
            section_start = i
            break

    if section_start is None:
        if not feature_title.strip():
            print(
                "Error: registry has no ## heading for this feature prefix; "
                "feature_title is required (set via create-bug.sh --feature-title).",
                file=sys.stderr,
            )
            sys.exit(1)
        lines.extend(
            [
                f"\n## {feature_title}\n\n",
                table_header,
                table_sep,
                new_row,
            ]
        )
    else:
        end = len(lines)
        for j in range(section_start + 1, len(lines)):
            if is_heading(lines[j]):
                end = j
                break

        head = lines[: section_start + 1]
        body = lines[section_start + 1 : end]
        tail = lines[end:]

        insert_after_in_body = -1
        pipe_indices = [i for i, ln in enumerate(body) if "|" in ln]

        if not pipe_indices:
            insert_after_in_body = -1
        else:
            # Column header / empty rows are not bug rows; real entries use markdown links.
            bug_rows = [
                i
                for i in pipe_indices
                if not is_separator_table_line(body[i]) and "](" in body[i]
            ]
            if bug_rows:
                insert_after_in_body = bug_rows[-1]
            else:
                insert_after_in_body = pipe_indices[-1]

        if insert_after_in_body < 0:
            new_body = table_block + body
        else:
            ins = insert_after_in_body + 1
            new_body = body[:ins] + [new_row] + body[ins:]

        lines = head + new_body + tail

    with open(registry_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
