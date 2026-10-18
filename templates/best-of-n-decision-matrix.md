# Best-of-N Decision Matrix

> **How to use.** Fix the criteria and weights **before** you ask Claude for options. Otherwise the matrix tends to get tuned to favor whichever answer came first. Ask for N (usually 3) designs that are genuinely different, run the distinctness check, then score each option from 1 to 5 against every criterion and write one line of justification per score. Implement the winner only after the comparison is complete. Record every loser in the Rejected Options Log. The `best-of-n-decision` Skill automates the structure, but the engineer of record still owns the scores.

---

## 1. Decision

| Field | Value |
|---|---|
| Decision | `__________` |
| Date / engineer of record | `__________` |
| Constraints all options must satisfy | `__________` |

## 2. Fixed criteria and weights

The criteria are fixed. Only the weights change, and you set them before you see the options. Weights must sum to 100.

| Criterion | What a 5 looks like | Weight |
|---|---|---|
| Simplicity | Few moving parts; a new maintainer understands it in 15 minutes | `__` |
| Testability | Core logic testable in isolation, fast and deterministic | `__` |
| Security | Small attack surface; safe defaults; input validated at one boundary | `__` |
| Scalability | Handles 10x data or traffic without a redesign | `__` |
| Maintenance | Easy to change; clear responsibilities; low operational burden | `__` |
| **Total** | | **100** |

Scoring scale: **1** poor, **2** weak, **3** adequate, **4** strong, **5** excellent.

## 3. Distinctness check (do this before scoring)

Two options are cosmetic variants when they differ only in naming, file layout, or code style. Each option must differ from the others in at least one of these:

- data model or storage
- layering and responsibilities
- consistency and failure behavior
- operational model

| Option | One-line summary | Key structural difference from the others |
|---|---|---|
| A | `__________` | `__________` |
| B | `__________` | `__________` |
| C | `__________` | `__________` |

If two options are variants, ask for a replacement: "Option C is a variant of B. Propose a design that uses a different storage or consistency model."

## 4. Scores

Weighted score = sum of (score x weight) / 100. The maximum is 5.00.

| Criterion (weight) | A | B | C |
|---|---|---|---|
| Simplicity (`__`) | | | |
| Testability (`__`) | | | |
| Security (`__`) | | | |
| Scalability (`__`) | | | |
| Maintenance (`__`) | | | |
| **Weighted score** | | | |

## 5. Selection

| Field | Value |
|---|---|
| Selected option | `__________` |
| Reasoning, beyond the score | `__________` |
| Ideas borrowed from rejected options (if any) | `__________` |
| Coherence check (see below) | pass / fail |

**Avoiding an incoherent hybrid.** You may borrow an idea from a losing option only if it fits the winner's structure without adding a second architecture. Borrowing C's append-only audit table into B's repository layer is fine. Running B's SQLite store and C's event log as two sources of truth is not. Ask: "After borrowing, is there still exactly one way data is stored and one place each rule lives?" If the answer is no, do not borrow.

**Avoiding first-answer-wins.** If the first option you saw wins, confirm the scores were written per criterion before you looked at the totals. Also check that each score has a justification that does not mention the other options.

---

## Example: Shipyard, Project 4 (Notes API Design Tournament)

**Decision:** the backend design for the Notes API (CRUD notes; later search and tags). **Shared constraints:** Python 3 standard library only, JSON over HTTP, runs locally.

**Weights:** Simplicity 25, Testability 25, Security 20, Scalability 10, Maintenance 20.

| Option | Summary | Structural difference |
|---|---|---|
| A | Single module; notes stored in one JSON file, rewritten on each change | No layers; whole-file storage |
| B | Layered router -> service -> SQLite repository | Separated responsibilities; relational store |
| C | Event-sourced append-only log; current state rebuilt by replaying events | State is derived; history is the source of truth |

| Criterion (weight) | A | B | C |
|---|---|---|---|
| Simplicity (25) | 5: one file, no schema | 3: three modules, small schema | 1: event types, replay, snapshots |
| Testability (25) | 3: HTTP and storage are tangled | 5: service testable with `:memory:` repo | 4: pure reducers, but replay fixtures |
| Security (20) | 3: no SQL, but manual validation spread out | 4: validation in one layer, parameterized SQL | 3: log can retain deleted data |
| Scalability (10) | 2: whole-file rewrite, no concurrency | 4: SQLite handles workshop scale and more | 4: append-only writes scale well |
| Maintenance (20) | 2: grows into a tangle when search is added | 5: search and tags slot into repository/service | 2: schema evolution of events is hard |
| **Weighted score** | **3.20** | **4.20** | **2.65** |

**Selected:** B. It has the highest score, and Project 5 (regression tests) and Project 6 (search and tags) both depend on testable layers. **Borrowed:** nothing in v1. C's audit trail is noted as a future option in the Rejected Options Log. **Coherence check:** pass, because there is a single store.
