#!/usr/bin/env python3
"""Print absolute paths and status markers from extension YAML.

Reads ``bugs-config.yml`` or ``config-template.yml`` in the extension root
(``paths.data_dir``, ``paths.registry_filename``, ``status.*``). Used by
create-bug scripts so defaults stay aligned with the YAML (not duplicated in
shell).

Usage:
  python3 bugs_paths.py <extension_root> <repo_root>

Stdout: six lines — data directory path, registry file path, then status
markers in order: open, investigating, fix_proposed, resolved.
"""
from __future__ import annotations

import sys
from pathlib import Path

DEFAULT_STATUS: dict[str, str] = {
    "open": "🔴",
    "investigating": "🟡",
    "fix_proposed": "🟡",
    "resolved": "✅",
}


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
    return (data_dir or ".project/bugs"), (registry or "bug-report.md")


def _parse_status_block(text: str) -> dict[str, str]:
    """Return status key -> marker from YAML ``status:`` block (subset parser)."""
    out: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = _strip_comment(lines[i])
        if not line.strip():
            i += 1
            continue
        st = line.strip()
        if st == "status:" or st.startswith("status:"):
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
                for key in ("open", "investigating", "fix_proposed", "resolved"):
                    if s2.startswith(f"{key}:"):
                        out[key] = _scalar(s2.split(":", 1)[1])
                        break
                i += 1
            break
        i += 1
    return out


def _read_config_text(extension_root: Path) -> str | None:
    for name in ("bugs-config.yml", "config-template.yml"):
        p = extension_root / name
        if p.is_file():
            return p.read_text(encoding="utf-8")
    return None


def load_config(extension_root: Path) -> tuple[tuple[str, str], dict[str, str]]:
    """Paths (relative dir, registry filename) and merged status markers."""
    text = _read_config_text(extension_root)
    if not text:
        rel: tuple[str, str] = (".project/bugs", "bug-report.md")
        return rel, dict(DEFAULT_STATUS)
    rel_dir, reg_name = _parse_paths_block(text)
    merged = dict(DEFAULT_STATUS)
    merged.update(_parse_status_block(text))
    return (rel_dir, reg_name), merged


def resolve_paths(extension_root: Path, repo_root: Path) -> tuple[Path, Path]:
    (rel_dir, reg_name), _ = load_config(extension_root)
    data_root = (repo_root / rel_dir).resolve()
    return data_root, (data_root / reg_name).resolve()


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: bugs_paths.py <extension_root> <repo_root>", file=sys.stderr)
        sys.exit(2)
    ext = Path(sys.argv[1]).resolve()
    repo = Path(sys.argv[2]).resolve()
    _, status = load_config(ext)
    d, r = resolve_paths(ext, repo)
    print(d)
    print(r)
    for key in ("open", "investigating", "fix_proposed", "resolved"):
        print(status.get(key, DEFAULT_STATUS[key]))


if __name__ == "__main__":
    main()
