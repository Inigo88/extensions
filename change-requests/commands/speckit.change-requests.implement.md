---
description: "Plan, implement, verify, and complete a change request with an optional approval gate"
---

# Implement change request (`speckit.change-requests.implement`)

## Goal

- Take a registered change request (**CRXXX**) from draft or approved through implementation to **Completed**, keeping the CR document and registry accurate.
- For non-trivial work, pause at an **approval gate** after the implementation plan before editing production code when configured.

## User input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. Expect a **CRXXX** id and/or path to a change request file; if missing, ask which item to implement.

## Prerequisites

1. **Configuration**: Read `change-requests-config.yml` or `config-template.yml` under **`.specify/extensions/change-requests/`** (when installed). Honor `features.require_implementation_approval_non_trivial` for the approval gate.
2. **Artifact**: Open the change request Markdown under **`<repo-root>/<paths.data_dir>`** from config (glob `…/CRXXX-*.md` from user input or registry link).
3. **Registry**: **`<repo-root>/<paths.data_dir>/<paths.registry_filename>`** from the same YAML.

## Execution

### 1. Analyze and scope

- Re-read **Summary**, **Rationale**, **Scope**, and current **Status** / **Priority**.
- Confirm the change request is still one coherent delivery; split only when work is clearly separable (then register follow-ups with `/speckit.change-requests.register`).
- Identify owning feature or component for regression checks.

### 2. Plan

- Complete **Implementation plan** with **Approach**, **Affected components**, and a **Detailed task list** (T001, …) at the same clarity as a feature `tasks.md`.
- Vague plans (“update the service”) are insufficient; list concrete edits per file or configuration.

### 3. Approval gate (non-trivial changes)

When `require_implementation_approval_non_trivial` is true and the change is non-trivial (multi-file, behavior change, migration, or risky ops):

- **STOP** after writing the plan and present the CR id, summary, and task list to the user.
- Do **not** implement until the user explicitly approves.
- After approval (or when the change is trivial), move status toward **Approved** or **In progress** as appropriate and sync the registry status column to **`status.approved`** or **`status.in_progress`** from config.

### 4. Implement

- Execute tasks in order; check off `[x]` in the CR document as you complete each task.
- Match project coding standards and keep the diff minimal but complete.

### 5. Verify

- Work through the **Verification** checklist (functional, regression, documentation, technical).
- Use the project’s preferred verification approach (tests, browser checks, etc.) when available.

### 6. Complete and sync

- Fill **Completion notes** with what shipped and any deviations.
- Set **Status** to **Completed**, set **Date completed**, and mark verification items complete.
- Update the registry row: status **`status.completed`** from config, add a short **Summary** column where useful, and refresh header counts (totals / completed / draft / approved) to match the table.

### 7. Optional follow-up

- If the user requested commits: use the project’s commit message convention (for example `chore(cr): complete CRXXX title`).

## Rules

- Use **absolute paths** at all times.
- Keep registry and CR document **in sync** after substantive status changes.
- Do not skip the approval gate for substantial work when `require_implementation_approval_non_trivial` is true.
