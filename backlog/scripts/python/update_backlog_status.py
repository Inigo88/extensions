#!/usr/bin/env python3
"""Update Backlog Statuses.

Two modes of operation:

1. **Aggregation only** (default):
   - Walks the source-of-truth Feature sections.
   - Recomputes Epic and Milestone statuses from configured aggregation rules
     (only at levels that are enabled in config).
   - Mirrors Status and Priority into the Project Dashboard tables.

2. **Event-driven promotion** (`--event <name>` or `--status <value>`):
   - Identifies a target Feature (by --feature / --branch / current git branch).
   - Promotes that Feature's `**Status**:` field to the event-mapped status.
   - Optionally also writes the `**Branch**:` field (used by `after_specify`).
   - Then runs aggregation.

The script supports all four hierarchy combinations:

    milestones=true,  epics=true   -> Milestone > Epic > Feature   (IDs: M.E.F)
    milestones=false, epics=true   -> Epic > Feature               (IDs: E.F)
    milestones=true,  epics=false  -> Milestone > Feature          (IDs: M.F)
    milestones=false, epics=false  -> Flat list of Features        (IDs: F)

Usage:
    update_backlog_status.py [PATH] [OPTIONS]

Examples:
    update_backlog_status.py
    update_backlog_status.py .project/backlog/my-product-backlog.md
    update_backlog_status.py --event after_specify --feature 1.1.2
    update_backlog_status.py --event after_implement
    update_backlog_status.py --status Done --feature 1.2.1 --json

Exits non-zero if the backlog file cannot be located or parsed, if more than one
file matches auto-discovery under a single ``backlog_roots`` entry, or if
configuration cannot be built from the packaged ``config-template.yml``.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Packaged defaults — single source of truth is ``config-template.yml`` in the
# extension root (same directory as ``backlog-config.yml``). Merged with any
# loaded user YAML before normalization.
# ---------------------------------------------------------------------------

DEFAULT_FILE_PATTERN = "*-backlog.md"
DEFAULT_BACKLOG_ROOTS = [".project/backlog", ".specify/backlog"]
DEFAULT_LEVELS = {"milestones": True, "epics": True}


class AmbiguousBacklogError(ValueError):
    """More than one backlog file matched discovery under the same root."""


def _extension_root():
    return Path(__file__).resolve().parent.parent.parent


def _packaged_template_dict():
    """Parse ``config-template.yml`` next to this script's extension root."""
    path = _extension_root() / "config-template.yml"
    if not path.is_file():
        return None
    try:
        data = parse_yaml(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception as exc:
        print(f"[backlog] Warning: could not parse {path}: {exc}", file=sys.stderr)
        return None


def _merge_user_config_over_template(user):
    """Overlay ``user`` keys on the packaged template (list keys replaced wholesale)."""
    base = _packaged_template_dict()
    if base is None:
        raise FileNotFoundError(
            "Packaged config-template.yml is missing or unreadable next to "
            "update_backlog_status.py; reinstall the backlog extension."
        )
    merged = dict(base)
    user = user if isinstance(user, dict) else {}
    for key, val in user.items():
        if key == "levels" and isinstance(val, dict):
            merged["levels"] = {**dict(merged.get("levels") or {}), **val}
        else:
            merged[key] = val
    return merged


# ---------------------------------------------------------------------------
# Minimal YAML reader.
# Supports the limited subset used by backlog-config.yml:
#   - top-level scalar key: value
#   - one-level nested map
#   - list of inline-or-block maps under a key
#   - quoted/unquoted scalars, booleans, simple inline lists [a, b, c]
#   - line comments (# ...)
# Not a general YAML parser.
# ---------------------------------------------------------------------------

_SCALAR_TRUE = {"true", "yes", "on"}
_SCALAR_FALSE = {"false", "no", "off"}


def _strip_comment(line):
    out = []
    quote = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
                out.append(ch)
            elif ch == "#":
                break
            else:
                out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(raw):
    s = raw.strip()
    if not s:
        return ""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    low = s.lower()
    if low in _SCALAR_TRUE:
        return True
    if low in _SCALAR_FALSE:
        return False
    if low in ("null", "~"):
        return None
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def _parse_inline_list(raw):
    s = raw.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    body = s[1:-1].strip()
    if not body:
        return []
    parts, buf, quote = [], [], None
    for ch in body:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch == ",":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [_parse_scalar(p) for p in parts]


def _parse_inline_map(raw):
    s = raw.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    body = s[1:-1].strip()
    if not body:
        return {}
    items, buf, quote, depth = [], [], None, 0
    for ch in body:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        items.append("".join(buf))
    out = {}
    for item in items:
        if ":" not in item:
            continue
        k, _, v = item.partition(":")
        out[k.strip()] = _parse_value(v)
    return out


def _parse_value(raw):
    s = raw.strip()
    if s.startswith("["):
        lst = _parse_inline_list(s)
        if lst is not None:
            return lst
    if s.startswith("{"):
        mp = _parse_inline_map(s)
        if mp is not None:
            return mp
    return _parse_scalar(s)


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


class _Frame:
    __slots__ = ("indent", "container", "pending_key")

    def __init__(self, indent, container):
        self.indent = indent
        self.container = container
        self.pending_key = None


def parse_yaml(text):
    """Parse the subset of YAML used by backlog-config.yml. Returns a dict."""
    root = {}
    stack = [_Frame(-1, root)]

    for raw in text.splitlines():
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue

        indent = _indent_of(stripped)
        content = stripped[indent:]

        while len(stack) > 1 and stack[-1].indent > indent:
            stack.pop()

        frame = stack[-1]

        if content.startswith("- "):
            item_body = content[2:].lstrip()

            if isinstance(frame.container, dict) and frame.pending_key is not None:
                key = frame.pending_key
                frame.container[key] = []
                stack.append(_Frame(indent, frame.container[key]))
                frame.pending_key = None
                frame = stack[-1]

            if not isinstance(frame.container, list):
                continue

            if item_body.startswith("{"):
                parsed = _parse_inline_map(item_body)
                frame.container.append(parsed if parsed is not None else item_body)
                continue
            if ":" in item_body:
                key, _, val = item_body.partition(":")
                key = key.strip()
                val = val.strip()
                item_map = {}
                frame.container.append(item_map)
                item_frame = _Frame(indent + 2, item_map)
                stack.append(item_frame)
                if val:
                    item_map[key] = _parse_value(val)
                else:
                    item_frame.pending_key = key
            else:
                frame.container.append(_parse_scalar(item_body))
            continue

        if ":" in content:
            key, _, val = content.partition(":")
            key = key.strip()
            val = val.strip()

            if isinstance(frame.container, dict) and frame.pending_key is not None:
                pk = frame.pending_key
                new_dict = {}
                frame.container[pk] = new_dict
                stack.append(_Frame(indent, new_dict))
                frame.pending_key = None
                frame = stack[-1]

            if isinstance(frame.container, dict):
                if val:
                    frame.container[key] = _parse_value(val)
                    frame.pending_key = None
                else:
                    frame.container[key] = None
                    frame.pending_key = key
            continue

    return root


# ---------------------------------------------------------------------------
# Configuration loading.
# ---------------------------------------------------------------------------

def _candidate_config_paths():
    here = Path(__file__).resolve()
    return [
        Path.cwd() / ".specify" / "extensions" / "backlog" / "backlog-config.yml",
        Path.cwd() / ".specify" / "extensions" / "backlog" / "config-template.yml",
        here.parent.parent.parent / "backlog-config.yml",
        here.parent.parent.parent / "config-template.yml",
    ]


def load_config(explicit_path=None):
    paths = [Path(explicit_path)] if explicit_path else _candidate_config_paths()
    raw_user = {}
    chosen = None
    for p in paths:
        if p and p.is_file():
            try:
                raw_user = parse_yaml(p.read_text(encoding="utf-8"))
                if not isinstance(raw_user, dict):
                    raw_user = {}
                chosen = p
                break
            except Exception as exc:
                print(f"[backlog] Warning: could not parse {p}: {exc}", file=sys.stderr)
                continue
    try:
        merged = _merge_user_config_over_template(raw_user)
    except FileNotFoundError as exc:
        print(f"[backlog] Error: {exc}", file=sys.stderr)
        return None, chosen
    try:
        return _normalize_config(merged), chosen
    except ValueError as exc:
        print(f"[backlog] Error: {exc}", file=sys.stderr)
        return None, chosen


def _normalize_status_list(raw):
    out = []
    if not isinstance(raw, list):
        return out
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id", "")
        if not sid:
            continue
        out.append({
            "id": sid,
            "display": entry.get("display", sid),
            "aggregate": entry.get("aggregate", "in_progress"),
        })
    return out


def _normalize_priority_list(raw):
    out = []
    if not isinstance(raw, list):
        return out
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        pid = entry.get("id", "")
        if not pid:
            continue
        out.append({"id": pid, "display": entry.get("display", pid)})
    return out


def _normalize_backlog_roots(raw):
    """Ordered roots scanned for file_pattern; first root with ≥1 match wins."""
    if not isinstance(raw, list) or not raw:
        return list(DEFAULT_BACKLOG_ROOTS)
    out = []
    for x in raw:
        if isinstance(x, str) and x.strip():
            out.append(x.strip())
    return out if out else list(DEFAULT_BACKLOG_ROOTS)


def _normalize_config(data):
    cfg = {
        "file_pattern": data.get("file_pattern", DEFAULT_FILE_PATTERN) or DEFAULT_FILE_PATTERN,
        "backlog_roots": _normalize_backlog_roots(data.get("backlog_roots")),
        "levels": dict(DEFAULT_LEVELS),
        "feature_statuses": [],
        "parent_statuses": [],
        "priorities": [],
        "events": {},
    }
    if isinstance(data.get("levels"), dict):
        for k, v in data["levels"].items():
            cfg["levels"][k] = bool(v)

    cfg["feature_statuses"] = _normalize_status_list(data.get("feature_statuses"))
    cfg["parent_statuses"] = _normalize_status_list(data.get("parent_statuses"))
    cfg["priorities"] = _normalize_priority_list(data.get("priorities"))

    if not cfg["feature_statuses"]:
        raise ValueError("feature_statuses is empty after loading config; fix backlog-config.yml or config-template.yml.")
    if not cfg["parent_statuses"]:
        raise ValueError("parent_statuses is empty after loading config; fix backlog-config.yml or config-template.yml.")
    if not cfg["priorities"]:
        raise ValueError("priorities is empty after loading config; fix backlog-config.yml or config-template.yml.")

    events = data.get("events")
    if isinstance(events, dict) and events:
        for name, spec in events.items():
            if not isinstance(spec, dict):
                continue
            cfg["events"][name] = {
                "enabled":    bool(spec.get("enabled", True)),
                "set_status": spec.get("set_status"),
                "set_branch": bool(spec.get("set_branch", False)),
            }
    else:
        raise ValueError("events map is empty after loading config; fix backlog-config.yml or config-template.yml.")

    return cfg


# ---------------------------------------------------------------------------
# Backlog file discovery and Git helpers.
# ---------------------------------------------------------------------------

def find_backlog_file(pattern, roots):
    """Return the sole path matching ``pattern`` under the first root (in order) that has matches.

    Raises ``AmbiguousBacklogError`` if more than one file matches in that root
    (pass an explicit backlog path to disambiguate).
    """
    for base_rel in roots:
        base = Path(base_rel)
        if not base.is_dir():
            continue
        matches = sorted(base.glob(pattern))
        if not matches:
            continue
        if len(matches) > 1:
            listed = ", ".join(str(m) for m in matches)
            raise AmbiguousBacklogError(
                f"Multiple backlog files match {pattern!r} under {base_rel!r}: {listed}. "
                "Pass an explicit backlog path, narrow file_pattern, or keep only one match per root."
            )
        return matches[0]
    return None


def current_git_branch():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8", errors="replace").strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


# ---------------------------------------------------------------------------
# Aggregation logic (aggregate roles drive parent status).
# ---------------------------------------------------------------------------

def _aggregate_role(status_id, statuses_list):
    for s in statuses_list:
        if s["id"] == status_id:
            return s["aggregate"]
    return "initial"


def _resolve_status_for_role(role, statuses_list):
    for s in statuses_list:
        if s["aggregate"] == role:
            return s["id"]
    return None


def get_aggregate_status(child_status_ids, child_catalog, parent_catalog):
    """Compute the parent's status id from its children's statuses."""
    if not child_status_ids:
        return _resolve_status_for_role("initial", parent_catalog) or "Backlog"

    roles = [_aggregate_role(s, child_catalog) for s in child_status_ids]

    is_final = all(r in ("final_done", "final_cancelled") for r in roles)
    has_done = any(r == "final_done" for r in roles)
    if is_final and has_done:
        return _resolve_status_for_role("final_done", parent_catalog) or "Done"
    if all(r == "final_cancelled" for r in roles):
        return _resolve_status_for_role("final_cancelled", parent_catalog) or "Cancelled"
    if all(r == "blocked" for r in roles):
        return _resolve_status_for_role("blocked", parent_catalog) or "Blocked"
    if any(r not in ("initial", "final_cancelled", "blocked") for r in roles):
        return _resolve_status_for_role("in_progress", parent_catalog) or "In progress"
    return _resolve_status_for_role("initial", parent_catalog) or "Backlog"


def _display_for(status_id, statuses_list):
    for s in statuses_list:
        if s["id"] == status_id:
            return s["display"]
    return status_id


def _priority_display(priority_id, priorities):
    if not priority_id:
        return ""
    for p in priorities:
        if p["id"] == priority_id:
            return p["display"]
    return priority_id


def update_table_row(line, *, status=None, status_catalog=None,
                     priority=None, priority_catalog=None):
    """Replace the Status (parts[3]) and/or Priority (parts[4]) cells of a
    Project Dashboard markdown table row. Cells not provided are left alone.
    """
    parts = line.split("|")
    if len(parts) < 4:
        return line
    if status is not None and status_catalog is not None:
        disp = _display_for(status, status_catalog)
        parts[3] = f" `{disp}` "
    if priority is not None and priority_catalog is not None and len(parts) >= 5:
        # Preserve the original cell's bold-wrapping if present (Epic rows use
        # `**[Priority]**` while feature rows use `[Priority]`).
        original = parts[4]
        bold = original.strip().startswith("**") and original.strip().endswith("**")
        disp = _priority_display(priority, priority_catalog)
        if disp:
            cell = f"`{disp}`"
            parts[4] = f" **{cell}** " if bold else f" {cell} "
    return "|".join(parts)


# ---------------------------------------------------------------------------
# Backlog parsing — locates milestones, epics, features, status/priority
# lines, and dashboard rows. Supports every combination of enabled levels.
# ---------------------------------------------------------------------------

# Heading patterns. IDs are flexible (1, 1.1, 1.1.1, ...) so the same parser
# works for every hierarchy combination.
_RE_MILESTONE = re.compile(r"^### Milestone (\d+): (.*)")
_RE_EPIC = re.compile(r"^#### Epic ((?:\d+\.)*\d+): (.*)")
_RE_FEATURE = re.compile(r"^- \*\*Feature ((?:\d+\.)*\d+)\*\*: (.*)")

# Dashboard patterns.
_RE_DASH_M_HEAD = re.compile(r"^#### Milestone (\d+): (.*)$")
_RE_DASH_E_ROW = re.compile(r"^\|\s*\*\*E((?:\d+\.)*\d+)\*\*\s*\|")
_RE_DASH_F_ROW = re.compile(r"^\|\s*((?:\d+\.)*\d+)\s*\|")

# Unindented metadata lines (Milestone/Epic blocks).
_RE_STATUS_LINE = re.compile(r"^\*\*Status\*\*: (.*)")
_RE_PRIORITY_LINE = re.compile(r"^\*\*Priority\*\*: (.*)")

# Indented metadata lines (Feature blocks).
_RE_INDENT_STATUS = re.compile(r"^[ \t]+\*\*Status\*\*:[ \t]*(.*)")
_RE_INDENT_BRANCH = re.compile(r"^[ \t]+\*\*Branch\*\*:[ \t]*(.*)")
_RE_INDENT_PRIORITY = re.compile(r"^[ \t]+\*\*Priority\*\*:[ \t]*(.*)")


def _new_milestone(name, mid, line_idx):
    return {
        "name": name, "id": mid, "line": line_idx,
        "status_line": -1, "priority_line": -1,
        "status": "Backlog", "priority": "",
        "epics": [], "direct_features": [],
    }


def _new_epic(name, eid, line_idx):
    return {
        "name": name, "id": eid, "line": line_idx,
        "status_line": -1, "priority_line": -1,
        "status": "Backlog", "priority": "",
        "features": [],
    }


def _new_feature(name, fid, title, line_idx):
    return {
        "name": name, "id": fid, "title": title,
        "header_line": line_idx,
        "status": "Backlog", "status_line": -1,
        "branch": "", "branch_line": -1,
        "priority": "", "priority_line": -1,
    }


def parse_backlog(lines, levels):
    """Parse the backlog file into a structured representation.

    Returns a dict with:
        milestones      : list of milestone dicts (only when levels.milestones)
        flat_epics      : list of top-level epic dicts (when milestones disabled
                          and epics enabled)
        flat_features   : list of top-level feature dicts (when both levels are
                          disabled; or features that appear outside any parent)
        dash_m_meta     : {milestone_id: {"status_line": i, "priority_line": j}}
        dash_e_rows     : {epic_id: line_idx}
        dash_f_rows     : {feature_id: line_idx}
    """
    milestones = []
    flat_epics = []
    flat_features = []

    current_m = None
    current_e = None

    dash_m_meta = {}
    dash_e_rows = {}
    dash_f_rows = {}

    in_dashboard = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if "### Project Dashboard" in line:
            in_dashboard = True
            i += 1
            continue

        # The dashboard ends as soon as we see any source-of-truth marker:
        #   - a level-3 heading other than "### Project Dashboard"
        #   - an Epic heading (level-4, "#### Epic ...")
        #   - a Feature bullet ("- **Feature ...")
        # `### ` is a prefix of `#### `, so guard against the level-4 case.
        if in_dashboard:
            is_h3 = line.startswith("### ") and not line.startswith("#### ")
            if is_h3 and "Project Dashboard" not in line:
                in_dashboard = False
            elif _RE_EPIC.match(line):
                in_dashboard = False
            elif _RE_FEATURE.match(line):
                in_dashboard = False

        if in_dashboard:
            m_dash = _RE_DASH_M_HEAD.match(line)
            if m_dash:
                mid = m_dash.group(1)
                meta = dash_m_meta.setdefault(mid, {"status_line": -1, "priority_line": -1})
                # Scan the next few lines for **Status**: and **Priority**:.
                for j in range(1, 5):
                    if i + j >= len(lines):
                        break
                    nxt = lines[i + j]
                    if nxt.startswith("#") or nxt.startswith("|"):
                        break
                    if _RE_STATUS_LINE.match(nxt) and meta["status_line"] == -1:
                        meta["status_line"] = i + j
                    if _RE_PRIORITY_LINE.match(nxt) and meta["priority_line"] == -1:
                        meta["priority_line"] = i + j

            e_dash = _RE_DASH_E_ROW.match(line)
            if e_dash:
                dash_e_rows[e_dash.group(1)] = i

            f_dash = _RE_DASH_F_ROW.match(line)
            if f_dash:
                # Skip rows that already matched as Epic rows (E-prefixed).
                if not e_dash:
                    dash_f_rows[f_dash.group(1)] = i

            i += 1
            continue

        # ---- Source-of-truth sections ----

        if levels.get("milestones", True):
            mm = _RE_MILESTONE.match(line)
            if mm:
                current_m = _new_milestone(f"Milestone {mm.group(1)}: {mm.group(2)}",
                                           mm.group(1), i)
                milestones.append(current_m)
                current_e = None
                i += 1
                continue

        if levels.get("epics", True):
            em = _RE_EPIC.match(line)
            if em:
                current_e = _new_epic(f"Epic {em.group(1)}: {em.group(2)}",
                                      em.group(1), i)
                if current_m is not None:
                    current_m["epics"].append(current_e)
                else:
                    flat_epics.append(current_e)
                i += 1
                continue

        fm = _RE_FEATURE.match(line)
        if fm:
            feature = _new_feature(f"Feature {fm.group(1)}",
                                   fm.group(1), fm.group(2).strip(), i)
            if current_e is not None:
                current_e["features"].append(feature)
            elif current_m is not None:
                current_m["direct_features"].append(feature)
            else:
                flat_features.append(feature)

            # Scan subsequent indented lines for Status/Branch/Priority.
            # Descriptions may span many lines (e.g. structured Why/What/AC/OQ);
            # stop at the next feature, a heading, unindented content, or once
            # all three metadata lines are found (cap lines to avoid runaway scans).
            j = 1
            while i + j < len(lines) and j <= 500:
                sub = lines[i + j]
                if _RE_FEATURE.match(sub):
                    break
                if sub.startswith("#"):
                    break
                if sub.strip() and not sub[0].isspace():
                    break
                sm = _RE_INDENT_STATUS.match(sub)
                if sm:
                    feature["status"] = sm.group(1).strip() or "Backlog"
                    feature["status_line"] = i + j
                bm = _RE_INDENT_BRANCH.match(sub)
                if bm:
                    feature["branch"] = bm.group(1).strip()
                    feature["branch_line"] = i + j
                pm = _RE_INDENT_PRIORITY.match(sub)
                if pm:
                    feature["priority"] = pm.group(1).strip()
                    feature["priority_line"] = i + j
                if (
                    feature["status_line"] >= 0
                    and feature["branch_line"] >= 0
                    and feature["priority_line"] >= 0
                ):
                    break
                j += 1
            i += 1
            continue

        # ---- Unindented Status / Priority for Milestone or Epic blocks ----

        sm = _RE_STATUS_LINE.match(line)
        if sm:
            target = current_e if current_e is not None else current_m
            if target is not None and target.get("status_line", -1) == -1:
                target["status_line"] = i
                target["status"] = sm.group(1).strip() or "Backlog"

        pm = _RE_PRIORITY_LINE.match(line)
        if pm:
            target = current_e if current_e is not None else current_m
            if target is not None and target.get("priority_line", -1) == -1:
                target["priority_line"] = i
                target["priority"] = pm.group(1).strip()

        i += 1

    return {
        "milestones": milestones,
        "flat_epics": flat_epics,
        "flat_features": flat_features,
        "dash_m_meta": dash_m_meta,
        "dash_e_rows": dash_e_rows,
        "dash_f_rows": dash_f_rows,
    }


def _iter_all_features(parsed):
    for m in parsed["milestones"]:
        for e in m["epics"]:
            for f in e["features"]:
                yield f
        for f in m["direct_features"]:
            yield f
    for e in parsed["flat_epics"]:
        for f in e["features"]:
            yield f
    for f in parsed["flat_features"]:
        yield f


def _iter_all_epics(parsed):
    for m in parsed["milestones"]:
        for e in m["epics"]:
            yield e
    for e in parsed["flat_epics"]:
        yield e


def find_feature(parsed, feature_id=None, branch=None):
    features = list(_iter_all_features(parsed))
    if feature_id:
        for f in features:
            if f["id"] == feature_id:
                return f
        return None
    if branch:
        for f in features:
            if f["branch"] and f["branch"] == branch:
                return f
        return None
    return None


# ---------------------------------------------------------------------------
# Mutators (source-of-truth lines).
# ---------------------------------------------------------------------------

def write_feature_status(lines, feature, new_status):
    if feature["status_line"] == -1:
        insert_at = feature["header_line"] + 1
        indent = "    "
        next_line = lines[insert_at] if insert_at < len(lines) else ""
        m = re.match(r"^(\s+)", next_line)
        if m:
            indent = m.group(1)
        lines.insert(insert_at, f"{indent}**Status**: {new_status}\n")
        feature["status_line"] = insert_at
        if feature["branch_line"] >= insert_at:
            feature["branch_line"] += 1
        if feature["priority_line"] >= insert_at:
            feature["priority_line"] += 1
    else:
        original = lines[feature["status_line"]]
        m = re.match(r"^([ \t]*)\*\*Status\*\*:", original)
        leading = m.group(1) if m else ""
        lines[feature["status_line"]] = f"{leading}**Status**: {new_status}\n"
    feature["status"] = new_status


def write_feature_branch(lines, feature, branch):
    if feature["branch_line"] == -1:
        insert_at = (feature["status_line"] + 1) if feature["status_line"] != -1 \
                    else (feature["header_line"] + 1)
        indent = "    "
        for probe in (insert_at, feature["header_line"] + 1):
            if 0 <= probe < len(lines):
                m = re.match(r"^(\s+)", lines[probe])
                if m:
                    indent = m.group(1)
                    break
        lines.insert(insert_at, f"{indent}**Branch**: {branch}\n")
        feature["branch_line"] = insert_at
        if feature["status_line"] >= insert_at:
            feature["status_line"] += 1
        if feature["priority_line"] >= insert_at:
            feature["priority_line"] += 1
    else:
        original = lines[feature["branch_line"]]
        m = re.match(r"^([ \t]*)\*\*Branch\*\*:", original)
        leading = m.group(1) if m else ""
        lines[feature["branch_line"]] = f"{leading}**Branch**: {branch}\n"
    feature["branch"] = branch


def write_parent_status(lines, item, new_status):
    """Rewrite an unindented `**Status**: <value>` line on a milestone/epic.

    Returns True iff the line text actually changed.
    """
    if item["status_line"] == -1:
        return False
    original = lines[item["status_line"]]
    new_line = f"**Status**: {new_status}\n"
    if original == new_line:
        return False
    lines[item["status_line"]] = new_line
    return True


# ---------------------------------------------------------------------------
# Top-level update routine.
# ---------------------------------------------------------------------------

def _mirror_feature_to_dashboard(lines, feature, parsed, feature_catalog, priorities):
    fid = feature["id"]
    if fid in parsed["dash_f_rows"]:
        idx = parsed["dash_f_rows"][fid]
        lines[idx] = update_table_row(
            lines[idx],
            status=feature["status"], status_catalog=feature_catalog,
            priority=feature["priority"], priority_catalog=priorities,
        )


def _mirror_epic_to_dashboard(lines, epic, new_status, parsed, parent_catalog, priorities):
    if epic["id"] in parsed["dash_e_rows"]:
        idx = parsed["dash_e_rows"][epic["id"]]
        lines[idx] = update_table_row(
            lines[idx],
            status=new_status, status_catalog=parent_catalog,
            priority=epic["priority"], priority_catalog=priorities,
        )


def _mirror_milestone_to_dashboard(lines, milestone, new_status, parsed, parent_catalog, priorities):
    meta = parsed["dash_m_meta"].get(milestone["id"])
    if not meta:
        return
    if meta["status_line"] != -1:
        disp = _display_for(new_status, parent_catalog)
        lines[meta["status_line"]] = f"**Status**: `{disp}`\n"
    if meta["priority_line"] != -1 and milestone["priority"]:
        disp = _priority_display(milestone["priority"], priorities)
        if disp:
            lines[meta["priority_line"]] = f"**Priority**: `{disp}`\n"


def update_backlog(file_path, cfg, *, event=None, status_override=None,
                   feature_id=None, branch=None, set_branch_override=None):
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    parsed = parse_backlog(lines, cfg["levels"])
    feature_catalog = cfg["feature_statuses"]
    parent_catalog = cfg["parent_statuses"]
    priorities = cfg["priorities"]

    promoted = None
    set_branch = False
    new_status = None

    # ---- Resolve requested promotion ----
    if event:
        event_spec = cfg["events"].get(event)
        if event_spec and event_spec.get("enabled", True):
            new_status = event_spec.get("set_status")
            set_branch = bool(event_spec.get("set_branch", False))
        else:
            print(f"[backlog] Event {event!r} disabled or unknown; aggregation only",
                  file=sys.stderr)
    if status_override is not None:
        new_status = status_override
    if set_branch_override is not None:
        set_branch = bool(set_branch_override)

    # ---- Locate target feature and apply promotion ----
    if new_status:
        effective_branch = branch or current_git_branch()
        target = find_feature(parsed, feature_id=feature_id, branch=effective_branch)
        if target is None:
            print(
                f"[backlog] Warning: could not identify target Feature "
                f"(feature_id={feature_id!r}, branch={effective_branch!r}); "
                f"skipping status promotion",
                file=sys.stderr,
            )
        else:
            valid_ids = {s["id"] for s in feature_catalog}
            if new_status not in valid_ids:
                print(f"[backlog] Warning: status {new_status!r} is not in "
                      f"feature_statuses; writing anyway", file=sys.stderr)
            write_feature_status(lines, target, new_status)
            if set_branch and effective_branch:
                write_feature_branch(lines, target, effective_branch)
            promoted = {
                "feature_id": target["id"],
                "feature_title": target["title"],
                "status": new_status,
                "branch": target["branch"] if set_branch else None,
            }
            parsed = parse_backlog(lines, cfg["levels"])

    # ---- Aggregation pass ----
    changed = []
    epics_enabled = cfg["levels"].get("epics", True)
    milestones_enabled = cfg["levels"].get("milestones", True)

    def _aggregate_epic(epic):
        """Roll feature statuses up into the epic; mirror dashboard rows."""
        f_statuses = [f["status"] for f in epic["features"]]
        for f in epic["features"]:
            _mirror_feature_to_dashboard(lines, f, parsed, feature_catalog, priorities)
        new_epic = get_aggregate_status(f_statuses, feature_catalog, parent_catalog)
        if write_parent_status(lines, epic, new_epic):
            changed.append(f"Epic {epic['id']}")
        epic["status"] = new_epic
        _mirror_epic_to_dashboard(lines, epic, new_epic, parsed, parent_catalog, priorities)
        return new_epic

    # Milestones (and the levels beneath them).
    for m in parsed["milestones"]:
        child_statuses = []
        child_catalog = parent_catalog if epics_enabled else feature_catalog

        if epics_enabled:
            for e in m["epics"]:
                child_statuses.append(_aggregate_epic(e))

        for f in m["direct_features"]:
            _mirror_feature_to_dashboard(lines, f, parsed, feature_catalog, priorities)
            child_statuses.append(f["status"])

        if milestones_enabled:
            new_m = get_aggregate_status(child_statuses, child_catalog, parent_catalog)
            if write_parent_status(lines, m, new_m):
                changed.append(m["name"])
            m["status"] = new_m
            _mirror_milestone_to_dashboard(lines, m, new_m, parsed, parent_catalog, priorities)

    # Top-level epics (milestones disabled, epics enabled).
    for e in parsed["flat_epics"]:
        _aggregate_epic(e)

    # Top-level / flat features (no epic and no milestone wrapping).
    for f in parsed["flat_features"]:
        _mirror_feature_to_dashboard(lines, f, parsed, feature_catalog, priorities)

    file_path.write_text("".join(lines), encoding="utf-8")

    return {
        "backlog_file": str(file_path),
        "milestones": len(parsed["milestones"]),
        "epics": sum(len(m["epics"]) for m in parsed["milestones"]) + len(parsed["flat_epics"]),
        "features": sum(1 for _ in _iter_all_features(parsed)),
        "promoted": promoted,
        "changed": changed,
    }


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="update_backlog_status.py",
        description="Update aggregated statuses in a product backlog.",
    )
    p.add_argument("path", nargs="?", help="Path to the backlog file (default: auto-discover)")
    p.add_argument("--event", help="Hook event name (e.g. after_specify) to apply event-mapped Feature promotion")
    p.add_argument("--status", help="Explicit Feature status to set (overrides --event mapping)")
    p.add_argument("--feature", help="Feature ID to promote (e.g. 1.2.3)")
    p.add_argument("--branch", help="Branch name used for Feature lookup (default: current git branch)")
    p.add_argument("--set-branch", dest="set_branch", action="store_true",
                   help="Also write the Feature **Branch** field (default for after_specify)")
    p.add_argument("--no-set-branch", dest="set_branch", action="store_false",
                   help="Do not write the Feature **Branch** field")
    p.set_defaults(set_branch=None)
    p.add_argument("--config", help="Path to backlog-config.yml (default: auto-discover)")
    p.add_argument("--json", dest="emit_json", action="store_true", help="Emit JSON output")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    cfg, cfg_path = load_config(args.config)
    if not cfg:
        return 1

    try:
        backlog_path = Path(args.path) if args.path else find_backlog_file(
            cfg["file_pattern"], cfg["backlog_roots"]
        )
    except AmbiguousBacklogError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if not backlog_path or not Path(backlog_path).is_file():
        print(
            f"Error: Backlog file not found (pattern={cfg['file_pattern']!r}, "
            f"roots={cfg['backlog_roots']!r}, path={args.path!r})",
            file=sys.stderr,
        )
        return 1

    result = update_backlog(
        backlog_path,
        cfg,
        event=args.event,
        status_override=args.status,
        feature_id=args.feature,
        branch=args.branch,
        set_branch_override=args.set_branch,
    )
    result["config_file"] = str(cfg_path) if cfg_path else None

    if args.emit_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"Backlog statuses updated in {result['backlog_file']}")
        if result["promoted"]:
            p = result["promoted"]
            extra = f" (branch={p['branch']})" if p["branch"] else ""
            print(f"  Feature {p['feature_id']} -> {p['status']}{extra}")
        if result["changed"]:
            print(f"  Parent statuses changed: {', '.join(result['changed'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
