# Decision matrix: Notes API

Fixed criteria, scored 1 (poor) to 5 (excellent), then multiplied by weight. Scored before any implementation.

| Criterion (weight) | A: single module + JSON | B: layered + SQLite | C: event log |
|---|---|---|---|
| Simplicity (×2) | 5 → 10 | 4 → 8 | 2 → 4 |
| Testability (×3) | 2 → 6 | 5 → 15 | 4 → 12 |
| Security (×2) | 3 → 6 | 4 → 8 | 3 → 6 |
| Scalability (×1) | 1 → 1 | 3 → 3 | 3 → 3 |
| Maintenance (×2) | 2 → 4 | 5 → 10 | 2 → 4 |
| **Total (max 50)** | **27** | **44** | **29** |

**Winner: B.** Business rules are testable without HTTP, SQL is isolated in one module (parameterised queries only), and search/tags in Project 6 become a repository change instead of a rewrite.

**Not a hybrid.** We considered A's single-file simplicity and C's audit trail. Neither combines coherently with B today: a single file would undo the layering, and an audit trail is a separate requirement — see the log.

**Approved by:** engineer of record, before implementation.
