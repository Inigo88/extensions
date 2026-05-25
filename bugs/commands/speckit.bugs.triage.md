---
description: "Review open bugs, set severity and status, and keep the registry table in sync"
---

# Triage open bugs (`speckit.bugs.triage`)

## Goal

- Build a clear picture of **open** and **in-progress** bugs, prioritize work, and align each bug file with the aggregate **registry** (`bug-report.md`).
- Move items from raw **Open** toward **Investigating** or **Fix Proposed** only when evidence supports that transition.

## User input

```text
$ARGUMENTS
```

Honor optional filters from `$ARGUMENTS` (for example: feature prefix, severity, or a specific **BXXX**). If empty, triage **all** open rows in the registry.

## Prerequisites

1. **Configuration**: Read `bugs-config.yml` (installed: `.specify/extensions/bugs/bugs-config.yml`) or `config-template.yml`. Use `paths.data_dir`, `paths.registry_filename`, and `status.*` emoji markers consistently between the registry table and narrative updates.
2. **Registry**: Open `<repo-root>/<paths.data_dir>/<paths.registry_filename>` using values from the YAML you loaded (do not assume a fixed default path from this document).
3. **Bug files**: Follow relative links from the registry to individual bug Markdown files.

## Execution

### 1. Inventory

- Parse the registry header for total / resolved / open / fix-proposed counts and list every row whose **Status** column is **not** the resolved marker (`status.resolved` from config). Treat other markers (`status.open`, `status.investigating`, `status.fix_proposed`) per your YAML — do not substitute ad-hoc emojis from this document.
- Apply user filters (feature section, BXXX id, severity stated in the bug file).

### 2. Per-bug review

For each candidate bug file:

- Read **Description**, **Severity**, **Steps to Reproduce**, and any partial **Technical Root Cause** already filled in.
- If reproduction is unclear, append **Open Questions** under Description (or a short bullet list) and keep status **Open** until answered.
- If reproduction is confirmed and investigation started, update the bug file checkboxes to **Investigating** and set the registry status cell to the **`status.investigating`** marker from config.
- If root cause is known and a credible **Proposed Fix** outline exists, you may set **Fix Proposed** in the bug file and the **`status.fix_proposed`** marker in the registry **only** when that section is substantive (not vague placeholders).

### 3. Prioritize

- Produce an ordered list (e.g. P0 first, then P1) with one-line **rationale** per bug.
- Call out duplicates or bugs that should be split; if splitting, register a new bug with `/speckit.bugs.register` and link related ids in each file.

### 4. Sync and summarize

- After edits, ensure registry **Status** and **Fix** columns match each bug’s body (single source of truth is the bug file for narrative; registry is the dashboard).
- Refresh the registry **header** summary line when counts change: run `scripts/python/reconcile_registry_header.py` from this extension with arguments `<absolute-path-to-bug-report.md>` and `<extension-root>` (same markers and paths as `bugs-config.yml`; recomputes totals, resolved, open, and in-progress from all bug table rows).
- Present a concise **triage summary** to the user: counts, top priorities, and any bugs blocked on input.

## Rules

- Do not mark **Resolved** in this command; resolution belongs to `/speckit.bugs.fix`.
- Prefer updating existing tables over inventing new feature sections.
- Use absolute paths for all file reads and writes.
