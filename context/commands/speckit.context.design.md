---
description: "Produce or update AI-oriented design/UX context under .project/context/ (constitution pipeline step 3, UI products only); PRD-grounded with user input; prompts for open UX questions."
---

# Context: Design

## Goal

Give the repository a **design / UX context** artifact under `.project/context/`: PRD-grounded, agent-scannable, and usable for constitution when the product has user-facing UI—without treating the tech-stack file as product truth.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input: treat it as available even when `$ARGUMENTS` appears literally empty below; only ask the user to repeat themselves if both are empty.

## Prerequisites

1. **Template** — `.specify/extensions/context/templates/design-template.md` (mandatory; abort if missing).
2. **Default output** — `.project/context/design.md`.

### Paths (do first)

1. **OUTPUT_PATH** / **WORK_CONTEXT** — From `out:`/`output:`/`path:` line (`*.md`) or sole repo-relative `*.md` in `$ARGUMENTS`; else **`.project/context/design.md`**. Strip used parts; remainder + chat = **WORK_CONTEXT**.
2. **PRD_PATH** + **UI gate** — `prd:` or `@` PRD `.md` → else **`.project/context/prd.md`** if it exists → else **ERROR**, stop. Load PRD; clearly non-UI → **ERROR**, stop. Ambiguous → ≤ **3** `NEEDS INPUT:` + **Prioritized questions** for UI intent.
3. **Collision** — File at **OUTPUT_PATH** → stop; ask **Merge | Replace | Different path | Abort**; on **Different path**, update **OUTPUT_PATH** and repeat (3).
4. **No file** — `mkdir -p` parent.

### Update runs (merge rules)

**Merge**: load file, merge **WORK_CONTEXT** + PRD updates. **Replace**: template + **WORK_CONTEXT** + PRD only. **Revision history**: one new row in **§1** per run only.

## Execution Steps

Execute the following steps **in order**. Treat earlier steps as gates: if a step **ERROR**s, stop the pipeline.

### Design document principles

1. **PRD-grounded** — **§2** and product-facing sections trace **only** to **PRD_PATH**. **§8** may reflect platform or design-system hints **only** when the user stated them in **WORK_CONTEXT** or the conversation, or in **non-stack** files they `@`-mention per step **2** (never **`.project/context/tech-stack.md`** or a stack artifact); otherwise use `TBD` / `NEEDS INPUT:`.
2. **Agent-scannable** — Prefer numbered steps, tables, and explicit screen lists over long narrative.
3. **Living document** — Informed defaults for low-impact gaps; at most **3** `NEEDS INPUT:` markers in the entire artifact (prioritize: primary user journeys > security-sensitive flows > accessibility policy > visual brand when unspecified).
4. **Template fidelity** — Preserve mandatory heading order from the template; optional sections follow template *Optional* rules.

### 1 — Parse paths, validate input, prepare output location

Run **Paths (do first)** (1)–(4). Stop on **ERROR** or unanswered collision choice.

### 2 — Context ingestion

1. **Load the template** from **`.specify/extensions/context/templates/design-template.md`**. If the file cannot be read or is missing: **ERROR** `Cannot load design template at .specify/extensions/context/templates/design-template.md` and **Stop**.
2. **Load the PRD** from **PRD_PATH**; cite FR/NFR IDs where they constrain UX. **Do not** load **`.project/context/tech-stack.md`** or any **technology-stack** artifact as an input. **Product scope and requirements** for this document come **only** from the PRD; **WORK_CONTEXT** and the user message may add optional UX or platform hints as plain text (they do not override the PRD).
3. Expand **WORK_CONTEXT** with any user-referenced paths (`@`-mentions, listed files), **except** do not open **`.project/context/tech-stack.md`** or any path the user supplied **only** as a technology-stack document—those are **out of scope** as inputs to this workflow.
4. **Optional** — If `.specify/memory/constitution.md` exists, read it once for non-negotiable UX or accessibility principles; do not paste it wholesale into the design doc.

### 3 — Internal coverage map (do not show unless useful)

Assign **Provided** / **Partial** / **Missing** for:

- **§1** document control
- **§2** PRD-sourced context for design
- **§3** baseline principles (from template)
- **§4** product-specific principles
- **§5** user flows (primary paths)
- **§6** information architecture
- **§7** key screens / surfaces
- **§8** visual and interaction (platform or design-system hints **only** when user-supplied; otherwise `TBD`)
- **§9** accessibility targets
- **§10** open questions (only if `NEEDS INPUT:` or material `TBD`)

### 4 — Draft the design document (working copy)

**Update runs:** **Merge** → load + merge **WORK_CONTEXT** / PRD updates. **Replace** or **Greenfield** → template shell as working copy.

Produce the full markdown (working copy; do not write to disk until step **6**).

1. **§1 — Document control** — **Status** default `Draft`, **Last updated** today (ISO). **Source PRD** → **PRD_PATH**. Under **### Revision history**, append **exactly one** row: greenfield → `Initial draft from PRD + user context`; update → short summary of what changed.
2. **§2 — Context (from PRD)** — **PRD reference**, **Summary for design**, **Product basics** table; ground every claim in the loaded PRD; `NEEDS INPUT:` sparingly (≤3 in whole doc).
3. **§3 — Product design principles** — Keep template defaults unless the user explicitly asked to replace them.
4. **§4 — Product-specific design principles** — At least **one** subsection with concrete initiative rules (defaults acceptable if user gave little; document as assumptions in **§10** rows when needed).
5. **§5 — User flows** — At least **one** named flow covering the **primary** user goal; add more when PRD implies them. Steps must be ordered and testable.
6. **§6 — Information architecture** — Table of main areas/entities aligned with PRD scope (omit empty shell).
7. **§7 — Key screens / surfaces** — Table listing screens that implement **FR**s or PRD flows; align naming and goals with the PRD (e.g. “Settings — web”).
8. **§8 — Visual and interaction** — Reflect **PRD** constraints and any **explicit** platform or design-system hints from **WORK_CONTEXT** / the user message; use `TBD` where unspecified. **Do not** infer implementation choices from a tech-stack artifact.
9. **§9 — Accessibility** — Concrete targets (e.g. WCAG 2.2 AA) or `TBD` with **§10** follow-up; keyboard/focus/screen reader notes.
10. **§10 — Open questions** — Include **only** when `NEEDS INPUT:` exists or material `TBD` needs owner follow-up; otherwise **omit entire §10** (including `## 10`).
11. **Deliverable hygiene** — No workflow or validation prose inside **OUTPUT_PATH**; no bare `[ ]` placeholders; **H1** `# Design document for [real product name]`; no empty optional sections left as shells.

### 5 — Design quality validation (inline only; no separate checklist file)

Run validation against the working copy. For each criterion assign **Pass** or **Fail**; on **Fail**, note one concrete issue (quote a short fragment or cite §). Intermediate passes may stay **internal**; the **user-facing** **D1–D10** table is mandatory in step **7** (after writing the file).

| # | Criterion |
|---|-----------|
| D1 | **PRD_PATH** in **§1** and/or **§2**; **§2** grounded in the loaded PRD (no fabricated product). |
| D2 | **§5** has at least **one** complete primary flow aligned with PRD goals (or explicit `NEEDS INPUT:` if blocked, ≤3 markers doc-wide). |
| D3 | **§7** lists screens/surfaces tied to PRD scope (no orphans without a PRD hook). |
| D4 | **§6** and **§7** agree (IA has screen coverage or honest `TBD` with **§10**). |
| D5 | **§8** does not contradict the PRD; platform/design-system claims **only** from PRD or user **WORK_CONTEXT** / message—else `TBD`; this workflow does **not** read or rely on a tech-stack file. |
| D6 | **§9** states accessibility targets or explicit `TBD` with follow-up; not empty boilerplate. |
| D7 | `NEEDS INPUT:` ≤ **3**; each maps to **§10** or the right **§5**/**§7** row; when **zero** markers and no material **TBD**, **§10** is **absent**. |
| D8 | Mandatory **§1–§9** in order; **§10** only when needed. |
| D9 | **§3** baseline principles kept unless the user mandated replacement. |
| D10 | **OUTPUT_PATH** is deliverable-only: no workflow/validation prose, empty tables, or stray `[ ]`; reads as **complete AI/constitution context**. |

**Iteration rule:** If any criterion is **Fail**, revise the working copy, then re-run the full table. Repeat until **all Pass** or **3 validation iterations** have completed (counting the first run). If still **Fail** after 3 iterations, keep the best working copy and in the assistant reply list remaining **Fail** items and why (do not invent facts to force **Pass**).

### 6 — Write artifact

1. Write the final working copy to **OUTPUT_PATH** (overwrite if updating; backup only if the user asks).
2. Do **not** write a separate checklist file.

### 7 — User-facing gap report and clarification prompts

Always include the following in the assistant reply after step **6**.

1. **Design quality validation (inline)** — Output the final **D1–D10** table with **Pass/Fail**.
2. **Section coverage summary** — Table: **§1–§9**, **§10** (**Omitted** when not needed) → **Complete** / **Partial** / **Missing** / **Omitted**.
3. **Prioritized questions** — At most **3** questions. Only items that materially affect UX, accessibility, security-sensitive flows, or screen scope. **Do not pad.** If **zero** critical gaps, state that and suggest **next pipeline step**: gather **`.project/context/`** context files you intend for **constitution** (e.g. `.cursor/skills/speckit-constitution`)—typically **PRD** and **tech-stack** plus **design** when UI applies; **design** itself required only the PRD to produce.

**Question format** (per question; output all questions, then wait for one user message answering **all**):

```markdown
## Question [N]: [Topic]

**Context**: [Quote relevant fragment]

**What we need to know**: [Restate gap or `NEEDS INPUT`]

**Recommended**: [One–two sentences when reasonable]

| Option | Answer | Implications |
|--------|--------|--------------|
| A | [First suggested answer] | [Effect on UX/scope] |
| B | [Second suggested answer] | [Effect on UX/scope] |
| C | [Third suggested answer] | [Effect on UX/scope] |
| Custom | Provide your own short answer | [How to phrase it] |

**Your choice**: _Reply once with e.g. "Q1: A, Q2: recommended, Q3: Custom — …"_
```

**Table formatting:** pipes aligned, spaces around cell text (`| Content |`), header separator at least three dashes per column.

### 8 — Report completion

End the assistant reply with a compact **completion** block:

- **OUTPUT_PATH**, **PRD_PATH**
- **Counts** — flows in **§5**, screens in **§7**, `NEEDS INPUT:` markers
- **Validation** — all **Pass** or list remaining **Fail** criteria (if any after iteration cap)
- **Readiness** — user answers Q1–Q3 → merge into doc + revision row; then **constitution** using **`.project/context/*.md`** (separate skill/command)

## Output

In the assistant reply after the artifact is written:

- **Design quality validation** — final **D1–D10** table with **Pass/Fail**.
- **Section coverage** — **§1–§9**, **§10** (when applicable) as **Complete** / **Partial** / **Missing** / **Omitted**.
- **Prioritized questions** — at most **3** (or state none); use the prescribed question format when asking.
- **Completion** — **OUTPUT_PATH**, **PRD_PATH**, counts (flows, screens, `NEEDS INPUT:` markers), validation summary, readiness for merge / constitution.

## Graceful Degradation

- **Missing template** — **ERROR** with the required path; do not improvise structure.
- **Missing PRD** — **ERROR**; stop until the user runs the PRD workflow or passes `prd:…`.
- **UI scope gate fails** — **ERROR** for non-UI products; ambiguous scope → proceed with ≤3 `NEEDS INPUT:` markers and capture UI intent in **Prioritized questions**.
- **Validation stuck after 3 iterations** — keep the best working copy; list remaining **Fail** items in the reply (do not invent facts).

## General guidelines

- Do not create or switch git branches unless the user asked.
- Do not paste whole constitution or tech-stack files into the design artifact.
- Keep the written file free of workflow or validation prose (**OUTPUT_PATH** is deliverable-only).

## Constraints

- **Do not** exceed **3** prioritized clarification questions in a single invocation.
- **Do not** exceed **3** `NEEDS INPUT:` markers in the written document.
- **Do not** silently omit mandatory template **headings** for **§1–§9**; **§10** follows template *Optional* rules.
- **Do not** write a separate checklist file; the **D1–D10** table lives **only** in the assistant reply.
- **Do not** use automated feature-pipeline scripts unless the user asked to tie this artifact to an active feature branch.
