---
description: "Recompute aggregated statuses across the backlog (also promotes the current Feature when invoked by a hook)"
---

# Update Backlog Statuses

## Goal

- Run `update_backlog_status.py` so Epic/Milestone statuses and the Project Dashboard match Feature-level source of truth and config roll-up rules.
- When hook context supplies an event, promote the targeted Feature first (per `events[]` mapping), then aggregate; otherwise support manual path/flags and aggregation-only runs.

## User Input

```text
$ARGUMENTS
```

When `$ARGUMENTS` is non-empty, parse it for an optional backlog path and script flags (see **Invoke the script**). When invoked by a hook, `$ARGUMENTS` is typically empty — use the **event name** from hook context (e.g. `after_specify`), not typed user text. In all cases, resolve the backlog path and behavior per **Prerequisites** below.

## Prerequisites

1. **Configuration**: `.specify/extensions/backlog/backlog-config.yml` when present; values are merged over the packaged `config-template.yml` in the same directory (the script’s default catalogs and events come from that merge — there are no separate hard-coded defaults). The script consumes:
   - `file_pattern` — glob matched under each directory in `backlog_roots` (see below).
   - `backlog_roots[]` — ordered repo-relative directories scanned for auto-discovery; use the **exact** order from the loaded YAML (do not assume a fixed root order from this document).
   - `levels.milestones` / `levels.epics` — disabled levels are skipped during roll-up.
   - `feature_statuses[]` — allowed Feature statuses (id / display / aggregate). Drives Feature dashboard rendering.
   - `parent_statuses[]` — allowed Epic / Milestone statuses. Drives parent dashboard rendering and is the catalog the aggregator picks parent statuses from.
   - `priorities[]` — allowed Priority values (id / display). Drives Priority dashboard rendering.
   - `events[]` — event → Feature status promotion mapping.
2. **Python**: Python 3.8+ available on `PATH` (`python3 --version`).
3. **Backlog path**:
   - If `$ARGUMENTS` provides a path, use it.
   - Otherwise let the script auto-discover: for each root in `backlog_roots` (in order), glob `<root>/<file_pattern>`; use the **first** root that yields **exactly one** match. If a root contains **two or more** matches, the script exits with an error listing them — pass an explicit backlog path or narrow `file_pattern`.

## Hooks

**Registration (two layers):**

1. **Project hook registry** — `.specify/extensions.yml` at the repository root lists, per lifecycle event, which extension command to run (e.g. `after_specify`, `after_clarify`, …).
2. **Backlog extension** — `extension.yml` in the installed backlog pack (`.specify/extensions/backlog/extension.yml`) wires those same event names to **`/speckit.backlog.update`**. Both must be present for a hook to reach this command.

**Invocation behavior:**

- Hook runs **do not** carry free-form user arguments; the executor supplies the **event name** in context (e.g. `after_specify`). The agent must pass `--event <name>` to `update_backlog_status.py`.
- Optional hooks may prompt before running; mandatory hooks run immediately (see each hook’s `optional` flag in the backlog `extension.yml`).

## Execution Steps

### Determine the event (when invoked as a hook)

When this command runs **because a hook fired**, read the **event name** from the hook context and pass `--event <name>` to the script. **Do not** assume a fixed status or branch-write behavior from this document — read the `events` map from the same YAML as above. For each hook name, the script applies that entry’s `set_status`, `set_branch`, and `enabled` exactly as configured (missing or `enabled: false` → no promotion for that event, aggregation still runs).

Typical **hook names** wired in `extension.yml` (your `events` block may define others): `after_specify`, `after_clarify`, `after_plan`, `after_tasks`, `after_analyze`, `after_implement`.

If there is **no** hook context and the user did not pass `--event`, skip promotion and run aggregation only (unless the user explicitly passed `--event` on the command line).

### Identify the target Feature (when promoting)

A promotion needs to know **which** Feature to update. Pick the most specific signal available:

1. **Explicit `--feature <id>`** — pass the ID directly when you can derive it from context (e.g. `backlog_feature_id` in the new feature spec’s frontmatter, issue title, or prior step output).
2. **`--branch <name>`** — match against existing `**Branch**:` field. Used for any event after `after_specify`, because the field was populated by `after_specify`.
3. **Current git branch** — automatic fallback when neither flag is given. The script runs `git rev-parse --abbrev-ref HEAD` and matches that against `**Branch**:` fields.

**Special case: `after_specify`.** This hook is what **creates** the branch ↔ feature link, so the Feature's `**Branch**:` field is still empty and current-branch matching cannot identify it. Before invoking the script you **must** resolve the Feature ID and pass `--feature <id>`. Resolution order:

1. Read the new feature spec at `specs/<branch-name>/spec.md` — if frontmatter contains `backlog_feature_id` (or similar), use it.
2. Otherwise, read the backlog file and match the feature **Title** against the spec’s feature title (case-insensitive, whitespace-tolerant).
3. If you still cannot identify the feature unambiguously, skip the `--event` and run the script in aggregation-only mode; report the missed promotion to the user so they can run it manually.

### Invoke the script

```bash
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py [PATH] [OPTIONS]
```

Common invocations:

```bash
# Manual aggregation only
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py

# Hook: after_specify (caller resolves the feature ID from spec context)
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py \
    --event after_specify --feature 1.2.3 --json

# Hook: after_implement (branch field was set during after_specify; auto-lookup works)
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py \
    --event after_implement --json

# Ad-hoc status override (bypasses event mapping)
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py \
    --status "Blocked" --feature 1.2.3
```

Always pass `--json` when invoked from a hook so the hook executor can parse the result. For manual-only aggregation with no hook, `--json` is optional unless the user asks for JSON.

The script exits non-zero if no backlog file is found or the file cannot be parsed — surface the error to the user verbatim.

## Aggregation rules

Roll-up uses each child status's `aggregate` role and picks the resulting parent status from `parent_statuses`. Applied at every enabled parent level:

- **`final_done` aggregate** — all children are terminal success or cancelled, with at least one success; parent status id is the `parent_statuses` entry whose `aggregate` is `final_done`.
- **`final_cancelled` aggregate** — all children cancelled; parent id from the `final_cancelled` catalog entry.
- **`blocked` aggregate** — all children blocked; parent id from the `blocked` entry.
- **`in_progress` aggregate** — mixed active work; parent id from the `in_progress` entry.
- **`initial` aggregate** — nothing has started; parent id from the `initial` entry.

Catalogs used per level — Features are always the leaves:

- **Feature → Epic** (when epics enabled): child roles read from `feature_statuses`; new Epic status picked from `parent_statuses`.
- **Feature → Milestone** (when epics disabled, milestones enabled): child roles read from `feature_statuses`; new Milestone status picked from `parent_statuses`.
- **Epic → Milestone** (when both enabled): child roles read from `parent_statuses`; new Milestone status picked from `parent_statuses`.

When both levels are disabled, no aggregation runs; the script only mirrors Feature statuses and priorities into the flat dashboard table.

Feature statuses are the source of truth: every parent status is derived; never the other way around. Priorities are user-set and never aggregated — the script only mirrors each item's source-of-truth Priority into the dashboard.

## Output

Human-readable (default) — example only; real paths and status **id** strings come from the run (discovered backlog path, configured catalogs, and `events` mapping):

```
Backlog statuses updated in <discovered-backlog-path>
  Feature 1.2.3 -> <promoted-status-id> (branch=<git-branch>)
  Parent statuses changed: Epic 1.2, Milestone 1: MVP
```

Machine-readable (`--json`) — shape is stable; replace placeholder strings with actual values from the script output:

```json
{
  "backlog_file": "<discovered-backlog-path>",
  "milestones": 3,
  "epics": 12,
  "features": 47,
  "promoted": {
    "feature_id": "1.2.3",
    "feature_title": "Payment retry",
    "status": "<feature-status-id-after-promotion>",
    "branch": "<git-branch-or-null>"
  },
  "changed": ["Epic 1.2", "Milestone 1: MVP"],
  "config_file": "<path-to-yaml-the-script-loaded>"
}
```

When no promotion is requested or the feature could not be identified, `promoted` is `null`.

## Graceful Degradation

- **No backlog file**: script exits with non-zero status and a clear error. Surface and stop.
- **Multiple backlog files** under the same `backlog_roots` entry matching `file_pattern`: script exits non-zero and lists the paths; pass an explicit backlog path or narrow `file_pattern`.
- **Configuration**: the script merges the project's `backlog-config.yml` (when found) over the packaged `config-template.yml` beside `update_backlog_status.py`. If that template is missing, or the merged result is invalid (e.g. empty catalogs), the script reports an error and exits.
- **Python missing**: report `[backlog] Python 3 not found; skipped status update` and continue without failing the calling workflow.
- **Event unknown or `enabled: false`**: aggregation still runs; the promotion is silently skipped with a warning on stderr.
- **Feature not found**: a warning is printed and aggregation still runs.
- **Status not in catalog**: the status is written anyway and a warning is emitted; users may extend `feature_statuses` / `parent_statuses` in config to legitimize custom values.

## General guidelines

- This command is **idempotent for aggregation** — running it multiple times with the same Feature statuses produces the same parent statuses and dashboard.
- This command is **single-write for promotion** — repeating an `--event` call applies the same promotion redundantly; that is safe but logs a redundant change.
- Do not manually edit the Project Dashboard tables; the script owns that presentation layer.
- Do not create or switch git branches.
