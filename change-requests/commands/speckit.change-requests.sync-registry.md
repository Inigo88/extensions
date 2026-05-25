---
description: "Scan change request files on disk and register any CR ids missing from the aggregate registry"
---

# Sync change request registry (`speckit.change-requests.sync-registry`)

## Goal

- Ensure every **CR###-*.md** file under the configured data directory has a corresponding row in **`change-request-report.md`**.
- Refresh the registry **summary line** counts from the table so the dashboard matches files on disk after manual moves, restores, or partial edits.

## User input

```text
$ARGUMENTS
```

Optional: a feature folder name or **CRXXX** to limit reporting; the sync script still scans the whole tree unless you post-filter in your narrative.

## Prerequisites

1. **Configuration**: Read `change-requests-config.yml` or `config-template.yml` next to `extension.yml` (installed: `.specify/extensions/change-requests/`). Use `paths.data_dir` and `paths.registry_filename`.
2. **Python**: Same as `/speckit.change-requests.register` — **Python 3** on `PATH` (`python3`, `python`, or Windows `py -3`) for running `sync_cr_registry.py`.

## Execution

### 1. Run the sync script

From the repository root, pass **absolute paths** for the extension directory (the folder that contains `extension.yml`) and the repository root:

```bash
python3 "/absolute/path/to/change-requests/scripts/python/sync_cr_registry.py" \
  "/absolute/path/to/change-requests" \
  "$(git rev-parse --show-toplevel)"
```

PowerShell example:

```powershell
$repo = git rev-parse --show-toplevel
python3 "C:\absolute\path\to\change-requests\scripts\python\sync_cr_registry.py" `
  "C:\absolute\path\to\change-requests" $repo
```

- If **`change-request-report.md`** is missing, the script initializes it from **`templates/change-request-registry-template.md`** when available.

### 2. Review output

- List each **CR id** that was newly registered and its relative path.
- If the script reports **no missing** change requests, the registry already referenced every file it found.

### 3. Manual tidy-up (agent or user)

- Open any newly added rows and adjust **Title** or **Summary** if the script-derived title from the document heading was incomplete.
- Resolve duplicate ids (should not occur if filenames stay unique); fix filenames and re-run sync if needed.

## Rules

- Prefer **absolute paths** for extension root and repo root arguments.
- This command **adds missing rows** and recomputes header counts; it does not delete rows for removed files (avoid accidental loss of audit history—prune manually if required).
