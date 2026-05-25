---
description: "Investigate, plan, implement, verify, and resolve a bug with approval gate when needed"
---

# Fix bug (`speckit.bugs.fix`)

## Goal

- Take a registered bug (**BXXX**) from investigation through implementation to **Resolved**, keeping the bug file and registry accurate.
- For non-trivial changes, pause at an **approval gate** after **Proposed Fix** before editing production code.

## User input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. Expect a **BXXX** id and/or path to a bug file; if missing, ask which open bug to fix.

## Prerequisites

1. **Configuration**: Read `bugs-config.yml` or `config-template.yml` under **`.specify/extensions/bugs/`** (when installed). Honor `features.require_fix_approval_non_trivial` for the approval gate (default comes from YAML, not this document).
2. **Bug artifact**: Open the bug Markdown under **`<repo-root>/<paths.data_dir>`** from config (glob `…/BXXX-*.md` from user input or registry link).
3. **Registry**: **`<repo-root>/<paths.data_dir>/<paths.registry_filename>`** from the same YAML.

## Execution

### 1. Analyze and scope

- Re-read **Description**, reproduction steps, and current **Status** / **Severity**.
- Confirm whether this is still a single coherent issue; split only when work is clearly separable (then register follow-ups with `/speckit.bugs.register`).
- **Categorize** the owning feature or component for regression checks later.

### 2. Investigate

- Identify **Technical Root Cause** with specific files and lines where possible.
- Update the bug file if investigation advances status from Open → **Investigating**; sync the registry status column to **`status.investigating`** from config.

### 3. Plan the fix

- Complete **Proposed Fix** with **Implementation Strategy**, **Affected Components**, and a **Detailed Task List** (T001, T002, …) similar in clarity to a feature `tasks.md`.
- Vague plans (“fix the CSS”) are insufficient; list concrete edits per file.

### 4. Approval gate (non-trivial fixes)

When `require_fix_approval_non_trivial` is true and the fix is non-trivial (multi-file, behavior change, or risky migration):

- **STOP** after writing the plan and present the bug id, summary, and task list to the user.
- Do **not** implement until the user explicitly approves.
- After approval (or when the fix is trivial and the gate does not apply), set bug status toward **Fix Proposed** if not already, and sync the registry to **`status.fix_proposed`** from config where your workflow uses that marker for proposed fixes.

### 5. Implement

- Execute tasks in order; check off `[x]` in the bug file as you complete each task.
- Match project coding standards and keep the diff minimal but complete.

### 6. Verify

- Work through the **Verification** checklist (functional, visual, accessibility, technical).
- For UI changes, use the project’s preferred verification approach (e.g. browser checks) when available.

### 7. Resolve and sync

- Fill **Resolution** with what changed and why.
- Set **Status** to **Resolved**, set **Date Resolved**, and mark verification items complete.
- Update the registry row: status **`status.resolved`** from config, add a short **Fix** column summary, and refresh header counts (totals / resolved / open / fix proposed) to match the table — for example by running `scripts/python/reconcile_registry_header.py <absolute-registry-path> <extension-root>` after updating the row.

### 8. Optional follow-up

- If the user requested commits: use the project’s commit message convention (for example `fix(scope): resolve BXXX title`).

## Rules

- Use **absolute paths** at all times.
- Keep registry and bug file **in sync**; update the registry after substantive status changes.
- Do not skip the approval gate for substantial work when `require_fix_approval_non_trivial` is true.
