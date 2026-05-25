---
description: "Draft or update an AI-oriented PRD under .project/context/ (constitution pipeline step 1); prompt for missing decision-critical details."
---

# Context: PRD

## Goal

Give the repository a **PRD-style product context** under `.project/context/`: problems, users, scope, and measurable outcomes for agents and constitution—without implementation prescriptions unless the user locks a policy.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user’s natural-language message in this conversation **is** part of the input: treat it as available even when `$ARGUMENTS` appears literally empty below; only ask the user to repeat themselves if both are empty.

## Prerequisites

1. **Template** — `.specify/extensions/context/templates/prd-template.md` (mandatory; abort if missing).
2. **Default output** — `.project/context/prd.md` (generated artifacts only; not this command file).

### Paths (do first)

1. **OUTPUT_PATH** / **PRODUCT_CONTEXT** — From `out:`/`output:`/`path:` line (`*.md`) or sole repo-relative `*.md` in `$ARGUMENTS`; else **`.project/context/prd.md`**. Strip used parts; remainder + chat = **PRODUCT_CONTEXT**.
2. **Empty input** — No **PRODUCT_CONTEXT** and no product description in chat → **ERROR**, stop.
3. **Collision** — File at **OUTPUT_PATH** → stop; ask **Merge | Replace | Different path | Abort**; on **Different path**, update **OUTPUT_PATH** and repeat (3).
4. **No file** — `mkdir -p` parent.

### Update runs (merge rules)

**Merge**: load file, merge **PRODUCT_CONTEXT** (keep prior decisions unless user replaces a section). **Replace**: ignore old body; draft from template + **PRODUCT_CONTEXT**. **Revision history**: one new row per run in step **4** sub-step **1** only.

## Execution Steps

Execute the following steps **in order**. Treat earlier steps as gates: if a step **ERROR**s, stop the pipeline.

### Pre-development PRD principles

The following norms guide drafting.

1. **Why and what, not how** — Describe problems, users, outcomes, and constraints. Do not prescribe implementation (frameworks, schemas, vendor APIs) unless the user states a **hard policy** dependency; then phrase it as a constraint, not a design.
2. **Avoid solution favoritism** — Replace tech-first statements with requirement-first language (e.g. “sub-second feedback for the trader” not “use Redis”).
3. **Technically aware framing** — Capture **business-driven** boundaries engineers need (latency tolerance, throughput, consistency vs availability preferences, integration points) without designing the system.
4. **Living document** — Prefer **informed defaults** for low-impact gaps (document in §7 *Assumptions*). For high-impact unknowns, use one-line **`NEEDS INPUT: …`** markers in the draft body. **LIMIT: at most 3 `NEEDS INPUT:` markers in the entire PRD.** If more than three high-impact unknowns exist, keep only the three most critical (prioritize: scope > security/privacy > user experience > technical details); resolve the rest with reasonable defaults and record them as assumptions in §7.
5. **Quantified NFRs when stated** — If quality targets are included, use testable numbers; if unknown, keep subsection with `TBD` and ensure §7 has a follow-up row (counts toward clarity, not toward the 3-marker limit unless expressed as `NEEDS INPUT:`).
6. **Pre-development scope** — Omit GTM, marketing copy, sales enablement, and post-launch ops unless the user explicitly asks to include them.

### 1 — Parse paths, validate input, prepare output location

Run **Paths (do first)** (1)–(4). Stop on **ERROR** or unanswered collision choice.

### 2 — Context ingestion

1. **Load the template** from **`.specify/extensions/context/templates/prd-template.md`**. If the file cannot be read or is missing: **ERROR** `Cannot load PRD template at .specify/extensions/context/templates/prd-template.md` and **Stop**.
2. Preserve heading hierarchy and section order from the template exactly; replace bracket placeholders and instructional lines under each heading with real content, `TBD`, or (sparingly) `NEEDS INPUT:` per the **3-marker limit** in principles.
3. **Expand PRODUCT_CONTEXT** with any user-referenced paths (open and summarize files the user `@`-mentions or lists).
4. **Optional alignment load** — If `.specify/memory/constitution.md` exists, read it once. Use it only to:
   - inherit **default NFR posture** language for §6 when the user did not specify quality bars, and/or
   - avoid contradicting non-negotiable principles.  
   Do not copy the constitution wholesale into the PRD.

### 3 — Internal coverage map (do not show unless useful)

Build an internal checklist keyed to the template sections (§1–§7). For each subsection, assign: **Provided** / **Partial** / **Missing** based on PRODUCT_CONTEXT + loaded files.

Use this coverage checklist:

- Context & problem (summary, evidence, anti-solution bias)
- Personas & stakeholders (primary vs secondary, JTBD)
- Success metrics (KPIs measurable; OKRs if relevant)
- Scope (FRs numbered, flows/surfaces for UI, out of scope)
- NFRs (performance, security, compliance — measurable or TBD)
- Assumptions, dependencies, risks, open questions (log table)

### 4 — Draft the PRD (working copy)

**Update runs:** **Merge** → load file + merge **PRODUCT_CONTEXT** (see **Update runs (merge rules)**). **Replace** or **Greenfield** → template shell after step **2** as working copy.

Produce the full PRD markdown (working copy; do not write to disk until step **6**).

1. Set **§1** — `Status`: default `Draft`. `Last updated`: today’s date (ISO `YYYY-MM-DD`). Append **exactly one** **Revision history** row for this invocation: greenfield → `Initial draft from context`; update → short summary of what **PRODUCT_CONTEXT** changed (do **not** append a revision row in **Update runs (merge rules)**—only here).
2. Set title line **Product Requirements Document for [PRODUCT NAME]** using the best clear name from context; if unknown, use a descriptive working title and mark `NEEDS INPUT: official product name` **once** in §1 or §2 if it is among the ≤3 markers (not in the H1 if it would read nonsense—use `TBD` in H1 only when unavoidable).
3. Fill **§2–§7** from context. Use:
   - **Reasonable defaults** for low-impact details (document them in §7 as *Assumption* rows).
   - **`TBD`** where impact is moderate and §7 can track follow-up without blocking decisions.
   - **`NEEDS INPUT: …`** only where a choice materially affects scope, compliance, security, UX, or success metrics—and **never more than 3** such markers in the full document.
4. **Functional requirements** — Use sequential IDs `FR-001`, `FR-002`, … Each MUST be testable (“System MUST … / User MUST be able to …”). Merge duplicates.
5. **Optional subsections** — Omit entirely only when the template marks them *Optional* **and** context clearly excludes them (e.g. skip **Key flows & surfaces** for a headless API if user said no UI). Otherwise include with `TBD` or brief honest placeholder.
6. **§7 log** — Every `NEEDS INPUT:` in the body MUST have a matching **question** or **risk** row. Every material `TBD` SHOULD have a §7 row where someone must act (owner `TBD` allowed in draft).

### 5 — PRD quality validation (inline only; no separate checklist file)

Run validation against the working copy. For each criterion assign **Pass** or **Fail**; on **Fail**, note one concrete issue (quote a short fragment or cite §). Intermediate passes may stay **internal**; the **user-facing** **V1–V9** table is mandatory in step **7** (after writing the file).

| # | Criterion |
|---|-----------|
| V1 | No implementation leakage (languages, frameworks, vendor products) unless user-mandated as policy; otherwise requirement-first wording. |
| V2 | No vague NFRs as “fast”/“secure” without numbers, explicit `TBD`, or §7 follow-up. |
| V3 | §2 has a real **problem statement** (not only a solution pitch). |
| V4 | At least one numbered FR in the scope section (template §5 or equivalent). |
| V5 | At least one KPI/metric or explicit `TBD` with §7 follow-up in success metrics (template §4 or equivalent). |
| V6 | Scope bounded: in-scope vs out-of-scope clear or honestly `TBD` with §7. |
| V7 | `NEEDS INPUT:` ≤ **3**; each has a §7 row. |
| V8 | Mandatory template headings present in order; none silently omitted. |
| V9 | **OUTPUT_PATH** is deliverable-only: no workflow/validation prose, no bare `[ ]`, no empty shells; reads as **complete AI/constitution context**. |

**Iteration rule:** If any criterion is **Fail**, revise the working copy, then re-run the full table. Repeat until **all Pass** or **3 validation iterations** have completed (counting the first run). If still **Fail** after 3 iterations, keep the best working copy and in the assistant reply list remaining **Fail** items and why (do not invent facts to force **Pass**).

### 6 — Write artifact

1. Write the final working copy to **OUTPUT_PATH** (overwrite if updating; keep a backup only if the user asks).
2. Do **not** write any separate checklist file for this workflow.

### 7 — User-facing gap report and clarification prompts

Always include the following in the assistant reply after step **6**.

1. **PRD quality validation (inline)** — Output the final **V1–V9** table with **Pass/Fail** (last iteration).
2. **Section coverage summary** — Table: each template top-level section (§1–§7) → **Complete** / **Partial** / **Missing**.
3. **Prioritized questions** — At most **3** questions. Include only items that **materially** affect scope, compliance, security, acceptance, or prioritization. Do not ask about stylistic preferences. **Do not pad:** if fewer than three critical gaps exist, output only those. If **zero** critical gaps, state that and suggest **next pipeline step**: run **`/speckit.context.tech-stack`** (PRD + any constraints); **if** the product has **user-facing UI**, run **`/speckit.context.design`** (uses **PRD + user input only**, not the tech-stack file)—before or after tech-stack as the user prefers; when the context files you need are ready, use them for **constitution** (e.g. `.cursor/skills/speckit-constitution`).

**Question format** (per question; match structure for all questions, then wait for one user message answering **all**):

```markdown
## Question [N]: [Topic]

**Context**: [Quote relevant PRD fragment]

**What we need to know**: [Restate the `NEEDS INPUT` or gap]

**Recommended**: [One–two sentences when a default is reasonable]

| Option | Answer | Implications |
|--------|--------|--------------|
| A | [First suggested answer] | [Effect on scope/outcomes] |
| B | [Second suggested answer] | [Effect on scope/outcomes] |
| C | [Third suggested answer] | [Effect on scope/outcomes] |
| Custom | Provide your own short answer | [How to phrase it] |

**Your choice**: _Reply once with e.g. "Q1: A, Q2: recommended, Q3: Custom — …"_
```

**Table formatting:** pipes aligned, spaces around cell text (`| Content |`), header separator at least three dashes per column.

### 8 — Report completion

End the assistant reply with a compact **completion** block:

- **OUTPUT_PATH** — final path written
- **Counts** — `NEEDS INPUT:` markers in file, approximate `TBD` count, FR count
- **Validation** — all **Pass** or list remaining **Fail** criteria (if any after iteration cap)
- **Readiness** — e.g. user answers Q1–Q3 → merge into PRD and append revision history; then **tech-stack** with this PRD as source; **if** UI applies, **`/speckit.context.design`** may follow (PRD + user input only, independent of tech-stack); constitution is a **separate** step using **`.project/context/*.md`**

## Output

In the assistant reply after the artifact is written:

- **PRD quality validation** — final **V1–V9** table with **Pass/Fail**.
- **Section coverage** — each template top-level section (§1–§7) as **Complete** / **Partial** / **Missing**.
- **Prioritized questions** — at most **3** (or state none); use the prescribed question format when asking.
- **Completion** — **OUTPUT_PATH**, counts (`NEEDS INPUT:`, `TBD`, FRs), validation summary, readiness for tech-stack / design / constitution.

## Graceful Degradation

- **Missing template** — **ERROR** with the required path; do not improvise structure.
- **Empty product context** — **ERROR**; stop until the user supplies a description, notes, or `@` files (see **Paths**).
- **Validation stuck after 3 iterations** — keep the best working copy; list remaining **Fail** criteria (do not invent facts).

## General guidelines

- Do not create or switch git branches unless the user asked.
- Do not tie to feature-pipeline scripts unless the user requested that scope.
- Keep the written PRD free of workflow or validation prose in the artifact body.

## Constraints

- **Do not** exceed **3** prioritized clarification questions in a single invocation (follow-up turns may ask more after answers are integrated).
- **Do not** exceed **3** `NEEDS INPUT:` markers in the written PRD.
- **Do not** silently omit template **headings**; optional *content* subsections may be omitted per template rules.
- **Do not** write a separate checklist file for PRD quality validation; the **V1–V9** table lives **only** in the assistant reply.
- **Do not** use automated feature-pipeline scripts (`check-prerequisites.sh`, `FEATURE_SPEC`) unless the user asked to tie this PRD to an active feature; this workflow is **context-document** scoped.
