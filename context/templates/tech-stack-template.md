# Technology stack for [PRODUCT OR SYSTEM NAME]

**Audience & use**: This file is **machine-oriented context** for AI implementation and for drafting the **project constitution** (e.g. speckit-constitution). Optimize for **clear constraints, versions, and verification** (see §8).

Use only sections that apply. Omit **§6** when no domain has two comparable options; omit **§9** when there are no `NEEDS INPUT:` markers. Subsections marked *Optional* may be omitted when they add no decision value.

---

## 1. Document control

**Status**: [Draft | Review | Approved | …]  
**Last updated**: [YYYY-MM-DD]  
**Source PRD**: [path]

### Revision history

| Date | Author | Summary of change |
| ---- | ------ | ----------------- |
| [ ]  | [ ]    | [ ]               |

---

## 2. Project context (from PRD)

### PRD reference

**PRD used**: [path]

### Summary from PRD

[What matters from the PRD for technical direction—avoid duplicating the full PRD.]

### Product basics

| Field | Value |
| ----- | ----- |
| Project type | [ ] |
| Main business goal | [ ] |
| Target users | [ ] |
| MVP vs long-term | [ ] |
| Existing system vs greenfield | [ ] |

---

## 3. Tech stack summary

### Executive overview

[3–6 sentences: product fit, deployment shape, primary languages/frameworks, data, auth, integrations at a glance.]

### Highlights *(Optional)*

- [Key choice and why it matters.]
- [ … ]

---

## 4. Security principles

*Ground in PRD security, privacy, and compliance expectations; keep **§5** domain choices (especially Authentication, Backend, Infrastructure / hosting, Integrations / APIs) consistent with this section.*

### Posture summary

[2–4 sentences: trust boundaries, sensitivity of data handled, and how the stack defaults toward least privilege.]

### Principles and stack alignment

| Principle | How the selected stack supports it |
| --------- | ---------------------------------- |
| Authentication & authorization | [ ] |
| Data protection (at rest / in transit) | [ ] |
| Secrets & key material | [ ] |
| Dependencies, supply chain, third parties | [ ] |
| Logging, monitoring, and sensitive data | [ ] |

### Compliance or assurance targets *(Optional)*

[Regimes, certifications, or internal bars from the PRD—otherwise `TBD` or omit.]

---

## 5. Proposed stack by decision domain

### [Domain name]

**Recommendation**: [One line.]

| Concern | Choice | Version / notes |
| ------- | ------ | ----------------- |
| [ ]     | [ ]    | [ ]               |

---

## 6. Options evaluation by domain *(Optional)*

*Omit this whole section when no domain has two comparable options.*

### [Domain name]

**Candidates**

| Code | Technology | Role in this domain |
| ---- | ---------- | ------------------- |
| A    | [ ]        | [ ]                 |
| B    | [ ]        | [ ]                 |

**Comparison**

| Criterion | A | B |
| --------- | - | - |
| Pros | [ ] | [ ] |
| Cons | [ ] | [ ] |
| Complexity (H/M/L) | [ ] | [ ] |
| Cost (H/M/L or model) | [ ] | [ ] |
| Scalability fit | [ ] | [ ] |
| Team fit | [ ] | [ ] |

**Simple scorecard**

| Criterion | A | B |
| --------- | - | - |
| Fast to build | [ ] | [ ] |
| Easy to maintain | [ ] | [ ] |
| Scalable | [ ] | [ ] |
| Cost-effective | [ ] | [ ] |

**Selected for this domain**: [A or B]  
**Why**: [ ]

---

## 7. Final recommendation

### Selected stack (consolidated)

| Domain | Selected technology / approach |
| ------ | ------------------------------ |
| [ ]    | [ ]                            |

### Why this stack

[Narrative tying choices to the PRD, the §3 summary, §4 security posture, §5 domain picks, §6 evaluations where §6 exists, and how the stack supports verification when coding with an agent (§8).]

### Risks and tradeoffs

| Risk / tradeoff | Mitigation or acceptance |
| ----------------- | ------------------------ |
| [ ]               | [ ]                      |

### Future upgrade path

- [Milestone or trigger] → [technology or pattern change]
- [ … ]

---

## 8. Test approach

*Written for teams using a coding agent: what to run locally, what CI enforces, and what people still check.*

- **Agent checks** (commands or suites to run or extend when the agent implements or refactors—e.g. unit, integration, E2E, lint, typecheck, security scans where applicable; tie to **§5**/**§7** tools): [ ]
- **CI gates** (what must pass on PR or before release so high-churn agent edits cannot merge unchecked): [ ]
- **Human / follow-up** (review focus, smoke paths, staging or UAT—omit bullet if nothing meaningful beyond automation): [ ]

---

## 9. Open items *(Optional)*

*If truly none: remove this section or write “None at time of writing” rather than leaving an empty list.*

- [ … ]
