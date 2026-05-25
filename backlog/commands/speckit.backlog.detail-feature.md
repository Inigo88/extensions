---
description: "Interactively extend one Feature's **Description** with Why, What, Acceptance Criteria, and Open Questions (concise; order fixed)"
---

# Detail Feature in Backlog

## Goal

- Restructure a single Feature’s `**Description**:` into **Why** → **What** → **Acceptance Criteria** → **Open Questions** in that fixed order, with brief copy suitable for backlog depth.
- Guide the user interactively through the steps, persist edits safely, and do **not** change Feature **Status** as part of this command.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input alongside feature id/title and optional path: treat both as available even if `$ARGUMENTS` appears literally empty; only ask the user to repeat missing identifiers if **both** are absent.

If several features match, ask **one** disambiguation question before editing.

## Prerequisites

1. **Configuration**: Read `.specify/extensions/backlog/backlog-config.yml` (fall back to `config-template.yml`). You only need `file_pattern` and `backlog_roots` for discovery unless the user gave a path.
2. **Target backlog**: Open the Markdown file (explicit path from input, else auto-discover using the same rules as **`/speckit.backlog.update`**).

### Markdown shape (preserve sibling field order)

Keep **`**Branch**:`**, **`**Status**:`**, and **`**Priority**:`** unchanged and in the **same positions** as today (after the description block). Every line that belongs to the description **must** stay **indented** (leading space or tab) so backlog tooling can still find Status/Branch/Priority.

```markdown
- **Feature <id>**: <Title>
  **Description**:
  **Why**
  <1–3 short sentences or few bullets>

  **What**
  <prior plain description, lightly condensed if needed>

  **Acceptance Criteria**
  <bullets or short sentences>

  **Open Questions**
  <bullets; mark *Answered:* or *Deferred* as you resolve them>

  **Branch**:
  **Status**: <unchanged id>
  **Priority**: <unchanged id>
```

If the file used a **single-line** `**Description**: …` before, split so the colon opens the block and the four subsections follow on new lines as above.

## Execution Steps

### Section order (mandatory)

After these execution steps, the Feature's `**Description**:` body **must** contain these subsections **in this exact order**:

1. **Why** — reason for the feature (problem, outcome, or driver).
2. **What** — the **previous** simple description content (the feature in plain terms); tighten wording if it is long, without changing meaning.
3. **Acceptance Criteria** — minimal, testable conditions for “done enough” at backlog level (not a full test plan).
4. **Open Questions** — uncertainties, dependencies, or decisions still outstanding.

Use **bold run-in headings** on their own line (same indentation as other Feature fields), then 1–3 short sentences or a **small** bullet list (≤5 bullets per section unless the user insists). Keep every section **brief and focused**; defer deep edge cases to specify/clarify.

### Interactive workflow (stop and wait for the user between steps)

Execute **in order**. After each user reply, **update the backlog file** (or the in-memory draft you will write once — prefer **saving Why + What skeleton early** after step 3 so progress is not lost; then append/refine AC and OQ).

### Step 1 — Show current description

Locate the Feature. Present **verbatim** (or clearly quoted) the **current** `**Description**:` content.

If `**Description**:` already contains **Why** / **What** / **Acceptance Criteria** / **Open Questions** headings, ask whether to **re-run** (refresh sections from new answers), **partially update** (e.g. only Open Questions), or **abort** — do not silently duplicate headings.

Treat “simple text” as everything after `**Description**:` until the next indented `**Branch**:` / `**Status**:` / `**Priority**:` line (or end of description block). That text becomes the raw material for **What** later.

### Step 2 — Question for **Why**

Ask **one** targeted question that helps define the **Why** section, for example:

- “What user or business outcome is blocked or weak today if we do **not** ship this?”
- “What measurable or qualitative change should exist after this ships?”

Tailor the question to the feature; avoid generic multi-part questionnaires.

### Step 3 — User answers → write **Why**; stage **What**

Wait for the user.

From their answer, draft **Why** (high-level, concise). Restructure the Feature so **`**Description**:`** opens a block containing:

- **Why** (new),
- **What** (the **prior** description content from step 1, edited only for length/clarity).

Do **not** add Acceptance Criteria or Open Questions yet unless the user already gave them unprompted — in that case, you may stash notes but still complete steps 4–7 explicitly.

Save to disk (partial update is OK).

### Step 4 — Ask for Acceptance Criteria

Ask the user for **Acceptance Criteria** at backlog granularity: what must be true to call the feature successfully delivered, in **few** bullets or sentences.

### Step 5 — Save **Acceptance Criteria**

Wait for the user. Merge their input into an **Acceptance Criteria** subsection — **short**, no duplicate of the full spec. Append this section **after** **What** in the file (order: Why → What → Acceptance Criteria → Open Questions).

Save to disk.

### Step 6 — **Open Questions** (initial list)

Without waiting for new input if you already have enough signal: derive the **first** **Open Questions** list from gaps between **Why**, **What**, and **Acceptance Criteria** (assumptions, unknown scope, dependencies, metrics, legal/security, rollout).

Present the list to the user and write it under **Open Questions** (same ordering rules). Each item should be one line or a short clause.

Save to disk.

### Step 7 — Iterate answer or defer

Loop until the user says they are done (or there are no remaining actionable questions):

- For each open item: ask whether to **answer** (you record a concise resolution next to or below the item), **defer** (mark explicitly as *Deferred* with a word or two on why / when it will be revisited), or **drop** if obsolete.
- Keep the **Open Questions** section **trim**; answered items should shrink to a brief resolution or move out if the user prefers a clean “remaining only” list.

Save after each batch of resolutions.

This command should **not** change Feature status by itself.

## Output

Confirm:

- Backlog path and Feature **id** + **title**
- That the four subsections exist in order (**Why** → **What** → **Acceptance Criteria** → **Open Questions**)
- Brief note on any **Deferred** questions left for specify/clarify

## Graceful Degradation

- **Feature not found**: stop; list nearest id/title matches if helpful.
- **Ambiguous target**: one clarifying question; do not guess.
- **User wants maximum brevity**: enforce tighter caps (e.g. 2 sentences per narrative section, 3 AC bullets) and say so in the summary.

## General guidelines

- Do not create or switch git branches.
- Do not renumber or remove features.
- Do not inflate scope — **condense**; `/speckit.specify` and `/speckit.clarify` own depth.
