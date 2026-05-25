# Design document for [PRODUCT NAME]

**Audience & use**: This file is **machine-oriented context** for AI agents building UI/UX and for drafting the **project constitution** (e.g. speckit-constitution). Prefer **flows, IA, screen lists, and accessibility targets** over marketing copy.

Use only sections that apply. Omit **§10** when there are no open questions. Subsections marked *Optional* may be omitted when they add no decision value.

---

## 1. Document control

**Status**: [Draft | Review | Approved | …]  
**Last updated**: [YYYY-MM-DD]  
**Source PRD**: [path]

### Revision history

| Date | Author | Summary of change |
| ---- | ------ | ------------------- |
| [ ]  | [ ]    | [ ]                 |

---

## 2. Context (from PRD)

### PRD reference

**PRD used**: [path]

### Summary for design

[What matters from the PRD for UX, flows, and surfaces—avoid duplicating the full PRD.]

### Product basics

| Field | Value |
| ----- | ----- |
| Project type | [ ] |
| Main business goal | [ ] |
| Target users | [ ] |
| MVP vs long-term | [ ] |
| Existing system vs greenfield | [ ] |

---

## 3. Product design principles

*Baseline principles for this product; add initiative- or release-specific nuance in **§4**.*

### 1. Clarity Over Cleverness

Prefer straightforward implementations and UI that users can parse at a glance. Choose obvious patterns in code and interface over clever abstractions, novelty for its own sake, or “impressive” but hard-to-follow solutions.

### 2. Minimize User Effort

When designing or building flows, favor the shortest path to the user’s goal: sensible defaults, fewer required fields and decisions, and consolidation of steps where it does not obscure intent. Avoid gratuitous confirmation or redundant navigation.

### 3. Consistency Creates Trust

Align new work with existing layouts, terminology, interaction patterns, and code conventions in the project. Reuse established patterns unless the spec explicitly requires a deliberate break for a documented reason.

### 4. Performance Is Part of UX

Treat responsiveness as a requirement, not polish: avoid unnecessary re-renders and heavy synchronous work on critical paths; use appropriate loading and empty states; consider pagination, virtualization, or chunking for large lists and assets.

### 5. Accessibility Is Default

Implement features so they work with keyboard navigation, screen readers, and zoom: semantic structure, labels for controls, focus order, contrast-sensitive choices, and motion alternatives where relevant. Do not defer accessibility to a later pass unless the user explicitly scopes that out.

### 6. Every Screen Needs a Clear Primary Action

For each view or modal, make the main next step obvious in hierarchy, copy, and layout—typically one primary control. Secondary actions should read as secondary; avoid ambiguous or competing primary calls to action.

### 7. Design Systems Over One-Off Solutions

Extend shared components, tokens, and patterns from the codebase or design system before introducing custom UI. If you must diverge, isolate the exception and document why it cannot use the shared pattern.

### 8. Trust Must Never Be Compromised

Implement honest copy, predictable behavior, and safe handling of data and permissions. Avoid dark patterns, misleading defaults, hidden costs, or “gotcha” flows. Surface errors and limitations clearly instead of masking them.

---

## 4. Product-specific design principles

### 1. [Principle title]

[What this means for this initiative, feature, or release—constraints, tradeoffs, or priorities that extend or narrow the principles in **§3**.]

### 2. [Principle title]

[Short rationale and how it shows up in decisions or reviews.]

---

## 5. User flows

### [Flow name]

1. [Step]
2. [Step]

*(Add diagrams or links when available.)*

---

## 6. Information architecture

| Area / section | Purpose | Key entities |
| -------------- | ------- | ------------ |
| [ ]            | [ ]     | [ ]          |

---

## 7. Key screens / surfaces

| Screen / surface | Primary user goal | Notes |
| ---------------- | ----------------- | ----- |
| [ ]              | [ ]               | [ ]   |

---

## 8. Visual and interaction

### Brand / tone

[ ]

### Typography

[ ]

### Color

[ ]

### Components / design system

[ ]

---

## 9. Accessibility

### Targets

[e.g. WCAG level, policy requirements, supported clients.]

### Keyboard, screen reader, and focus

[ ]

---

## 10. Open questions *(Optional)*

*If truly none: remove this section or write “None at time of writing” rather than leaving an empty list.*

- [ … ]
