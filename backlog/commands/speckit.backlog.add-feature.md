---
description: "Place a new Feature in the backlog (existing or new Epic/Milestone when enabled), update body + Project Dashboard, then refresh aggregation"
---

# Add Feature to Backlog

## Goal

- Place exactly one new Feature under the correct Milestone/Epic (per enabled levels), assign a new ID, and update both the narrative body and the Project Dashboard.
- When a parent in the **`final_done`** aggregate state (see `parent_statuses` in config) gains new work, re-open aggregation via `update_backlog_status.py` (or the documented manual fallback) so parent statuses and the dashboard stay consistent.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input alongside the title/description and placement hints: treat both as available even if `$ARGUMENTS` appears literally empty; only ask the user to repeat missing **title** or **description** if **both** are absent.

## Prerequisites

1. **Configuration**: Read `.specify/extensions/backlog/backlog-config.yml` (fall back to `config-template.yml`). Use:
   - `levels.milestones` / `levels.epics`
   - `feature_statuses[]`, `parent_statuses[]`, `priorities[]` — only `id` values on source-of-truth `**Status**:` / `**Priority**:` lines; dashboard cells use catalog `display` wrapped in backticks like `/speckit.backlog.create`.
2. **Target file**: Open the backlog Markdown (explicit path from input, else auto-discover using `file_pattern` and **`backlog_roots` order from config** — do not assume a fixed directory order from this document). If discovery would match **more than one** file in the same root, stop and ask for an explicit path (same rule as `/speckit.backlog.update`).
3. **Python**: Same as `/speckit.backlog.update` — `python3` on `PATH` for running `update_backlog_status.py` during the final aggregation step.

## Execution Steps

### Where the feature fits (do this before any edit)

Scan the backlog’s **source-of-truth** sections (Milestone → Epic → Feature, or the enabled subset). Use the user’s words **and** the closest existing **titles** and **descriptions** to decide placement.

### When `milestones: true`

1. **Pick a Milestone**  
   - If the user names a milestone (number or title), use it.  
   - Otherwise choose the milestone whose stated goal/theme **best matches** this feature; if none fit well, plan a **new Milestone** (next milestone index after the highest `### Milestone N:` in the file).

2. **If `epics: true` under that milestone**  
   - Prefer an **existing Epic** whose title/description clearly covers this feature (same capability area).  
   - If no epic is a reasonable home but the milestone still fits, add a **new Epic** under that milestone: next epic id `M.E` where `M` is the milestone number and `E` is one greater than the highest existing epic segment under that milestone (e.g. epics `2.1`, `2.2` → new epic `2.3`).  
   - If the feature does not belong under any existing milestone theme, use a **new Milestone** and (when epics are on) at least **one new Epic** under it, then the new Feature as the first feature under that epic (`M.1.1` for new milestone `M`).

3. **If `epics: false` (Milestone → Feature only)**  
   - Attach the feature under the chosen milestone with the next feature id `M.n` (max existing `M.*` under that milestone + 1).  
   - If no milestone fits, create a **new Milestone** and add the feature as `M.1`.

### When `milestones: false` and `epics: true`

- Prefer an **existing top-level Epic** that matches thematically.  
- Otherwise create a **new Epic** at the top level: epic id = one greater than the highest existing top-level epic id (epics `1`, `2`, `3` → new epic `4`; first feature id `4.1`).

### When both levels are `false` (flat features)

- No Milestone or Epic: append with the next top-level feature id only (see table below).

### New parent defaults

When you create a **new Milestone** or **Epic**, set:

- **Title** and **Description** from the user input (or a concise title you confirm is acceptable).  
- **Status** / **Priority** on the new parent: use `parent_statuses` / `priorities` **ids** on source lines; pick the parent status whose `aggregate` is `"initial"` (read its `id` from config — do not assume a fixed name from this document) and default **Priority** to the `Medium` **id** only if that id exists in `priorities[]`; otherwise pick a sensible default from the loaded priority list.  
- Match **headings and nesting** to siblings in the same file (`### Milestone …`, `#### Epic …`).

For **dashboard** structure when adding parents, follow the same layout rules as `/speckit.backlog.create` (subsections, epic header rows, `| --- |` separators between epics). Re-read the live backlog’s dashboard tables and mirror column spacing and patterns.

### Hierarchy and ID assignment

Features are always present. Assign **Feature** ids from existing content **after** you know the parent epic (if any) and milestone (if any):

| `milestones` | `epics` | Parent for a new Feature | ID pattern | Next ID rule |
| :----------- | :------ | :----------------------- | :--------- | :------------ |
| `true`       | `true`  | An **Epic** under a Milestone | `M.E.F` | Under epic `M.E`, if features `M.E.1` … `M.E.k` exist, use `M.E.(k+1)`; if none, use `M.E.1`. |
| `false`      | `true`  | A **top-level Epic** | `E.F` | Under epic `E`, next free `E.n` (e.g. epic `2` → `2.3` after `2.1`, `2.2`). |
| `true`       | `false` | A **Milestone** (direct features) | `M.F` | Under milestone `M`, next free `M.n`. |
| `false`      | `false` | *(none)* — flat list | `F` | Next integer id after the highest existing top-level Feature id. |

Never reuse an existing Feature id. Do **not** renumber existing features.

### Parents that were terminal-success (re-open)

When the new feature attaches under an **Epic** and/or **Milestone** whose current `**Status**:` id matches the **`final_done`** aggregate entry in `parent_statuses`, that parent is no longer “all children finished.” You must not leave it on that terminal id while new work exists under it.

1. **Preferred**: After you add the feature (and any new parents), run `update_backlog_status.py` as in [After edits](#after-edits). Aggregation recomputes Epic and Milestone statuses from all child statuses; the parent moves to whichever **`parent_statuses`** entry matches the computed aggregate role (for example the role `in_progress`), not to a hard-coded label from this document.

2. **If Python cannot run**: In the **source-of-truth** blocks only, set each affected Epic/Milestone `**Status**:` line to the `parent_statuses` **id** whose `aggregate` is `in_progress`. Do not hand-edit Project Dashboard cells; tell the user to run the script as soon as `python3` is available so the dashboard matches the body.

If you add a **new** Epic or Milestone, set its initial status from `parent_statuses` as in [New parent defaults](#new-parent-defaults); only adjust existing **terminal-success** parents as above.

### Source-of-truth block (body)

Insert or extend the **source-of-truth** region of the file: the `### Milestone …` / `#### Epic …` / Feature bullet area **below** the horizontal rule that ends `### Project Dashboard`. Do not add Feature bullets inside the dashboard tables.

**Order of insertion** when a new parent is required:

1. **New Milestone** (when `milestones: true`): insert `### Milestone N: …` with **Description**, **Status**, **Priority** (ids), then (if `epics: true`) a new `#### Epic N.1: …` block with the same fields, then the new Feature bullet `N.1.1`. If `epics: false`, add only the milestone and the first Feature `N.1` under it.  
2. **New Epic only** (milestone already exists, `epics: true`): insert `#### Epic M.E: …` after the last epic under that milestone (or after milestone heading if it is the first epic), then the new Feature as `M.E.1`.  
3. **Existing parent only**: insert the new Feature bullet **after** the last Feature under that Epic, or after the last direct Feature under that Milestone, or at the end of the flat list.

Feature bullet shape:

```markdown
- **Feature <id>**: <Title>
  **Description**: <Simple, direct description. Do NOT use "As a user, I want...">
  **Branch**:
  **Status**: <feature status id>
  **Priority**: <priority id>
```

Preserve indentation (spaces) consistent with sibling features in that file. **`Branch`:** must be present and empty (branch is set during specify / `after_specify`).

### Project Dashboard

Update the dashboard so it reflects **every** new or touched parent, not only the feature row.

**Feature row** (align column widths with neighboring rows):

`| <id> | <Title> | `<display for feature status>` | `<display for priority>` |`

**When you add a new Epic** (`epics: true`): add the bold epic header row (epic id with an `E` prefix, e.g. `| **E2.3** | **Title** | … |`) and a `| --- | --- | --- | --- |` separator before the next epic header (if any), matching `/speckit.backlog.create`. Place the new epic’s block (header + new feature row(s)) in the same milestone subsection as in the body.

**When you add a new Milestone** (`milestones: true`): add a new `#### Milestone N: …` dashboard subsection with milestone **Status** / **Priority** lines (using parent catalog **display** in backticks, consistent with existing milestones) and the table for that milestone, including any new epic header rows and the new feature row.

Placement reminders:

- **M + E + F**: Row order matches body: under the right milestone table, epic header, feature rows, separators.  
- **E + F**: New epic header + feature rows in the single table.  
- **M + F**: New milestone subsection + feature rows only.  
- **Flat F**: Single table; new row only.

Do **not** copy stale Status/Priority from unrelated rows; use the catalogs for **new** items’ chosen ids.

### After edits

```bash
python3 .specify/extensions/backlog/scripts/python/update_backlog_status.py [PATH_TO_BACKLOG]
```

Use the same path you edited. Omit `[PATH_TO_BACKLOG]` only when relying on auto-discovery (identical rules to `/speckit.backlog.update`).

This step is **required** when any parent was in the **`final_done`** aggregate state so Epic/Milestone statuses and the dashboard reopen correctly. If Python is missing, apply the manual parent status fix in [Parents that were terminal-success (re-open)](#parents-that-were-terminal-success-re-open), report that aggregation was skipped, and tell the user to run the command when `python3` is available.

## Output

Confirm:

- Backlog file path
- **Placement decision**: existing vs new Milestone / Epic (per enabled levels), with brief rationale
- Assigned Feature **id** (and new Epic/Milestone ids if created)
- If a parent was **terminal-success** (`final_done`) before the add: confirm it was reopened (via successful script run or manual `in_progress` id on source lines)
- Whether the status script ran successfully (or was skipped)

## Graceful Degradation

- **No backlog file found**: stop and report; do not create a new backlog (use `/speckit.backlog.create` instead).
- **Ambiguous fit** (two or more epics/milestones equally plausible): ask one clarifying question; do not guess.
- **Unknown status/priority id**: use the Feature status whose `aggregate` is `"initial"` and a sensible default from `priorities[]` (prefer the `Medium` **id** when that id exists); never invent ids that are absent from the loaded catalogs.

## General guidelines

- Do not create or switch git branches.
- Do not remove or renumber existing features.
- Keep epic/milestone **header rows** and `---` separators in the dashboard structurally valid Markdown tables (same column count as adjacent rows).
