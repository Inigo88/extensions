# Bugs Spec Kit extension

Markdown-centric bug tracking: register ids and files, triage open work from the registry, and run a structured fix workflow with optional approval before implementation.

## Layout

| Path | Purpose |
|------|---------|
| `<repo>/.project/bugs/` | Default location for bug Markdown + `bug-report.md` (`paths.data_dir`). |
| `.specify/extensions/bugs/` | Installed extension root (`extension.yml`, `commands/`, `templates/`, `scripts/`, `bugs-config.yml`). |
| `extension.yml` | Manifest: `speckit.bugs.register`, `speckit.bugs.triage`, `speckit.bugs.fix`. |
| `commands/` | One markdown file per slash command. |
| `templates/` | `bug-template.md` (single bug), `bug-report-registry-template.md` (aggregate `bug-report.md`). |
| `scripts/bash/create-bug.sh` | Creates **BXXX** file, updates registry tables, then reconciles the summary line; uses templates from this extension. Resolves `paths.*` and `status.*` via `scripts/python/bugs_paths.py` (same YAML as `bugs-config.yml`). |
| `scripts/powershell/create-bug.ps1` | Same behavior as `create-bug.sh` for PowerShell (`pwsh`); uses the same Python helpers. |
| `scripts/python/` | `bugs_paths.py` (prints data dir, registry path, and four status markers), `format_feature_title.py` (default `NNN — …` headings), `update_registry.py` (registry tables), `reconcile_registry_header.py` (summary counts from table rows + YAML markers). |
| `bugs-config.yml` / `config-template.yml` | Runtime YAML beside `extension.yml`; `config-template.yml` matches at install and is a reset reference (same pairing as the backlog extension). |

## Installation

```bash
# Offline: registers speckit.bugs.* commands
specify extension add bugs
```

After install, the extension root is **`.specify/extensions/bugs/`** (`extension.yml`, `commands/`, `templates/`, `scripts/`, `bugs-config.yml`). Bug Markdown and the registry live under **`<repo>/.project/bugs/`** by default (`paths.data_dir` in `bugs-config.yml`). Requires **Python 3** (for path/status helpers, `update_registry.py`, `reconcile_registry_header.py`, and template fill). Use **`bash`** + `create-bug.sh` or **`pwsh`** + `create-bug.ps1`. Paths and registry status markers come from **`bugs-config.yml`** / **`config-template.yml`** next to `extension.yml` (see `scripts/python/bugs_paths.py`, which prints **six** lines: two paths, then `status.open`, `status.investigating`, `status.fix_proposed`, `status.resolved`).

## Disabling

```bash
# Unregisters speckit.bugs.* until you enable again
specify extension disable bugs

# Restores speckit.bugs.*
specify extension enable bugs
```

## Commands

- **`/speckit.bugs.register`** — Create `BXXX` + registry row; fill initial fields from user input.
- **`/speckit.bugs.triage`** — Review open bugs, set severity/status, align registry dashboard.
- **`/speckit.bugs.fix`** — Investigate, plan, implement, verify, resolve; approval gate for non-trivial fixes when enabled in config.

## Changelog

- **1.0.2** — Registry summary line is rebuilt from bug table rows; new rows use `status.open` from YAML (not hard-coded). `bugs_paths.py` prints six lines (paths + status markers).
- **1.0.1** — `scripts/powershell/create-bug.ps1` (parity with `create-bug.sh` on Windows / `pwsh`).
- **1.0.0** — Extension layout with three commands; `create-bug.sh` resolves templates from the extension root.
