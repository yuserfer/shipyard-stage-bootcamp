# Acceptance evidence: shipctl (Project 2)

Test command: `python3 -m unittest discover -s tests -v` → `Ran 15 tests … OK` (see the recorded run in deck video 02 for raw output).

| Criterion | Proof |
|---|---|
| AC1 add + incrementing ids | `AddTaskTests.test_add_assigns_incrementing_ids`, `test_new_id_follows_highest_existing_id` |
| AC2 empty title rejected | `AddTaskTests.test_empty_title_is_rejected` |
| AC3 owner, due date, invalid date | `OwnerAndDueTests.*` |
| AC4 pending by due date, undated last | `ListAndFilterTests.test_list_defaults_to_pending_sorted_by_due` |
| AC5 owner/status filters combine | `ListAndFilterTests.test_filter_by_owner`, `test_filter_by_status_done`, `test_owner_and_status_combine` |
| AC6 done/delete, unknown id exit 1 | `CompleteAndDeleteTests.*`, `OwnerAndDueTests.test_unknown_id_exits_1` |
| AC7 corrupt storage exit 2 | `StorageTests.test_corrupt_database_exits_2` |
| AC8 README documents commands | `README.md`, section "shipctl" |
