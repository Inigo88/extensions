---
description: "Create a change request file from the template and append a row to the project registry"
---

# Register change request (`speckit.change-requests.register`)

## Goal

- Assign the next **CRXXX** id, create a change request Markdown file from the template, and append a row to the project registry.
- Capture enough context from the user to mark the change request as **Draft** and ready for approval or implementation workflows.

## User input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. If the **title** is missing, ask for a short title before running automation.

## Prerequisites

1. **Configuration**: Read `change-requests-config.yml` next to `extension.yml` (**installed path:** `.specify/extensions/change-requests/change-requests-config.yml`). Fall back to `config-template.yml` in the same folder. Honor `paths.data_dir` and `paths.registry_filename` when locating artifacts; **`create-change-request.sh` / `create-change-request.ps1` load these paths** via `scripts/python/change_requests_paths.py`.
2. **Extension root**: The directory that contains `extension.yml` for this extension (**after install:** `.specify/extensions/change-requests/`). Templates and scripts resolve from here.
3. **Templates**: **`templates/change-request-template.md`** and **`templates/change-request-registry-template.md`** under the extension root.

## Execution

### 1. Scope and title

- From `$ARGUMENTS` (and the conversation), extract a concise **Title** and optional **feature scope** (e.g. `019-hero` or a 3-digit feature prefix that maps to `specs/019-*` when present).
- If the user describes multiple unrelated changes, register **separate** change requests unless they explicitly want one umbrella document.

### 1b. Registry section heading (`NNN — …` in `change-request-report.md`)

Headings use the **`019 — Hero Section`** style (3-digit prefix, em dash, title-cased words)—not the raw folder slug `019-hero-section`.

- If a `##` section for that feature’s **3-digit prefix** already exists in `change-request-report.md`, the script only appends a table row (heading unchanged).
- If **no** section exists yet, `create-change-request.sh` / `create-change-request.ps1` **defaults** the new heading from `--feature` / `-Feature` via `scripts/python/format_feature_title.py`.
- Pass **`--feature-title`** / **`-FeatureTitle`** only when the derived title is wrong (brands, acronyms, or names that should not follow slug title-case).

### 2. Create files via script

Run from the **repository root** so `git rev-parse --show-toplevel` resolves correctly. Invoke the script by **absolute path** (extension root is derived from the script’s location):

**Bash (macOS / Linux / Git Bash):**

```bash
bash "/absolute/path/to/change-requests/scripts/bash/create-change-request.sh" "Change request title here" \
  [--feature "019-hero-section"] \
  [--feature-title "019 — Hero (override)"] \
  [--short-name "optional-slug"]
```

**PowerShell (Windows or `pwsh` anywhere):**

```powershell
pwsh -File "C:\absolute\path\to\change-requests\scripts\powershell\create-change-request.ps1" `
  -Title "Change request title here" `
  -Feature "019-hero-section" `
  -FeatureTitle "019 — Hero (override)" `
  -ShortName "optional-slug"
```

- Omit `--feature` / `-Feature` for general change requests (script defaults to `000-general`; derived heading `000 — General`).
- Omit **`--feature-title`** / **`-FeatureTitle`** unless you need to override the automatic `NNN — …` heading for a new section.
- Requires **Python 3** on `PATH` (`python3`, `python`, or Windows `py -3`).
- After the script finishes, note the printed **CRXXX** and absolute path to the new file.

### 3. Fill the change request document

Open the new Markdown file and complete at minimum:

- **Summary**, **Rationale**, and **Scope** (in / out) from user input.
- **Impact analysis** at a level appropriate to the risk.
- **Priority** and **Target area**.
- Set **Status** checkboxes: mark **Draft**, leave others unchecked.

### 4. Registry hygiene

- Confirm the new row appears in the registry under the correct feature section with the **draft** marker from **`status.draft`** in config (align emoji with YAML rather than hard-coding in prose).
- Do not duplicate feature sections; if the script added a new section, confirm the heading matches intent (default from the feature folder id, or the **`--feature-title`** override).

## Rules

- Use **absolute paths** in tool calls and when telling the user where files were written.
- Filename convention: `CRXXX-short-slug.md` inside **`<repo>/.project/change-requests/<feature-folder>/`** by default (or `paths.data_dir` from config).
- Wait for `create-change-request.sh` or `create-change-request.ps1` to finish before hand-editing the registry to avoid clobbering its updates.
