#!/usr/bin/env python3
"""Print absolute paths for change request data dir and registry from extension YAML.

Reads ``change-requests-config.yml`` or ``config-template.yml`` in the extension root
(``paths.data_dir``, ``paths.registry_filename``). Used by create-change-request scripts.

Usage:
  python3 change_requests_paths.py <extension_root> <repo_root>

Stdout: two lines — data directory path, then full registry file path.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _strip_comment(line: str) -> str:
    out: list[str] = []
    quote: str | None = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _scalar(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _parse_paths_block(text: str) -> tuple[str, str]:
    """Return (data_dir relative, registry_filename) from YAML text."""
    data_dir: str | None = None
    registry: str | None = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = _strip_comment(lines[i])
        if not line.strip():
            i += 1
            continue
        st = line.strip()
        if st == "paths:" or st.startswith("paths:"):
            i += 1
            while i < len(lines):
                raw2 = lines[i]
                line2 = _strip_comment(raw2)
                if not line2.strip():
                    i += 1
                    continue
                ind = len(raw2) - len(raw2.lstrip(" \t"))
                if ind == 0:
                    break
                s2 = line2.strip()
                if s2.startswith("data_dir:"):
                    data_dir = _scalar(s2.split(":", 1)[1])
                elif s2.startswith("registry_filename:"):
                    registry = _scalar(s2.split(":", 1)[1])
                i += 1
            break
        i += 1
    return (data_dir or ".project/change-requests"), (registry or "change-request-report.md")


def resolve_paths(extension_root: Path, repo_root: Path) -> tuple[Path, Path]:
    rel_dir, reg_name = ".project/change-requests", "change-request-report.md"
    for name in ("change-requests-config.yml", "config-template.yml"):
        p = extension_root / name
        if p.is_file():
            rel_dir, reg_name = _parse_paths_block(p.read_text(encoding="utf-8"))
            break
    data_root = (repo_root / rel_dir).resolve()
    return data_root, (data_root / reg_name).resolve()


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: change_requests_paths.py <extension_root> <repo_root>", file=sys.stderr)
        sys.exit(2)
    ext = Path(sys.argv[1]).resolve()
    repo = Path(sys.argv[2]).resolve()
    d, r = resolve_paths(ext, repo)
    print(d)
    print(r)


if __name__ == "__main__":
    main()
