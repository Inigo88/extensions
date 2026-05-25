# Context Documents Extension

Structured **PRD**, **technology stack**, and **design** context for Spec Kit—machine-oriented inputs for **project constitution** (see `.cursor/skills/speckit-constitution`).

## Overview

This extension provides three optional, template-driven workflows. Together they:

- **Capture product intent** in a PRD (problem, users, scope, NFRs, risks) with best-practice framing and follow-up prompts for critical gaps
- **Record stack decisions** grounded in the PRD, including **section 4 security principles**, selective two-option comparisons where tradeoffs matter, plus verification hooks for agent-assisted development
- **Describe UX and surfaces** when the product has a user-facing or interactive UI, grounded **only** in the **PRD** plus user input (not the tech-stack document)
- **Write defaults** to **`.project/context/`** (`prd.md`, `tech-stack.md`, `design.md`) unless the user overrides the output path in arguments or the message

Artifacts are written primarily for **AI agents** (implementation and constitution drafting): explicit, decision-ready, and easy to scan—not polished human-facing prose.

## Workflow sequence

Typical order when you want all three files:

1. **`speckit.context.prd`** — User supplies a product description (and optional paths or notes); a draft PRD is produced; the user is prompted for missing high-impact details.
2. **`speckit.context.tech-stack`** — Uses the PRD plus any extra constraints; produces the tech stack document; the user is prompted to resolve open questions and choose among options where the workflow offered alternatives.
3. **`speckit.context.design`** — **Only if** the product has a user-facing interface: uses the **PRD and user input only** (does **not** read the tech-stack file); produces the design document; the user is prompted for remaining UX gaps. May be run whenever a PRD exists—you do **not** need to finish tech-stack first for design.

Constitution creation or update uses those files (for example `@.project/context/prd.md`) and is **out of scope** for these three commands.

## Commands

| Command | Description |
| ------- | ----------- |
| `speckit.context.prd` | Draft or update an AI-oriented PRD under `.project/context/` (constitution pipeline step 1); prompt for missing decision-critical details |
| `speckit.context.tech-stack` | Produce or update tech stack context from the PRD plus input (step 2); options where tradeoffs matter; prompts for decisions |
| `speckit.context.design` | Produce or update design/UX context from the **PRD** and user input only (step 3, UI products only); prompts for open UX questions |

## Outputs

- **Default directory**: `.project/context/`
- **Default files**: `prd.md`, `tech-stack.md`, `design.md`
- **Overrides**: `out:`, `output:`, or `path:` in arguments, or an explicit path in the user message when the command supports it (see each command workflow).

## Installation

```bash
# Offline: registers speckit.context.* commands
specify extension add context
```

## Disabling

```bash
# Unregisters speckit.context.* until you enable again
specify extension disable context

# Restores speckit.context.*
specify extension enable context
```

## Templates

Command workflows load section shells from:

- `templates/prd-template.md`
- `templates/tech-stack-template.md`
- `templates/design-template.md`

## Prerequisites and guards

- **`speckit.context.tech-stack`** expects a PRD (default `.project/context/prd.md` or a path you pass); it stops with a clear error if none is available.
- **`speckit.context.design`** requires a **PRD** (default `.project/context/prd.md` or a path you pass) and targets products with user-facing or interactive UI. It does **not** use the tech-stack file. For headless-only scope, skip this command.

## Extension structure

```text
context/
├── extension.yml       # Manifest (schema_version, extension, requires, provides, tags)
├── README.md
├── .gitignore
├── commands/
│   ├── speckit.context.prd.md
│   ├── speckit.context.tech-stack.md
│   └── speckit.context.design.md
└── templates/
    ├── prd-template.md
    ├── tech-stack-template.md
    └── design-template.md
```

There is no `config-template.yml`; output paths are controlled via command arguments (see each command workflow). When you publish this extension separately, set **`repository`** in `extension.yml` to your canonical URL.
