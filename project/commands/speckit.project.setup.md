---
description: "Create .project/ at repo root with assets, backlog, context, documents, crs, and bugs subfolders"
---

# Project setup (`.project/` layout)

## Goal

Create a standard **`.project/`** directory at the **repository root** with these subfolders:

| Subfolder | Intended use |
| --------- | ------------ |
| `assets/` | Attachments, exports, images, and other binaries referenced from project docs |
| `backlog/` | Backlog or planning Markdown when you keep it under `.project/` |
| `context/` | Agent-oriented product context (e.g. PRD, tech stack, design) — default target for `speckit.context.*` |
| `documents/` | Broader project documentation outside `context/` |
| `crs/` | Change requests (CRS) or similar change-tracking notes |
| `bugs/` | Bug reports, repro steps, triage notes |

The operation is **idempotent**: re-runs only create **missing** directories and **missing** `.gitkeep` files. **Do not** delete, move, or overwrite existing files in `.project/`.

## User Input

```text
$ARGUMENTS
```

Treat the user’s message in this conversation as input even when `$ARGUMENTS` is empty. Optional: `root:` followed by a repo-relative directory to use instead of the detected repo root (monorepo / nested use).

## Prerequisites

1. **Repository root** — Prefer `git rev-parse --show-toplevel` when inside a Git work tree; otherwise use the **workspace / project root** the user is working in.
2. **Apply `root:`** — If `$ARGUMENTS` (or the user message) contains `root:` / `path:` with a single repo-relative path, resolve **REPO_ROOT** to that directory (must exist and be a directory). All `.project/` paths are relative to **REPO_ROOT**.

## Execution

From **REPO_ROOT**, run the bundled script (preferred):

- **Bash**: `.specify/extensions/project/scripts/bash/project-setup.sh` with **REPO_ROOT** as the first argument (use `.` when **REPO_ROOT** is already the shell cwd).
- **PowerShell**: `.specify/extensions/project/scripts/powershell/project-setup.ps1` with `-Root` set to **REPO_ROOT** (or `.` when already in **REPO_ROOT**).

If scripts are missing, fall back to equivalent `mkdir -p` / `New-Item` for:

`.project/assets`  
`.project/backlog`  
`.project/context`  
`.project/documents`  
`.project/crs`  
`.project/bugs`  

and create each subfolder’s `.gitkeep` **only if** that file does not already exist.

## Optional README

If **`.project/README.md`** does not exist, create it with a short explanation of the folders (use the table under **Goal**, tightened to one line per row). If it already exists, **do not** modify it.

## Output

In the assistant reply after success:

- **REPO_ROOT** path used
- List of subfolders and whether each was **created** or **already present**
- Note that `.gitkeep` files are placeholders so empty directories can be tracked in Git
- If **`.project/README.md`** was created, say so; if skipped because it existed, say so

## Constraints

- **Do not** run `git` config changes or destructive git operations as part of this command.
- **Do not** overwrite non-empty project files; this workflow only ensures directories and optional `.gitkeep` / README as specified above.
- **Do not** create commits unless the user explicitly asks.

## Graceful degradation

- If **REPO_ROOT** cannot be determined, ask the user for the directory once or use the workspace root explicitly stated by the environment.
- If script execution fails (permissions, path), surface the error and stop; do not partially delete `.project/`.
