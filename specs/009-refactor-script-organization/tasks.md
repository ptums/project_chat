# Tasks: Refactor Script Organization

**Input**: Design documents from `/specs/009-refactor-script-organization/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Manual verification only (as per project standards)

**Organization**: Tasks are grouped by requirement to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which requirement this task belongs to (e.g., R1, R2, R3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare for file moves and path updates

- [X] T001 Verify all files exist in current locations before moving
- [X] T002 [P] Verify scripts/ directory exists, create if needed
- [X] T003 [P] Create tools/ directory for audit tools

---

## Phase 2: Requirement 1 - Move Scripts to scripts/ Directory (Priority: P1) 🎯 MVP

**Goal**: Consolidate utility scripts into scripts/ directory for better organization

**Independent Test**: Verify all 7 scripts are in scripts/ directory and can be executed from there

### Implementation for Requirement 1

- [X] T004 [P] [R1] Move backfill_embeddings.py from root to scripts/backfill_embeddings.py
- [X] T005 [P] [R1] Move backup_db.py from root to scripts/backup_db.py
- [X] T006 [P] [R1] Move fix_invalid_projects.py from root to scripts/fix_invalid_projects.py
- [X] T007 [P] [R1] Move import_chatgpt_from_zip.py from root to scripts/import_chatgpt_from_zip.py
- [X] T008 [P] [R1] Move reindex_conversations.py from root to scripts/reindex_conversations.py
- [X] T009 [P] [R1] Move setup_dev.py from root to scripts/setup_dev.py
- [X] T010 [P] [R1] Move setup_prod_conversation_index.py from root to scripts/setup_prod_conversation_index.py
- [X] T011 [R1] Verify all moved scripts execute correctly from scripts/ directory

**Checkpoint**: At this point, Requirement 1 should be complete with all scripts in scripts/ directory

---

## Phase 3: Requirement 2 - Create tools/ Directory (Priority: P1) 🎯 MVP

**Goal**: Separate audit/maintenance tools from utility scripts

**Independent Test**: Verify audit_conversations.py is in tools/ directory and can be executed from there

### Implementation for Requirement 2

- [X] T012 [R2] Move audit_conversations.py from root to tools/audit_conversations.py
- [X] T013 [R2] Verify audit_conversations.py executes correctly from tools/ directory

**Checkpoint**: At this point, Requirement 2 should be complete with audit tool in tools/ directory

---

## Phase 4: Requirement 3 - Update Repos Directory References (Priority: P1) 🎯 MVP

**Goal**: Update all code references to use new ../repos/ path instead of repos/

**Independent Test**: Verify no references to repos/ remain (except in comments/docs), and code works with ../repos/ path

### Implementation for Requirement 3

- [X] T014 [P] [R3] Update help text in scripts/index_thn_code.py line 44: change repos/ to ../repos/
- [X] T015 [P] [R3] Update METADATA_DIR in brain_core/thn_code_indexer.py line 33: change Path("repos/.metadata") to Path("../repos/.metadata")
- [X] T016 [P] [R3] Update target_dir default in brain_core/thn_code_indexer.py line 36: change "repos" to "../repos"
- [X] T017 [R3] Verify all path references updated correctly using grep
- [X] T018 [R3] Test that code indexing still works with new path references

**Checkpoint**: At this point, Requirement 3 should be complete with all path references updated

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [X] T019 [P] Verify all files are in correct locations (scripts/ and tools/)
- [X] T020 [P] Run grep to confirm no remaining repos/ references in code (except documentation)
- [X] T021 [P] Test execution of moved scripts to ensure functionality preserved
- [X] T022 [P] Test execution of moved audit tool to ensure functionality preserved
- [X] T023 [P] Verify git status shows all moves correctly tracked
- [X] T024 Run quickstart.md validation scenarios
- [X] T025 Update any documentation that references old file locations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Requirement 1 (Phase 2)**: Depends on Setup completion - can proceed independently
- **Requirement 2 (Phase 3)**: Depends on Setup completion - can proceed independently
- **Requirement 3 (Phase 4)**: Can proceed independently, but should verify after moves complete
- **Polish (Phase 5)**: Depends on all requirements being complete

### Requirement Dependencies

- **Requirement 1 (P1)**: Can start after Setup (Phase 1) - No dependencies on other requirements
- **Requirement 2 (P1)**: Can start after Setup (Phase 1) - No dependencies on other requirements
- **Requirement 3 (P1)**: Can start after Setup (Phase 1) - No dependencies on other requirements, but should verify after file moves

### Within Each Requirement

- File moves before verification
- Path updates before testing
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All file moves in Requirement 1 marked [P] can run in parallel (different files)
- All path updates in Requirement 3 marked [P] can run in parallel (different files)
- All Polish tasks marked [P] can run in parallel
- Requirements 1, 2, and 3 can be worked on in parallel by different team members

---

## Parallel Example: Requirement 1

```bash
# All file moves can be done in parallel:
Task: "Move backfill_embeddings.py from root to scripts/backfill_embeddings.py"
Task: "Move backup_db.py from root to scripts/backup_db.py"
Task: "Move fix_invalid_projects.py from root to scripts/fix_invalid_projects.py"
Task: "Move import_chatgpt_from_zip.py from root to scripts/import_chatgpt_from_zip.py"
Task: "Move reindex_conversations.py from root to scripts/reindex_conversations.py"
Task: "Move setup_dev.py from root to scripts/setup_dev.py"
Task: "Move setup_prod_conversation_index.py from root to scripts/setup_prod_conversation_index.py"
```

---

## Parallel Example: Requirement 3

```bash
# All path updates can be done in parallel:
Task: "Update help text in scripts/index_thn_code.py line 44: change repos/ to ../repos/"
Task: "Update METADATA_DIR in brain_core/thn_code_indexer.py line 33: change Path(\"repos/.metadata\") to Path(\"../repos/.metadata\")"
Task: "Update target_dir default in brain_core/thn_code_indexer.py line 36: change \"repos\" to \"../repos\""
```

---

## Implementation Strategy

### MVP First (All Requirements)

1. Complete Phase 1: Setup
2. Complete Phase 2: Requirement 1 (Move Scripts)
3. Complete Phase 3: Requirement 2 (Create tools/)
4. Complete Phase 4: Requirement 3 (Update Path References)
5. **STOP and VALIDATE**: Test all moved files and updated paths
6. Complete Phase 5: Polish

### Incremental Delivery

1. Complete Setup → Foundation ready
2. Add Requirement 1 → Test independently → Commit
3. Add Requirement 2 → Test independently → Commit
4. Add Requirement 3 → Test independently → Commit
5. Polish → Final verification

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together
2. Once Setup is done:
   - Developer A: Requirement 1 (Move Scripts) - all 7 files in parallel
   - Developer B: Requirement 2 (Create tools/) - single file
   - Developer C: Requirement 3 (Update Path References) - 3 files in parallel
3. All requirements complete independently
4. Team collaborates on Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific requirement for traceability
- Each requirement should be independently completable and testable
- Manual verification only (as per project standards)
- Use `git mv` to preserve file history
- Commit after each requirement or logical group
- Stop at any checkpoint to validate requirement independently
- Avoid: vague tasks, same file conflicts, cross-requirement dependencies that break independence

---

## Task Summary

**Total Tasks**: 25

**Tasks by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Requirement 1 - Move Scripts): 8 tasks
- Phase 3 (Requirement 2 - Create tools/): 2 tasks
- Phase 4 (Requirement 3 - Update Path References): 5 tasks
- Phase 5 (Polish): 7 tasks

**Tasks by Requirement**:
- R1: 8 tasks
- R2: 2 tasks
- R3: 5 tasks

**Parallel Opportunities**: 18 tasks marked [P]

**Suggested MVP Scope**: All requirements (R1, R2, R3) - 15 tasks total

**Independent Test Criteria**:
- R1: Verify all 7 scripts are in scripts/ directory and can be executed from there
- R2: Verify audit_conversations.py is in tools/ directory and can be executed from there
- R3: Verify no references to repos/ remain (except in comments/docs), and code works with ../repos/ path

