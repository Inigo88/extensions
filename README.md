# Spec Kit extensions

This repository holds **local Spec Kit (Specify) extensions**—each directory is a self-contained extension with `extension.yml`, commands, templates, and helper scripts. Install them into a project’s `.specify/extensions/` layout with the Specify CLI.

## Extensions

| Directory | Extension id | Summary |
|-----------|--------------|---------|
| [project](project/) | `project` | Standard `.project/` directory tree for assets, backlog, context, documents, change requests, and bugs. |
| [context](context/) | `context` | PRD, tech stack, and design context documents for agent workflows. |
| [backlog](backlog/) | `backlog` | Markdown product backlog with milestones, epics, features, and status aggregation. |
| [bugs](bugs/) | `bugs` | Bug registry, triage, and structured fix workflow. |
| [change-requests](change-requests/) | `change-requests` | Change request templates, registry sync, and implementation workflow. |

Each folder has its own **README** with commands, hooks, configuration, and tooling requirements.

## Prerequisites

- **Specify** / Spec Kit toolchain that supports `specify extension …` (see each extension’s `requires` in `extension.yml`).
- Extensions that declare **Python** in `extension.yml` expect Python **3.8+** for their scripts.

## Installation

From a machine where these sources are available (path may vary):

```bash
specify extension add /path/to/extensions/project
specify extension add /path/to/extensions/context
specify extension add /path/to/extensions/backlog
specify extension add /path/to/extensions/bugs
specify extension add /path/to/extensions/change-requests
```

Many workflows assume **`speckit.project.setup`** has been run first so `.project/` exists. See the [project](project/) extension README for the folder layout.

## Repository layout

```
extensions/
├── README.md           # this file
├── project/            # layout bootstrap
├── context/            # PRD / tech / design
├── backlog/            # product backlog
├── bugs/               # bug tracking
└── change-requests/    # CR registry and workflows
```

## License

Extension metadata in each `extension.yml` lists license (typically **MIT**). Confirm per extension if you redistribute or fork.
