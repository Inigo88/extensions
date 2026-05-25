---
description: "Create a product backlog from a natural-language product description"
---

# Create Product Backlog

## Goal

- Produce one backlog Markdown file that follows the backlog template and `backlog-config.yml` (enabled Milestone/Epic levels and status/priority catalogs).
- Resolve the output path, run the existing-file gate (replace / amend / abort), then write or merge content without inventing structure when templates are missing.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input alongside the typed product description: treat both as available even if `$ARGUMENTS` appears literally empty; only ask for a short product description if **both** are empty.

## Prerequisites

1. **Configuration**: Read `.specify/extensions/backlog/backlog-config.yml` (fall back to `config-template.yml` if it does not exist). Extract:
   - `levels.milestones` (bool) — whether to emit Milestone headings.
   - `levels.epics` (bool) — whether to emit Epic headings.
   - `feature_statuses[]` — allowed `**Status**:` values for Features. Use only `id` values from this list.
   - `parent_statuses[]` — allowed `**Status**:` values for Epics and Milestones. Use only `id` values from this list.
   - `priorities[]` — allowed `**Priority**:` values for Milestones, Epics, and Features. Use only `id` values from this list.
   - `backlog_roots[]` — ordered directories (repo-relative) scanned with `file_pattern` for auto-discovery in other commands; use the order and paths **exactly** as in the loaded file (do not substitute a different search order from this document).
2. **Template**: Read `.specify/extensions/backlog/templates/backlog-template.md` to understand the section order. Skip Milestone/Epic sections in the template when their level is disabled.
3. **Output path**:
   - If the user specified a path in the input (e.g. `backlog/my-product.md` or `docs/backlog.md`), use that path (relative to repo root).
   - Otherwise, place the new file under **the first directory in `backlog_roots`** as **`<slug>-backlog.md`**, where `<slug>` is a **filename-safe** provisional name (2–5 words) from the product description. If `file_pattern` uses a different glob shape, align the new file’s basename with that pattern (substitute the `*` segment with `<slug>`). Create **that directory** if it does not exist. **OUTPUT_PATH** must be known before the full hierarchy is generated.
   - All paths are relative to the repo root; use absolute paths when reading/writing files.

## Existing artifact check

Run once **OUTPUT_PATH** is resolved, **before** drafting or writing that path. (For the default filename, **OUTPUT_PATH** uses the provisional slug from Prerequisites item 3.)

1. **Exit early** — If nothing exists at **OUTPUT_PATH**, continue the pipeline.
2. **Fast path** — If a file exists **and** the user **unambiguously** asked for **Replace** or **Amend / update** in the same message → one-line notice + mini-summary, then proceed in that mode (**Amend** = merge per **Update runs (merge rules)**; **Replace** = rebuild); **skip steps 3–6**. If intent is ambiguous, run the full gate (steps 3–6).
3. **Skim** — Read enough to recap: title, product name line, top-level headings, dashboard / milestone–epic–feature counts.
4. **Warn** — Say the file already exists at **OUTPUT_PATH** and may be replaced or heavily changed.
5. **Summarize** — Short recap only (no full file paste).
6. **Confirm** — Ask: **Replace** | **Amend / update** (merge per **Update runs (merge rules)**) | **Abort**. If unanswered, **stop** the pipeline here.

## Update runs (merge rules)

When **OUTPUT_PATH** already contains a backlog and the user chose **Amend / update** (including after a clearly **Amend** fast path):

- **Load** the file first; 
- **Merge** the new product description and hierarchy/work-item changes **without** discarding existing milestones, epics, or features unless the user explicitly removes or replaces them or chose **Replace**.
- **Replace** means regenerate from the template and current product description; prior backlog content is discarded unless the user lists sections, milestones, epics, or feature IDs to preserve.

## Execution Steps

Given the product description, do this:

0. **Existing artifact check (gate)** — Resolve **OUTPUT_PATH** (provisional slug when using the default). Run **Existing artifact check**; if it blocks, **stop** until **Replace**, **Amend / update**, or **Abort** (**Abort** ends the workflow).

1. **Derive backlog content**:
   - **Product name**: Concise (2–5 words).
   - **Product description**: 2–4 sentences on what the product is, its main purpose, and key value.
   - **Business problem**: Clear statement of the problem or opportunity; who is affected and what outcome we expect.
   - **Actors**: List of actors (user types, roles, or systems) that will use or interact with the product; each with a brief role or description.

2. **Build the hierarchy** based on enabled levels. Features are **always** present; the two levels above them can be toggled independently. ID format and number of segments follow the enabled levels:

   | `milestones` | `epics` | Hierarchy            | Milestone ID | Epic ID  | Feature ID |
   | :----------- | :------ | :------------------- | :----------- | :------- | :--------- |
   | `true`       | `true`  | M → E → F *(default)* | `1`         | `1.1`    | `1.1.1`    |
   | `false`      | `true`  | E → F                | —            | `1`      | `1.1`      |
   | `true`       | `false` | M → F                | `1`          | —        | `1.1`      |
   | `false`      | `false` | F (flat)             | —            | —        | `1`        |

   - **Milestones** (only if `levels.milestones=true`): High-level delivery phases or goals (e.g. MVP, Scale, Optimize). Each has **Title**, **Description**, **Status**, **Priority**.
   - **Epics** (only if `levels.epics=true`): Larger capability or theme. Each has **Title**, **Description**, **Status**, **Priority**. When milestones are enabled, epics are nested under their milestone; when milestones are disabled, epics are top-level.
   - **Features** (always): Concrete, testable items. Each has **Title**, **Description**, **Branch**, **Status**, **Priority**. Do NOT use the "As a user, I want..." format — write simple, direct descriptions of what the feature does. The **Branch** label is included with no value (just `**Branch**: `); branch names are assigned during the specify workflow.

3. **Pick statuses and priorities** from the configured catalogs:
   - Each Milestone and Epic **MUST** use a status `id` from `parent_statuses`.
   - Each Feature **MUST** use a status `id` from `feature_statuses`.
   - Each Milestone, Epic, and Feature **MUST** use a priority `id` from `priorities`.
   - Newly generated items use the status catalog entry with `aggregate: "initial"` (defaults to `Backlog`) unless the user input implies otherwise.
   - Use informed guesses and industry norms to set priority; when uncertain, prefer the **`Medium` id** if it exists in `priorities[]`, otherwise pick a neutral entry from that list. Keep scope realistic.

4. **Write the backlog**: Fill the template structure with the generated content. Preserve section order and headings from the template (omitting disabled levels). Set **Created** to the current date. Write the result to the output path. Do NOT output a `## Notes` section at the end.

5. **Project Dashboard layout** — adapt to enabled levels:
   - **M+E+F**: one `#### Milestone N: <title>` sub-section per milestone, each with `**Status**:` / `**Priority**:` lines and a single table whose rows alternate between bolded Epic header rows (`| **E1.1** | **Title** | ... |`) and Feature rows (`| 1.1.1 | Title | ... |`); separate epics within the same milestone with a `| --- | --- | --- | --- |` row.
   - **E+F**: a single dashboard table grouping each top-level Epic (bolded header row) and its Features.
   - **M+F**: one `#### Milestone N:` sub-section per milestone with a table listing its Features only (no Epic rows).
   - **F**: a single flat table of Features under `### Project Dashboard`.
   - In every case, the Status and Priority cells use the catalog's `display` string wrapped in backticks (e.g. `` `⚪ Backlog` ``, `` `High` ``); the source-of-truth `**Status**:` / `**Priority**:` lines further down use the plain `id`.

6. **Provide constitution context**: Extract the entire first section of your generated backlog (Product description, Business problem, Actors — explicitly EXCLUDING Milestones/Epics/Features). Present this excerpt to the user and **ask if they would like to initialize or update the project constitution** (`/speckit.constitution`) using this text. Do not execute the constitution workflow until the user confirms.

## Output

Confirm the output file path and provide a short summary:
- Product name
- Counts: number of milestones / epics / features (omit levels that are disabled in config)
- The constitution-context excerpt (from step 6)

## Config as source of truth

Allowed **status** and **priority** `id` values, their dashboard `display` strings, aggregation `aggregate` roles, hook `events` mapping, and discovery (`file_pattern`, `backlog_roots`, `levels`) come **only** from the YAML you loaded in Prerequisites — plus `extension.yml` → `config.defaults` for `file_pattern` and `levels.*` when the framework must synthesize a minimal file.

Do **not** copy status, priority, or event **id** strings from this command document; always take them from that YAML (or from `config-template.yml` beside `extension.yml` in the installed extension when the live file is absent). Use `aggregate: "initial"` in each catalog to pick default ids for new items.

## Graceful Degradation

- If `backlog-config.yml` is missing, fall back to `config-template.yml` in the same extension directory. If both are missing, read `extension.yml` in that directory for `config.defaults` (`file_pattern`, `levels_milestones`, `levels_epics`), then stop and ask the user to restore the shipped YAML before inventing catalogs — do not substitute ad-hoc status or priority lists from this document.
- If the template file is missing, abort and report the missing path; do not invent the structure.

## General guidelines

- Focus on **WHAT** the product does and **WHO** it serves; avoid implementation detail.
- Milestones should be few (e.g. 2–4) and represent major phases.
- Epics group related features; features should be testable and user-valued.
- Do not create or switch git branches.
