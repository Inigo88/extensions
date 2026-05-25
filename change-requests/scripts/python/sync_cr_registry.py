#!/usr/bin/env python3
"""Scan change request Markdown files and append missing rows to the aggregate registry.

Also refreshes the summary line counts from table contents.

Usage:
  python3 sync_cr_registry.py <extension_root> <repo_root>
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Import path resolution from sibling module when run as script
_CR_ID_FILE = re.compile(r"^CR(\d{3})-.+\.md$", re.IGNORECASE)
_CR_ID_LINK = re.compile(r"\[CR(\d{3})\]", re.IGNORECASE)
_TITLE_LINE = re.compile(r"^#\s+Change\s+request\s+CR\d{3}:\s*(.+)\s*$", re.IGNORECASE)


def _run_paths_py(ext: Path, repo: Path) -> tuple[Path, Path]:
    paths_py = ext / "scripts/python/change_requests_paths.py"
    out = subprocess.run(
        [sys.executable, str(paths_py), str(ext), str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    if len(lines) < 2:
        raise RuntimeError("change_requests_paths.py must print two lines")
    return Path(lines[0]), Path(lines[1])


def _ids_in_registry(text: str) -> set[str]:
    found: set[str] = set()
    for m in _CR_ID_LINK.finditer(text):
        found.add(f"CR{m.group(1)}")
    return found


def _default_title_from_filename(name: str) -> str:
    base = Path(name).stem
    m = re.match(r"^CR\d{3}-(.+)$", base, re.IGNORECASE)
    if m:
        slug = m.group(1)
        return slug.replace("-", " ").title() if slug else base
    return base.replace("-", " ").title()


def _title_from_file(path: Path) -> str:
    try:
        first = path.read_text(encoding="utf-8").splitlines()[:5]
    except OSError:
        return _default_title_from_filename(path.name)
    for line in first:
        m = _TITLE_LINE.match(line.strip())
        if m:
            return m.group(1).strip()
    return _default_title_from_filename(path.name)


def _feature_id_for(rel: Path) -> str:
    parts = rel.parts
    if len(parts) >= 2:
        return parts[0]
    return "000-general"


def _recompute_header(body: str) -> str:
    rows = [ln for ln in body.splitlines() if "|" in ln and "](" in ln and "CR" in ln]
    total = len(rows)
    completed = sum(1 for ln in rows if "✅" in ln)
    approved_or_progress = sum(1 for ln in rows if "🟡" in ln)
    draft = sum(1 for ln in rows if "🔴" in ln)
    summary = (
        f"> **{total} total** · ✅ {completed} completed · "
        f"🔴 {draft} draft / in flight · 🟡 {approved_or_progress} approved or in progress\n"
    )
    lines = body.splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.strip().startswith("> **") and "total**" in line:
            out.append(summary.rstrip("\n"))
            replaced = True
        else:
            out.append(line)
    if not replaced and lines:
        # Insert after first heading line
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = i + 1
                while insert_at < len(lines) and lines[insert_at].strip() == "":
                    insert_at += 1
                break
        lines = lines[:insert_at] + [summary.rstrip("\n"), ""] + lines[insert_at:]
        out = lines
    return "\n".join(out) + ("\n" if body.endswith("\n") else "")


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: sync_cr_registry.py <extension_root> <repo_root>", file=sys.stderr)
        sys.exit(2)
    ext = Path(sys.argv[1]).resolve()
    repo = Path(sys.argv[2]).resolve()
    data_dir, registry_path = _run_paths_py(ext, repo)

    if not registry_path.is_file():
        tpl = ext / "templates/change-request-registry-template.md"
        if tpl.is_file():
            registry_path.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Initialized registry from template: {registry_path}")
        else:
            print(f"Error: registry missing and no template at {tpl}", file=sys.stderr)
            sys.exit(1)

    reg_text = registry_path.read_text(encoding="utf-8")
    registered = _ids_in_registry(reg_text)

    cr_files: list[tuple[str, Path, str]] = []
    for path in sorted(data_dir.rglob("*.md")):
        if path.name == registry_path.name:
            continue
        m = _CR_ID_FILE.match(path.name)
        if not m:
            continue
        cr_id = f"CR{m.group(1)}"
        rel = path.relative_to(data_dir).as_posix()
        cr_files.append((cr_id, path, rel))

    update_py = ext / "scripts/python/update_cr_registry.py"
    format_title_py = ext / "scripts/python/format_feature_title.py"

    added = 0
    for cr_id, path, rel in cr_files:
        if cr_id in registered:
            continue
        title = _title_from_file(path)
        feature_id = _feature_id_for(Path(rel))
        feat_title = subprocess.run(
            [sys.executable, str(format_title_py), feature_id],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            [
                sys.executable,
                str(update_py),
                str(registry_path),
                feature_id,
                cr_id,
                rel,
                title,
                feat_title,
            ],
            check=True,
        )
        registered.add(cr_id)
        added += 1
        print(f"Registered {cr_id}: {rel}")

    if added:
        reg_text = registry_path.read_text(encoding="utf-8")
    new_text = _recompute_header(reg_text)
    if new_text != reg_text:
        registry_path.write_text(new_text, encoding="utf-8")
        print("Refreshed registry header counts.")

    if added == 0:
        print("No missing change requests to register.")
    else:
        print(f"Done. Added {added} row(s).")


if __name__ == "__main__":
    main()
