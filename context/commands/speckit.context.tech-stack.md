---
description: "Produce or update AI-oriented tech stack context under .project/context/ (constitution pipeline step 2); PRD-first, security principles, options where tradeoffs matter, prompts for decisions."
---

# Context: Tech stack

## Goal

Give the repository a **technology stack context** under `.project/context/`: PRD-first, **explicit security posture**, decision-dense, and honest about tradeoffs—so agents and constitution share one stack story without option bloat or stack docs inventing product scope.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input: treat it as available even when `$ARGUMENTS` appears literally empty below; only ask the user to repeat themselves if both are empty.

## Prerequisites

1. **Template** — `.specify/extensions/context/templates/tech-stack-template.md` (mandatory; abort if missing).
2. **Default output** — `.project/context/tech-stack.md`.

### Paths (do first)

1. **OUTPUT_PATH** / **WORK_CONTEXT** — From `out:`/`output:`/`path:` line (`*.md`) or sole repo-relative `*.md` in `$ARGUMENTS`; else **`.project/context/tech-stack.md`**. Strip used parts; remainder + chat = **WORK_CONTEXT**.
2. **PRD_PATH** + load — `prd:` or `@` PRD `.md` → else **`.project/context/prd.md`** if it exists → else **ERROR**, stop. Load PRD. **WORK_CONTEXT** and chat empty → need enough PRD for **§2**–**§4** (incl. security posture); else **ERROR**, stop.
3. **Collision** — File at **OUTPUT_PATH** → stop; ask **Merge | Replace | Different path | Abort**; on **Different path**, update **OUTPUT_PATH** and repeat (3).
4. **No file** — `mkdir -p` parent.

## Update runs (merge rules)

**Merge**: load file, merge **WORK_CONTEXT** + PRD. **Replace**: template + **WORK_CONTEXT** + PRD only. **Revision history**: one new row in **§1** per run only.

## Execution Steps

Execute the following steps **in order**. Treat earlier steps as gates: if a step **ERROR**s, stop the pipeline.

### Tech stack principles

1. **PRD-first** — Project context, security posture, and stack direction trace to **PRD_PATH**; do not contradict the PRD unless **WORK_CONTEXT** explicitly overrides (then note the override in **§2** or **§7**).
2. **Summary before detail** — **§3** states the headline stack in plain language; **§4**–**§5** and **§7** *Selected stack (consolidated)* must agree (no named technology in **§3** that contradicts **§5**/**§7** or **§4** security claims). Avoid prestige picks without a PRD hook.
3. **Omit irrelevant domains** — Use **only** decision domains that matter for this product (see step **4** list). **Do not** include empty domain headings, “N/A” rows, or explanatory text about what you skipped.
4. **Living document** — Prefer informed defaults for low-impact gaps (document under **§7** *Risks and tradeoffs* / *Future upgrade path*). For high-impact unknowns, at most **3** `NEEDS INPUT:` markers in the entire document (prioritize: security/compliance > cost/capex > scalability/team fit > minor tooling).
5. **Options only when they matter** — A domain appears in **§6** only when there are **exactly two** defensible, **meaningfully different** options and the tradeoff matters. If a domain has **only one** reasonable option, document it in **§5** (and **§7**) and **do not** include that domain in **§6**—**no** one-candidate subsections and **no** commentary that options were skipped.
6. **Two candidates or nothing** — When a **§6** subsection exists for a domain, it must name **exactly two** options (A/B). **Never** add a third candidate, “honorable mention,” or filler. If **no** domain in the artifact has two options to compare, **omit the entire §6** (including the `## 6` heading).
7. **Scoring is comparative** — When **§6** compares two candidates, use the **same** scale for both (e.g. 1–5 or H/M/L) and keep scores explainable in prose.

### 1 — Parse paths, validate input, prepare output location

Run **Paths (do first)** (1)–(4). Stop on **ERROR** or unanswered collision choice.

### 2 — Context ingestion

1. **Load the template** from **`.specify/extensions/context/templates/tech-stack-template.md`**. If the file cannot be read or is missing: **ERROR** `Cannot load tech stack template at .specify/extensions/context/templates/tech-stack-template.md` and **Stop**.
2. **Load the PRD** from **PRD_PATH**; summarize and cite sections/FR/NFR IDs where helpful.
3. Expand **WORK_CONTEXT** with any user-referenced paths (open and summarize files the user `@`-mentions or lists).
4. **Optional** — If `.specify/memory/constitution.md` exists, read it once for non-negotiable engineering and **security** principles; do not paste it wholesale into the tech-stack doc.

### 3 — Internal coverage map (do not show unless useful)

Assign **Provided** / **Partial** / **Missing** for:

- **§1** document control and revision history
- **§2** PRD-sourced project context (type, goal, users, MVP vs long-term, greenfield vs existing)
- **§3** tech stack summary (executive clarity, consistency with PRD)
- **§4** security principles (posture, PRD alignment, consistency with **§5**/**§7**)
- Each **decision domain** you expect to include in **§5** (from the list in step **4**)
- Which domains warrant a **§6** two-option evaluation vs a single clear choice in **§5** only
- **§7** final recommendation, risks, upgrade path
- **§8** test approach (AI agent: local checks, CI, human follow-up)
- **§9** open items (only if `NEEDS INPUT:`)

### 4 — Draft the tech stack (working copy)

**Update runs:** **Merge** → load + merge **WORK_CONTEXT** / PRD (see **Update runs (merge rules)**). **Replace** or **Greenfield** → template shell after step **2** as working copy.

Produce the full markdown (working copy; do not write to disk until step **6**).

1. **§1 — Document control** — **Status** default `Draft`, **Last updated** today (ISO), **Source PRD** → **PRD_PATH**. Under **### Revision history**, append **exactly one** row for this invocation: greenfield → `Initial draft from PRD + context`; update → short summary of what changed (do **not** append revision rows outside **§1**).

2. **§2 — Project context (from PRD)** — **### PRD reference** with **PRD used** path; **### Summary from PRD**; **### Product basics** table (project type, main business goal, target users, MVP vs long-term, existing vs greenfield). Use PRD evidence; `NEEDS INPUT:` sparingly (≤3 in whole doc).

3. **§3 — Tech stack summary** — **### Executive overview** (3–6 sentences); optional **### Highlights** (≤~8 bullets). Ground in PRD; do **not** duplicate **§5** tables; stay consistent with **§5** and **§7** *Selected stack* as you draft.

4. **§4 — Security principles** — **### Posture summary** (2–4 sentences: trust boundaries, data sensitivity, default toward least privilege). **### Principles and stack alignment**: fill rows from PRD security, privacy, compliance, and product risk; keep claims **consistent** with **§5** (revise **§4** or **§5** if a conflict appears before finalizing). Optional **### Compliance or assurance targets** from the PRD, or `TBD` / omit when not applicable.

5. **§5 — Proposed stack by decision domain** — Use **only** `###` headings from this canonical list when that domain **applies**; otherwise **omit** the heading entirely (no comment):

   - Core (languages, runtimes, core libraries)
   - Frontend
   - Backend
   - Database
   - CMS
   - Infrastructure / hosting
   - Authentication
   - DevOps / CI-CD
   - AI services
   - Analytics
   - Monitoring / logging
   - Search
   - Storage / files
   - Integrations / APIs

   Under each included domain: one-line **Recommendation** plus the **Concern / Choice / Version** table (per template).

6. **§6 — Options evaluation (selective)** — If **no** domain has two viable options, **omit §6 entirely** (no `## 6` heading). If **one** or more qualify, **§6** contains only those `###` subsections—each with **exactly two** candidates (A/B), comparison, scorecard, **Selected** + **Why**. Single-option domains: **§5** + **§7** only, **not** **§6**.

7. **§7 — Final recommendation** — **### Selected stack (consolidated)** table; **### Why this stack** (tie to PRD, **§3**, **§4**, **§5**, **§6** where **§6** exists, and how **§8** keeps AI-assisted work safe on this stack); **### Risks and tradeoffs**; **### Future upgrade path**.

8. **§8 — Test approach** — **Always include** the three template bullets (**Agent checks**, **CI gates**, **Human / follow-up**), written for **coding-agent workflows**: concrete commands or suites from **§5**/**§7** (incl. lint, typecheck, **security scans** where the stack supports them), what CI blocks merges without, and what humans still verify. Omit the third bullet only when there is no meaningful human or follow-up scope.

9. **§9 — Open items** — Include **only** when `NEEDS INPUT:` markers exist (bulleted); otherwise **omit entire §9** (including `## 9`).

10. **Deliverable hygiene** — Finished document for **agent consumption**, not a human worksheet: keep the **PRD-style** opening applicability paragraph from the template if present (single block at top, same role as in `prd-template.md`); **no** other reader-facing fill instructions; every `###` under **§5** / **§6** is a real domain name; **no** bare `[ ]` cells—replace or delete rows; **no** workflow or validation prose in the file; **no** canonical-domain bullet list pasted into the artifact; **H1** must be `# Technology stack for [real product name]` (replace placeholder). Do **not** emit `## 6` or `## 9` as empty shells.

### 5 — Tech stack quality validation (inline only; no separate checklist file)

Run validation against the working copy. For each criterion assign **Pass** or **Fail**; on **Fail**, note one concrete issue (quote a short fragment or cite §). Intermediate passes may stay **internal**; the **user-facing** **V1–V9** table is mandatory in step **7** (after writing the file).

| # | Criterion |
|---|-----------|
| V1 | **PRD_PATH** in **§1** and/or **§2**; **§2** grounded in the loaded PRD (no fabricated product). |
| V2 | **§3** substantive, PRD-grounded, and **consistent** with **§5** and **§7** *Selected stack* (no contradicting names or roles). |
| V3 | **§4** substantive and PRD-grounded; **§5** lists **only** applicable canonical domains with no empty filler; **§4** does not contradict **§5** or **§7**. |
| V4 | **§6** (if present): only domains with **two** defensible A/B options; each subsection ⊂ **§5**; comparison, scorecard, selection; **same** score scale for both candidates. If no domain qualifies, **§6** is **fully omitted** (no empty `## 6`). |
| V5 | **§7** includes **Selected stack**, **Why this stack**, **Risks and tradeoffs**, **Future upgrade path**; *Why* ties PRD + **§3**–**§6** (if any) + **§8**; risks/upgrade are substantive, not generic boilerplate. |
| V6 | **§5** picks align with **§7** consolidated table; version or “current as of” notes where material. |
| V7 | `NEEDS INPUT:` ≤ **3**; each has a **§9** bullet when present; **§9** absent when there are **zero** markers. |
| V8 | **§1–§5**, **§7**, **§8** present in order; **§6** only before **§7** when it has qualifying subsections; **§8** **Agent checks** and **CI gates** have real content. |
| V9 | **OUTPUT_PATH** is deliverable-only: no workflow/validation prose beyond the allowed opening block, no pasted canonical-domain lists, no placeholder headings or stray `[ ]`; reads as **complete AI/constitution context**. |

**Iteration rule:** If any criterion is **Fail**, revise the working copy, then re-run the full table. Repeat until **all Pass** or **3 validation iterations** have completed (counting the first run). If still **Fail** after 3 iterations, keep the best working copy and in the assistant reply list remaining **Fail** items and why (do not invent facts to force **Pass**).

### 6 — Write artifact

1. Apply **deliverable hygiene** again if the last validation pass changed content, then write the final working copy to **OUTPUT_PATH** (overwrite if updating; keep a backup only if the user asks).
2. Do **not** write a separate checklist file for this workflow.

### 7 — User-facing gap report and clarification prompts

Always include the following in the assistant reply after step **6**.

1. **Tech stack quality validation (inline)** — Output the final **V1–V9** table with **Pass/Fail** (last iteration).
2. **Section coverage summary** — Table: **§1** (document control), **§2** (project context), **§3** (summary), **§4** (security principles), **§5** (stack by domain), **§6** (**Omitted** when no contested domains—whole `## 6` absent), **§7** (final), **§8** (test approach, AI-assisted dev), **§9** (**Omitted** when no `NEEDS INPUT:`) → **Complete** / **Partial** / **Missing** / **Omitted** (§6 and §9 only).
3. **Prioritized questions** — At most **3** questions. Only items that materially affect stack, security, compliance, cost, or scalability. **Do not pad.** If **zero** critical gaps, state that and suggest **next pipeline step**: if the product has **user-facing UI**, run **`/speckit.context.design`** (PRD + user input only; does **not** require this tech-stack file); when **`.project/context/prd.md`**, **`.project/context/tech-stack.md`**, and **`design.md`** (if UI) are ready as needed, proceed to **constitution** using those paths as sources.

**Question format** (per question; output all questions, then wait for one user message answering **all**):

```markdown
## Question [N]: [Topic]

**Context**: [Quote relevant fragment]

**What we need to know**: [Restate gap or `NEEDS INPUT`]

**Recommended**: [One–two sentences when reasonable]

| Option | Answer | Implications |
|--------|--------|--------------|
| A | [First suggested answer] | [Effect on stack / risk] |
| B | [Second suggested answer] | [Effect on stack / risk] |
| C | [Third suggested answer] | [Effect on stack / risk] |
| Custom | Provide your own short answer | [How to phrase it] |

**Your choice**: _Reply once with e.g. "Q1: A, Q2: recommended, Q3: Custom — …"_
```

**Table formatting:** pipes aligned, spaces around cell text (`| Content |`), header separator at least three dashes per column.

### 8 — Report completion

End the assistant reply with a compact **completion** block:

- **OUTPUT_PATH**, **PRD_PATH**
- **Counts** — domains in **§5**, domains with **§6** two-option evaluation, `NEEDS INPUT:` markers
- **Validation** — all **Pass** or list remaining **Fail** criteria (if any after iteration cap)
- **Readiness** — e.g. user answers Q1–Q3 → merge into doc + revision row; **if** UI applies, run **`/speckit.context.design`** when desired (PRD + user input only; **not** blocked on this tech-stack file); then **constitution** with **`.project/context/*.md`** as appropriate (separate command/skill)

## Output

In the assistant reply after the artifact is written:

- **Tech stack quality validation** — final **V1–V9** table with **Pass/Fail**.
- **Section coverage** — **§1** (document control), **§2** (project context), **§3** (summary), **§4** (security principles), **§5** (stack), **§6** (**Omitted** when no contested domains), **§7** (final), **§8** (test approach), **§9** (**Omitted** when no `NEEDS INPUT:`) → **Complete** / **Partial** / **Missing** / **Omitted** as applicable.
- **Prioritized questions** — at most **3** (or state none); use the prescribed question format when asking.
- **Completion** — **OUTPUT_PATH**, **PRD_PATH**, counts (domains, §6 evaluations, `NEEDS INPUT:`), validation summary, readiness for design / constitution.

## Graceful Degradation

- **Missing template** — **ERROR** with the required path; do not improvise structure.
- **Missing PRD** — **ERROR**; stop until the user points to a PRD or runs the PRD workflow.
- **Validation stuck after 3 iterations** — keep the best working copy; list remaining **Fail** items (do not invent facts).

## General guidelines

- Do not create or switch git branches unless the user asked.
- Do not emit empty **§6** / **§9** shells or instructional residue in **OUTPUT_PATH** beyond the allowed PRD-style opening paragraph.

## Constraints

- **Do not** exceed **3** prioritized clarification questions in a single invocation.
- **Do not** exceed **3** `NEEDS INPUT:` markers in the written document.
- **Do not** silently omit mandatory template **headings** for **§1–§5**, **§7**, and **§8**; optional **§6** / **§9** and optional *domains* follow template *Optional* rules.
- **Do not** add **§6** content for a domain that has **only one** reasonable option; **do not** emit an empty **§6** or `## 6` with no qualifying subsections. **Do not** add more than **two** candidate technologies per domain in **§6**.
- **Do not** write a separate checklist file; the **V1–V9** table lives **only** in the assistant reply.
- **Do not** leave stray instructional prose (beyond the PRD-style opening paragraph), workflow copy-paste, unfilled placeholder headings, stray literal `[ ]` tokens, or empty **§9** in **OUTPUT_PATH**; the file must be **complete and scannable for an AI** building the product or drafting a constitution from it.
- **Do not** use automated feature-pipeline scripts unless the user asked to tie this artifact to an active feature branch.
