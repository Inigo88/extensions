# Change requests Spec Kit extension

Markdown-centric change requests: create **CR###** documents from a template, keep an aggregate registry in sync (including rescans for files not yet listed), and run a structured implementation workflow with an optional approval gate.

## Layout

| Path | Purpose |
|------|---------|
| `<repo>/.project/change-requests/` | Default location for CR Markdown + `change-request-report.md` (`paths.data_dir`). |
| `.specify/extensions/change-requests/` | Installed extension root (`extension.yml`, `commands/`, `templates/`, `scripts/`, `change-requests-config.yml`). |
| `extension.yml` | Manifest: `speckit.change-requests.register`, `speckit.change-requests.implement`, `speckit.change-requests.sync-registry`. |
| `commands/` | One markdown file per slash command. |
| `templates/` | `change-request-template.md` (single CR), `change-request-registry-template.md` (aggregate `change-request-report.md`). |
| `scripts/bash/create-change-request.sh` | Creates **CRXXX** file, updates registry counts and tables; uses templates from this extension. Resolves `paths.*` via `scripts/python/change_requests_paths.py` from `change-requests-config.yml` (or `config-template.yml` if the live config is absent). |
| `scripts/powershell/create-change-request.ps1` | PowerShell (`pwsh`) entrypoint: creates **CRXXX** files, updates the registry, and runs the Python helpers used by `create-change-request.sh`. |
| `scripts/python/sync_cr_registry.py` | Scans the data directory for `CR*.md` files missing from the registry and appends rows; refreshes header counts. |
| `change-requests-config.yml` / `config-template.yml` | Runtime YAML beside `extension.yml`; `config-template.yml` is the shipped template for installs and resets, `change-requests-config.yml` is the working copy you edit. |

## Installation

```bash
specify extension add change-requests
```

After install, the extension root is **`.specify/extensions/change-requests/`**. Change request Markdown and the registry live under **`<repo>/.project/change-requests/`** by default. Requires **Python 3**. Use **`bash`** + `create-change-request.sh` or **`pwsh`** + `create-change-request.ps1`. Paths come only from **`change-requests-config.yml`** / **`config-template.yml`** next to `extension.yml` (see `scripts/python/change_requests_paths.py`).

## Disabling

```bash
specify extension disable change-requests
specify extension enable change-requests
```

## Commands

- **`/speckit.change-requests.register`** — Create `CRXXX` + registry row from a title and optional feature scope (creation from template).
- **`/speckit.change-requests.implement`** — Plan, implement, verify, and complete a CR; approval gate for non-trivial work when enabled in config.
- **`/speckit.change-requests.sync-registry`** — Register any CR files on disk that are missing from the registry table; realign header counts.

## Changelog

- **1.0.0** — Initial extension: register, implement, sync-registry; Bash and PowerShell create scripts; Python helpers aligned with the bugs extension layout.
