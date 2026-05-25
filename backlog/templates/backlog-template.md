# Product Backlog: [PRODUCT NAME]

**Created**: [DATE]

---

## Product description

[Short description of the product: what it is, main purpose, and key value in 2–4 sentences.]

---

## Business problem

[Clear statement of the problem or opportunity; who is affected and what outcome is expected.]

---

## Actors

[List of actors (user types, roles, or systems) that will use or interact with the product. One per line or short bullet.]

- [Actor 1]: [Brief role or description]
- [Actor 2]: [Brief role or description]

---

## Backlog

**Status legend**:

- **Milestones/Epics**: `⚪ Backlog` | `🟡 In progress` | `🔴 Blocked` | `⚪ Cancelled` | `🟢 Done`
- **Features**: `⚪ Backlog` | `🔵 Specified` | `🔵 Clarified` | `🔵 Planned` | `🔵 Tasked` | `🔵 Analyzed` | `🟢 Implemented` | `🔴 Blocked` | `⚪ Cancelled`

**Priority legend**: `High` | `Medium` | `Low`

**Hierarchy levels (per config)**:

- `milestones=true,  epics=true`  → Milestone → Epic → Feature (IDs: `M.E.F`) — *default*
- `milestones=false, epics=true`  → Epic → Feature (IDs: `E.F`)
- `milestones=true,  epics=false` → Milestone → Feature (IDs: `M.F`)
- `milestones=false, epics=false` → Flat list of Features (IDs: `F`)

Omit headings and dashboard sub-tables for levels disabled in `backlog-config.yml`. Features are always present.

---

### Project Dashboard

<!--
Layout adapts to enabled levels:

  * M+E+F : one sub-section per Milestone, each with a table grouping its Epics
            (and the Features under each Epic).
  * E+F   : a single table grouping each Epic (header row) and its Features.
  * M+F   : one sub-section per Milestone, each with a table listing its Features.
  * F     : a single flat table of Features.

The `**Status**:` and `**Priority**:` lines on every Milestone block (and the
Status/Priority cells in every table row) are owned by /speckit.backlog.update —
do not hand-edit them.
-->

#### Milestone 1: [Title]
**Status**: `⚪ Backlog`  
**Priority**: `High`  

| ID       | Name             | Status      | Priority    |
| :------- | :--------------- | :---------- | :---------- |
| **E1.1** | **[Epic Title]** | `⚪ Backlog` | **`High`** |
| 1.1.1    | [Feature Title]  | `⚪ Backlog` | `High`   |
| 1.1.2    | [Feature Title]  | `⚪ Backlog` | `Medium` |
| ---      | ---              | ---         | ---         |
| **E1.2** | **[Epic Title]** | `⚪ Backlog` | **`Medium`** |
| 1.2.1    | [Feature Title]  | `⚪ Backlog` | `Medium` |

#### Milestone 2: [Title]
**Status**: `⚪ Backlog`  
**Priority**: `Medium`  

| ID       | Name             | Status      | Priority    |
| :------- | :--------------- | :---------- | :---------- |
| **E2.1** | **[Epic Title]** | `⚪ Backlog` | **`Medium`** |
| 2.1.1    | [Feature Title]  | `⚪ Backlog` | `Medium` |

---

### Milestone 1: [Title]

**Description**: [Short description of the milestone goal and scope.]  
**Status**: Backlog  
**Priority**: High  

#### Epic 1.1: [Title]

**Description**: [Short description of the epic.]  
**Status**: Backlog  
**Priority**: High  

- **Feature 1.1.1**: [Title]  
  **Description**: [Simple, direct description of what the feature does. *Do NOT use "As a [user], I want..."*]  
  **Branch**:   
  **Status**: Backlog  
  **Priority**: High  

- **Feature 1.1.2**: [Title]  
  **Description**: [Short description.]  
  **Branch**:   
  **Status**: Backlog  
  **Priority**: Medium  

#### Epic 1.2: [Title]

**Description**: [Short description of the epic.]  
**Status**: Backlog  
**Priority**: Medium  

- **Feature 1.2.1**: [Title]  
  **Description**: [Short description.]  
  **Branch**:   
  **Status**: Backlog  
  **Priority**: Medium  

---

### Milestone 2: [Title]

**Description**: [Short description of the milestone goal and scope.]  
**Status**: Backlog  
**Priority**: Medium  

#### Epic 2.1: [Title]

**Description**: [Short description of the epic.]  
**Status**: Backlog  
**Priority**: Medium  

- **Feature 2.1.1**: [Title]  
  **Description**: [Short description.]  
  **Branch**:   
  **Status**: Backlog  
  **Priority**: Medium  

---

[Add more milestones, epics, and features as needed. Keep the nested structure: Milestone → Epic → Feature. Every item has Title, Description, Status, Priority; every Feature also has Branch.]
