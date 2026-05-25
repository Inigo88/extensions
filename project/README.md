# Project layout extension

Creates a standard **`.project/`** tree at the repository root so Spec Kit workflows have predictable places for assets, context, docs, and lightweight tracking folders.

## What you get

After installation, the command **`speckit.project.setup`** is available. Running it ensures these directories exist (creating only what is missing; existing files are left alone):

| Folder | Role |
|--------|------|
| `.project/assets/` | Binaries, exports, images |
| `.project/backlog/` | Backlog or planning notes |
| `.project/context/` | PRD, tech stack, design — typical target for context commands |
| `.project/documents/` | General project documentation |
| `.project/crs/` | Change requests / change notes |
| `.project/bugs/` | Bug reports and triage |

Empty folders get a **`.gitkeep`** only when that file is not already there. If **`.project/README.md`** is missing, the command may add a short folder guide; an existing README is never overwritten.

## Installation

```bash
# Offline: registers speckit.project.setup
specify extension add project
```

## Disabling

```bash
# Unregisters speckit.project.setup until you enable again
specify extension disable project

# Restores speckit.project.setup
specify extension enable project
```

## Metadata

See **`extension.yml`** for id, version, and required Spec Kit version.
