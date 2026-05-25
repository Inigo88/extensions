---
description: "Create a bug file and registry row from a title and optional feature scope"
---

# Register bug (`speckit.bugs.register`)

## Goal

- Assign the next **BXXX** id, create a bug Markdown file from the template, and append a row to the project registry.
- Capture enough context from the user to mark the bug **Open** and ready for triage or fix workflows.

## User input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. If the **title** is missing, ask for a short title before running automation.

## Prerequisites

1. **Configuration**: Read `bugs-config.yml` next to `extension.yml` (**installed path:** `.specify/extensions/bugs/bugs-config.yml`). Fall back to `config-template.yml` in the same folder. Honor `paths.data_dir` and `paths.registry_filename` when locating bug data, and **`status.*`** for new registry rows and the summary line; **`create-bug.sh` / `create-bug.ps1` load paths and markers from the same YAML** (via `scripts/python/bugs_paths.py`, which prints **six** lines: data dir, registry path, then `status.open`, `status.investigating`, `status.fix_proposed`, `status.resolved`). After adding a row, **`reconcile_registry_header.py`** recomputes the registry blockquote (`**N total**`, resolved, open, fix proposed) from all bug table rows.
2. **Extension root**: The directory that contains `extension.yml` for this extension (**after install:** `.specify/extensions/bugs/`). Templates and scripts resolve from here.
3. **Templates**: **`.specify/extensions/bugs/templates/`** — `bug-template.md` and `bug-report-registry-template.md` (relative: `templates/…` under the extension root; both entry scripts resolve `EXTENSION_ROOT` automatically).

## Execution

### 1. Scope and title

- From `$ARGUMENTS` (and the conversation), extract a concise **Title** and optional **feature scope** (e.g. `019-hero` or a 3-digit feature prefix that maps to `specs/019-*` when present).
- Decide whether this is one bug or multiple unrelated issues; if multiple, register separate bugs unless the user explicitly wants one umbrella report.

### 1b. Registry section heading (`NNN — …` in `bug-report.md`)

Headings use the **`019 — Hero Section`** style (3-digit prefix, em dash, title-cased words)—not the raw folder slug `019-hero-section`.

- If a `##` section for that feature’s **3-digit prefix** already exists in `bug-report.md`, the script only appends a table row (heading unchanged).
- If **no** section exists yet, `create-bug.sh` / `create-bug.ps1` **defaults** the new heading from `--feature` / `-Feature` (resolved folder id) via `scripts/python/format_feature_title.py` (e.g. `019-hero-section` → `019 — Hero Section`).
- Pass **`--feature-title`** only when the derived title is wrong (brands, acronyms, or a name that should not follow slug title-case).

### 2. Create files via script

Run from the **repository root** so `git rev-parse --show-toplevel` resolves correctly. Invoke the script by **absolute path** (extension root is derived from the script’s location—no separate root variable):

**Bash (macOS / Linux / Git Bash):**

```bash
bash "/absolute/path/to/bugs/scripts/bash/create-bug.sh" "Bug title here" \
  [--feature "019-hero-section"] \
  [--feature-title "019 — Hero (override)"] \
  [--short-name "optional-slug"]
```

**PowerShell (Windows or `pwsh` anywhere):**

```powershell
pwsh -File "C:\absolute\path\to\bugs\scripts\powershell\create-bug.ps1" `
  -Title "Bug title here" `
  -Feature "019-hero-section" `
  -FeatureTitle "019 — Hero (override)" `
  -ShortName "optional-slug"
```

- Omit `--feature` / `-Feature` for general bugs (script defaults to `000-general`; derived heading `000 — General`).
- Omit **`--feature-title`** / **`-FeatureTitle`** unless you need to override the automatic `NNN — …` heading for a new section.
- Requires **Python 3** on `PATH` (`python3`, `python`, or Windows `py -3`).
- After the script finishes, note the printed **BXXX** and absolute path to the new bug file.

### 3. Fill the bug document

Open the new bug file and complete at minimum:

- **Description**, **Steps to Reproduce**, **Expected** / **Actual** behavior from user input.
- **Severity** (P0/P1/P2 or your team’s scale).
- **Found in** (feature or area).
- Set **Status** checkboxes: mark **Open**, leave others unchecked.

### 4. Registry hygiene

- Confirm the new row appears in the registry under the correct feature section with the **open** marker from **`status.open`** in config (not a hard-coded emoji from this document).
- Do not duplicate feature sections; if the script added a new section, confirm the heading matches what you want (default from the feature folder id, or the **`--feature-title`** override).

## Rules

- Use **absolute paths** in tool calls and when telling the user where files were written.
- Filename convention: `BXXX-short-slug.md` inside **`<repo>/.project/bugs/<feature-folder>/`** by default (or `paths.data_dir` from config).
- Wait for `create-bug.sh` or `create-bug.ps1` to finish before hand-editing the registry to avoid clobbering its updates.
