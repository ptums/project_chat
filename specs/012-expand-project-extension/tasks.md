---
description: "Task list for Expand Project-Specific Extension with Rules feature"
---

# Tasks: Expand Project-Specific Extension with Rules

**Input**: Design documents from `/specs/012-expand-project-extension/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual testing (consistent with project standards) - no automated test tasks included

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `brain_core/`, `db/` at repository root
- Paths shown below assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and preparation

- [ ] T001 Backup existing project_knowledge table before migration (use scripts/backup_db.py or manual backup)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Verify migration script 004_project_knowledge_simplify.sql exists and is correct in db/migrations/
- [x] T003 Verify rollback script 004_project_knowledge_simplify_rollback.sql exists and is correct in db/migrations/
- [ ] T004 Run migration script 004_project_knowledge_simplify.sql to update project_knowledge table structure
- [ ] T005 Verify migration completed successfully by checking table structure in database

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Rules Retrieval and Parsing (Priority: P1) 🎯 MVP

**Goal**: Implement functions to retrieve and parse project rules from the database

**Independent Test**: Call `_get_project_rules("THN")` and `_parse_rules_text()` with sample rules text, verify they return correct data structures.

### Implementation for User Story 1

- [x] T006 [US1] Implement \_get_project_rules(project: str) function in brain_core/context_builder.py to query rules column from project_knowledge table
- [x] T007 [US1] Implement \_parse_rules_text(rules_text: str) function in brain_core/context_builder.py to parse numbered rules into list
- [x] T008 [US1] Add error handling for missing rules or parsing failures in \_parse_rules_text() function in brain_core/context_builder.py
- [ ] T009 [US1] Test \_parse_rules_text() with various formats (numbered list, newline-separated) in brain_core/context_builder.py

**Checkpoint**: At this point, User Story 1 should be fully functional - rules can be retrieved and parsed from database

---

## Phase 4: User Story 2 - System Prompt Extension with Rules (Priority: P1)

**Goal**: Update system prompt composition to include project rules section formatted as numbered bullet list

**Independent Test**: Call `build_project_system_prompt("THN")` and verify it includes base prompt + overview + rules section with proper formatting.

### Implementation for User Story 2

- [x] T010 [US2] Update \_get_project_overview() function in brain_core/context_builder.py to query overview column directly (remove key='overview' filter)
- [x] T011 [US2] Update build_project_system_prompt() function in brain_core/context_builder.py to retrieve rules using \_get_project_rules()
- [x] T012 [US2] Add rules parsing in build_project_system_prompt() function in brain_core/context_builder.py using \_parse_rules_text()
- [x] T013 [US2] Format rules section as markdown numbered list in build_project_system_prompt() function in brain_core/context_builder.py
- [x] T014 [US2] Implement rules section format "### Project {PROJECT} rules:\n\n1. {rule 1}\n2. {rule 2}..." in build_project_system_prompt() function in brain_core/context_builder.py
- [x] T015 [US2] Ensure rules section is only included when rules exist and are not empty in build_project_system_prompt() function in brain_core/context_builder.py
- [x] T016 [US2] Update project extension format to match spec: "In this current conversation is tagged as project {PROJECT}.\n\nHere's a general overview..." in build_project_system_prompt() function in brain_core/context_builder.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - system prompt includes rules section

---

## Phase 5: User Story 3 - Seed Data and Validation (Priority: P2)

**Goal**: Load seed data with rules and validate the complete system works with all projects

**Independent Test**: Load seed data, test system prompt generation for all projects (THN, DAAS, FF, 700B), verify rules appear correctly.

### Implementation for User Story 3

- [ ] T017 [US3] Load seed data from project_knowledge_seed_v2.sql into database using psql command
- [ ] T018 [US3] Verify seed data loaded correctly by querying project_knowledge table for all projects
- [ ] T019 [US3] Test build_project_system_prompt() with THN project and verify rules section appears in brain_core/context_builder.py
- [ ] T020 [US3] Test build_project_system_prompt() with DAAS project and verify rules section appears in brain_core/context_builder.py
- [ ] T021 [US3] Test build_project_system_prompt() with FF project and verify rules section appears in brain_core/context_builder.py
- [ ] T022 [US3] Test build_project_system_prompt() with 700B project and verify rules section appears in brain_core/context_builder.py
- [ ] T023 [US3] Test build_project_system_prompt() with general project and verify no rules section appears in brain_core/context_builder.py

**Checkpoint**: All user stories should now be independently functional - seed data loaded and system works for all projects

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T024 [P] Add logging for rules retrieval in \_get_project_rules() function in brain_core/context_builder.py
- [x] T025 [P] Add logging for rules parsing in \_parse_rules_text() function in brain_core/context_builder.py
- [x] T026 [P] Add logging for rules section composition in build_project_system_prompt() function in brain_core/context_builder.py
- [ ] T027 Verify error handling works correctly when rules column is NULL in brain_core/context_builder.py
- [ ] T028 Verify error handling works correctly when rules column is empty string in brain_core/context_builder.py
- [ ] T029 Test rules parsing with edge cases (single rule, no rules, malformed rules) in brain_core/context_builder.py
- [ ] T030 Run quickstart.md validation steps to verify implementation matches documentation
- [x] T031 Update db/migrations/README.md to document migration 004_project_knowledge_simplify.sql

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 (uses \_get_project_rules and \_parse_rules_text functions)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 (needs complete system prompt functionality)

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority
- Manual testing after each story completion

### Parallel Opportunities

- All Setup tasks can run in parallel (only one task in this phase)
- Foundational tasks T002 and T003 can run in parallel (verification tasks)
- Once Foundational phase completes, US1 can start
- Once US1 completes, US2 can start (depends on US1 functions)
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational verification tasks together:
Task: "Verify migration script 004_project_knowledge_simplify.sql exists and is correct in db/migrations/"
Task: "Verify rollback script 004_project_knowledge_simplify_rollback.sql exists and is correct in db/migrations/"
```

---

## Parallel Example: User Story 1

```bash
# After migration, these US1 tasks can be worked on together:
Task: "Implement _get_project_rules(project: str) function in brain_core/context_builder.py to query rules column from project_knowledge table"
Task: "Add error handling for missing rules or parsing failures in _parse_rules_text() function in brain_core/context_builder.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (backup database)
2. Complete Phase 2: Foundational (run migration)
3. Complete Phase 3: User Story 1 (rules retrieval and parsing)
4. **STOP and VALIDATE**: Test rules retrieval and parsing functions
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - rules retrieval working!)
3. Add User Story 2 → Test independently → Deploy/Demo (system prompt with rules working!)
4. Add User Story 3 → Test independently → Deploy/Demo (seed data and validation complete)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (rules retrieval and parsing)
   - Developer B: Can help with US1 or prepare for US2
3. Once US1 is complete:
   - Developer A: User Story 2 (system prompt extension)
   - Developer B: User Story 3 (seed data and validation)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing after each task or logical group
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks include explicit file paths for clarity
- No automated tests per project standards (manual testing only)
- Migration scripts already created in planning phase - verify and run them
