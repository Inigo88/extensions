# Product Backlog Extension

Create and maintain a product backlog for Spec Kit projects: a structured Markdown document of Milestones → Epics → Features whose aggregated statuses stay in sync with the active spec workflows.

## Overview

This extension provides backlog operations as an optional, self-contained module. It manages:

- **Backlog creation** from a natural-language product description (configurable hierarchy levels). Default output path is **`.project/backlog/<slug>-backlog.md`** (run **`speckit.project.setup`** first if that folder does not exist).
- **Status aggregation** that rolls Feature statuses up into Epic and Milestone statuses (only at enabled levels).
- **Project Dashboard synchronization** — the dashboard tables at the top of the backlog mirror the source-of-truth Status and Priority of every Milestone, Epic, and Feature below.
- **Hook integration** — every `/speckit.*` workflow that changes a Feature status can trigger a status recompute.

Commands and scripts assume the extension is **installed** under `.specify/extensions/backlog/` (for example after `specify extension add backlog`). Paths in command docs and hook wiring refer to that layout.

## Commands

| Command | Description |
|---------|-------------|
| `speckit.backlog.create` | Create a product backlog from a natural-language product description |
| `speckit.backlog.add-feature` | Add a Feature with placement into an existing or new Epic/Milestone (body + Project Dashboard), then refresh aggregation |
| `speckit.backlog.detail-feature` | Interactively extend one Feature’s description with **Why**, **What**, **Acceptance Criteria**, and **Open Questions** (short, backlog-level) |
| `speckit.backlog.update` | Recompute aggregated statuses across the backlog |

## Hooks

All hooks are **optional** (prompt the user before running) and trigger `speckit.backlog.update`. Each hook promotes the active Feature to a configured status before re-aggregating:

| Event | Promotes Feature to | Notes |
|-------|---------------------|-------|
| `after_specify`   | `Specified`   | Also writes the `**Branch**:` field with the current branch. The caller must pass `--feature <id>` (see below) |
| `after_clarify`   | `Clarified`   | |
| `after_plan`      | `Planned`     | |
| `after_tasks`     | `Tasked`      | |
| `after_analyze`   | `Analyzed`    | The caller (analyze workflow) must only fire this hook when analysis is clean — the extension does not inspect the analysis report itself |
| `after_implement` | `Implemented` | Terminal Feature status — Epic/Milestone roll up to `Done` once all child features are `Implemented` (or `Cancelled`, with at least one `Implemented`) |

Hooks in `extension.yml` carry no arguments — only the event name. The command file (`speckit.backlog.update.md`) tells the agent invoking it how to derive `--event <name>` from the hook context and how to identify the target Feature, in order of preference:

1. an explicit `--feature <id>` resolved from the spec context (required for `after_specify`);
2. an explicit `--branch <name>`;
3. the current git branch (`git rev-parse --abbrev-ref HEAD`), matched against existing `**Branch**:` fields.

For `after_specify`, the Branch field is still empty (it's the event that populates it), so the agent **must** resolve `--feature` from the freshly-created `specs/<branch>/spec.md` (frontmatter or title match against the backlog) before invoking the script.

## Event ↔ status mapping

Configured in `backlog-config.yml` under `events`:

```yaml
events:
  after_specify:
    enabled: true
    set_status: "Specified"
    set_branch: true
  after_implement:
    enabled: true
    set_status: "Implemented"
    set_branch: false
  # ... etc
```

Set any event's `enabled: false` (or remove the section) to keep aggregation but skip status promotion for that event.

## Configuration

Project overrides live in `.specify/extensions/backlog/backlog-config.yml`. The script builds effective configuration by **merging** that file over the packaged **`config-template.yml`** in the same directory, which is the single source of truth for default catalogs, priorities, events, and discovery settings (the Python script does not duplicate those defaults). The shipped `config-template.yml` is also a useful reference for resetting a corrupted `backlog-config.yml`. Simple top-level defaults (`file_pattern`, `levels.*`) remain declared under `config.defaults` in `extension.yml` for tooling that synthesizes a minimal file.

### Hierarchy levels

Features are **always** present. The two parent levels above them can be toggled independently:

```yaml
levels:
  milestones: true   # set false to skip Milestone headings and roll-up
  epics: true        # set false to skip Epic headings and roll-up
```

| `milestones` | `epics` | Resulting hierarchy | IDs |
| :--- | :--- | :--- | :--- |
| `true`  | `true`  | Milestone → Epic → Feature *(default)* | `M.E.F`  |
| `false` | `true`  | Epic → Feature                          | `E.F`    |
| `true`  | `false` | Milestone → Feature                     | `M.F`    |
| `false` | `false` | Flat list of Features                   | `F`      |

All four modes are supported end-to-end: the parser, the aggregator, the dashboard renderer, and the create command all adapt to the enabled levels.

### Status catalogs

Two independent catalogs are declared in config:

- **`feature_statuses`** — allowed values for a Feature's `**Status**:`. Drives the dashboard rendering of Feature rows. Contributes to parent roll-up via each entry's `aggregate` role.
- **`parent_statuses`** — allowed values for an Epic's or Milestone's `**Status**:`. The aggregator picks the parent's new status by matching the resulting roll-up role against this catalog.

Each entry has the same shape:

```yaml
feature_statuses:
  - id: "Backlog"            # canonical string written to the backlog
    display: "⚪ Backlog"     # rendered string in the dashboard (backticked by the renderer)
    aggregate: "initial"     # roll-up role contributed to the parent
  - id: "Implemented"
    display: "🟢 Implemented"
    aggregate: "final_done"
  # ...

parent_statuses:
  - id: "Backlog"
    display: "⚪ Backlog"
    aggregate: "initial"
  - id: "In progress"
    display: "🟡 In progress"
    aggregate: "in_progress"
  # ...
```

A status id MAY appear in both lists (e.g. `Backlog`, `Blocked`, `Cancelled`, `Done`) — the lists are independent and their `display` strings can diverge if you want different rendering at different levels.

| `aggregate` role | Effect on the parent (when child has this role) |
| :--- | :--- |
| `initial`         | Counted as "not started" — does not move the parent off `Backlog`. |
| `in_progress`     | Any child with this role moves the parent to the `in_progress` entry in `parent_statuses`. |
| `blocked`         | If **all** children have this role, the parent becomes the `blocked` entry in `parent_statuses`. |
| `final_cancelled` | Treated as cancelled; if **all** children are cancelled, the parent becomes the `final_cancelled` entry. |
| `final_done`      | If **all** children are `final_done` or `final_cancelled` **and** at least one is `final_done`, the parent becomes the `final_done` entry. |

The roll-up steps use the catalogs as follows (Features are always the leaves):

- **Feature → Epic** (epics enabled): child roles read from `feature_statuses`; new Epic status picked from `parent_statuses`.
- **Feature → Milestone** (epics disabled, milestones enabled): child roles read from `feature_statuses`; new Milestone status picked from `parent_statuses`.
- **Epic → Milestone** (both enabled): child roles read from `parent_statuses`; new Milestone status picked from `parent_statuses`.

You can extend either catalog with custom statuses by adding entries with an appropriate `aggregate` role.

> Features do **not** have a `Done` status. `Implemented` is the terminal Feature state; `Done` only exists in `parent_statuses` and is reached when all child features are `Implemented` or `Cancelled`, with at least one `Implemented`.

### Priority catalog

`**Priority**:` is a per-item attribute on every Milestone, Epic, and Feature. It is **not** aggregated upward — `/speckit.backlog.update` only mirrors each item's source-of-truth Priority into the Project Dashboard cells. Edit the source-of-truth `**Priority**:` line directly; the next aggregation run regenerates the dashboard.

```yaml
priorities:
  - id: "High"
    display: "High"
  - id: "Medium"
    display: "Medium"
  - id: "Low"
    display: "Low"
```

Like statuses, you can add custom priorities with their own `display` strings (plain text is fine; status rows may still use emoji in `display` if you prefer).

### File discovery

`file_pattern` and `backlog_roots` control how `/speckit.backlog.update` finds the backlog when no path is supplied:

```yaml
file_pattern: "*-backlog.md"
backlog_roots:
  - ".project/backlog"   # preferred (align with speckit.project.setup)
  - ".specify/backlog"   # legacy
```

For each root **in order**, the script globs `<root>/<file_pattern>` and uses the **first** root that contains any match. Within that root, **exactly one** file must match; if two or more files match, the script **exits with an error** listing the paths (pass an explicit backlog path, narrow `file_pattern`, or keep only one matching file per root). Roots with no matches are skipped until one yields a single file.

## Installation

```bash
# Offline: registers speckit.backlog.* commands
specify extension add backlog
```

## Disabling

```bash
# Unregisters speckit.backlog.* until you enable again
specify extension disable backlog

# Restores speckit.backlog.*
specify extension enable backlog
```

## Graceful Degradation

- If `python3` is not installed: status updates are skipped with a warning; the calling workflow continues.
- If more than one backlog file matches `file_pattern` under the same `backlog_roots` entry: `/speckit.backlog.update` exits non-zero with a clear error listing the matches.
- If no backlog file is found under any configured `backlog_roots` entry: `/speckit.backlog.update` exits non-zero with a clear error.
- If `backlog-config.yml` is missing: the script still loads defaults from the packaged `config-template.yml` (merged with an empty overlay). If that template is missing from the install, configuration fails with a clear error.
- If a hook event is unknown or `enabled: false` in config: aggregation still runs; the promotion is skipped with a warning.
- If the target Feature cannot be identified (no `--feature`, no matching `--branch`, no current git branch): the promotion is skipped with a warning; aggregation still runs.
- If a Feature carries a status that is not in the catalog: the status is written anyway and a warning naming the offending feature is emitted (so user-defined statuses don't lose data).

## Scripts

The extension currently ships a single cross-platform Python implementation (no Bash/PowerShell shims yet):

- `scripts/python/update_backlog_status.py` — Promotes the active Feature (when an event is supplied) and recomputes Epic/Milestone statuses and the Project Dashboard.

Key flags:

| Flag | Purpose |
|------|---------|
| `[PATH]`              | Explicit backlog file (default: auto-discover under `backlog_roots`, **`.project/backlog`** first) |
| `--event <name>`      | Apply the event's `set_status` / `set_branch` from config |
| `--status <value>`    | Override Feature status without using the event mapping |
| `--feature <id>`      | Identify the target Feature by ID (e.g. `1.2.3`) |
| `--branch <name>`     | Identify the target Feature by Branch field (default: current git branch) |
| `--set-branch` / `--no-set-branch` | Force-enable or force-disable Branch-field writing |
| `--config <path>`     | Path to `backlog-config.yml` (default: auto-discover) |
| `--json`              | Emit machine-readable JSON (use this from hooks) |

The script is self-contained — it ships its own minimal YAML reader and depends only on the Python stdlib.

## Tests

From the repository root:

```bash
python3 -m unittest discover -s old/backlog/tests -p 'test*.py' -v
```

## Templates

- `templates/backlog-template.md` — Markdown skeleton used by `/speckit.backlog.create`. Sections for disabled levels (and their dashboard sub-tables) are omitted from the generated output; in flat-features mode the dashboard collapses to a single Feature table.

## Extension structure

```text
backlog/
├── extension.yml           # Manifest (schema_version, extension, requires, provides, hooks, tags, config.defaults)
├── README.md
├── .gitignore
├── config-template.yml     # Default config (merged under backlog-config.yml; script source of truth)
├── backlog-config.yml      # Runtime backlog config (shipped default; customize in the project)
├── commands/
│   ├── speckit.backlog.create.md
│   ├── speckit.backlog.update.md
│   ├── speckit.backlog.add-feature.md
│   └── speckit.backlog.detail-feature.md
├── templates/
│   └── backlog-template.md
├── tests/
│   └── test_update_backlog_status.py
└── scripts/
    └── python/
        └── update_backlog_status.py
```

When you publish this extension separately, set or update **`repository`** in `extension.yml` to your canonical URL if it differs from the placeholder.
