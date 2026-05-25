#!/usr/bin/env python3
"""
Derive a registry section heading from a feature folder id (e.g. specs layout).

  019-hero-section -> 019 — Hero Section
  000-general      -> 000 — General
"""
import sys


def format_feature_title(feature_id: str) -> str:
    s = feature_id.strip()
    if len(s) > 3 and s[:3].isdigit() and "-" in s:
        prefix, rest = s.split("-", 1)
        words = rest.replace("-", " ").title()
        return f"{prefix} — {words}"
    return s.replace("-", " ").title()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: format_feature_title.py <feature-folder-id>", file=sys.stderr)
        sys.exit(1)
    print(format_feature_title(sys.argv[1]))


if __name__ == "__main__":
    main()
