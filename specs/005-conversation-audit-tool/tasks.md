# Tasks: Conversation Audit Tool

**Input**: Design documents from `/specs/005-conversation-audit-tool/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual testing via CLI (no automated tests required per spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single CLI application**: `audit_conversations.py` at repository root
- Reuses existing: `brain_core/db.py`, `brain_core/config.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `audit_conversations.py` script file at repository root with basic structure and imports
- [x] T002 [P] Import required modules: `uuid`, `psycopg2`, `brain_core.db.get_conn`, `brain_core.config.DB_CONFIG`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create `validate_uuid(uuid_str: str) -> uuid.UUID` function in `audit_conversations.py` to validate and parse UUID strings with error handling
- [x] T004 Create `validate_project(project: str) -> bool` function in `audit_conversations.py` to validate project names (THN, DAAS, FF, 700B, general)
- [x] T005 Create `display_main_menu()` function in `audit_conversations.py` to display main menu options and return user selection
- [x] T006 Create `main()` function in `audit_conversations.py` with entry point, menu loop, and routing to view handlers
- [x] T007 Add error handling wrapper functions in `audit_conversations.py` for database operations with user-friendly error messages

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - List Conversations by Project (Priority: P1) 🎯 MVP

**Goal**: Display all conversations for a specific project with id, title, project, and message count

**Independent Test**: Run `python audit_conversations.py`, select option 1, enter a project name, verify all conversations for that project are listed with correct details

### Implementation for User Story 1

- [x] T008 [US1] Create `list_conversations_by_project(project: str)` function in `audit_conversations.py` to query database for conversations filtered by project
- [x] T009 [US1] Implement SQL query in `list_conversations_by_project()` to join conversations with messages count, ordered by created_at DESC
- [x] T010 [US1] Add display formatting in `list_conversations_by_project()` to show id, title, project, message count in readable format
- [x] T011 [US1] Add "No conversations found" message handling in `list_conversations_by_project()` when query returns empty results
- [x] T012 [US1] Integrate `list_conversations_by_project()` into main menu routing when user selects option 1

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - List Conversation by ID (Priority: P1)

**Goal**: Display conversation details when user provides a conversation ID

**Independent Test**: Run `python audit_conversations.py`, select option 2, enter a valid conversation ID, verify conversation details are displayed

### Implementation for User Story 2

- [x] T013 [US2] Create `get_conversation_by_id(conv_id: str)` function in `audit_conversations.py` to query database for single conversation by UUID
- [x] T014 [US2] Add UUID validation in `get_conversation_by_id()` using `validate_uuid()` function before database query
- [x] T015 [US2] Implement SQL query in `get_conversation_by_id()` to get conversation with message count
- [x] T016 [US2] Add display formatting in `get_conversation_by_id()` to show id, title, project, message count, created_at
- [x] T017 [US2] Add "Conversation not found" error handling in `get_conversation_by_id()` when query returns no results
- [x] T018 [US2] Integrate `get_conversation_by_id()` into main menu routing when user selects option 2

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - List Conversation by Title (Priority: P1)

**Goal**: Find conversations by searching for title (exact or partial match)

**Independent Test**: Run `python audit_conversations.py`, select option 3, enter a title (or partial), verify matching conversations are displayed

### Implementation for User Story 3

- [x] T019 [US3] Create `search_conversations_by_title(title: str)` function in `audit_conversations.py` to query database for conversations matching title pattern
- [x] T020 [US3] Implement SQL query in `search_conversations_by_title()` using ILIKE for case-insensitive partial matching
- [x] T021 [US3] Add display formatting in `search_conversations_by_title()` to show all matching conversations with id, title, project, message count
- [x] T022 [US3] Add "No conversations found" message handling in `search_conversations_by_title()` when query returns empty results
- [x] T023 [US3] Integrate `search_conversations_by_title()` into main menu routing when user selects option 3

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Review Message History (Priority: P2)

**Goal**: Display message history for a conversation in chronological order with role and content

**Independent Test**: Run `python audit_conversations.py`, select any list option, type `/messages <conversation_id>`, verify message history is displayed in readable format

### Implementation for User Story 4

- [x] T024 [US4] Create `view_messages(conv_id: str)` function in `audit_conversations.py` to query and display message history
- [x] T025 [US4] Add UUID validation in `view_messages()` using `validate_uuid()` function before database query
- [x] T026 [US4] Implement SQL query in `view_messages()` to load messages ordered by created_at ASC with LIMIT 50
- [x] T027 [US4] Add display formatting in `view_messages()` to show messages with [USER] or [ASSISTANT] role prefix and numbered list
- [x] T028 [US4] Add "Conversation not found" and "No messages found" error handling in `view_messages()`
- [x] T029 [US4] Create message review mode command handler in `audit_conversations.py` to process `/messages <id>` command from list views
- [x] T030 [US4] Add command prompt display in message review mode showing available commands: `/edit-title`, `/edit-project`, `/delete`, `/back`

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Edit Conversation Title (Priority: P2)

**Goal**: Update conversation title when reviewing message history

**Independent Test**: Run `/messages <conversation_id>`, type `/edit-title`, enter new title, verify title is updated in database

### Implementation for User Story 5

- [x] T031 [US5] Create `edit_conversation_title(conv_id: uuid.UUID, new_title: str)` function in `audit_conversations.py` to update conversation title
- [x] T032 [US5] Add title validation in `edit_conversation_title()` to ensure title is non-empty after `.strip()`
- [x] T033 [US5] Implement SQL UPDATE query in `edit_conversation_title()` to update `conversations.title` WHERE id = conv_id
- [x] T034 [US5] Add success message display in `edit_conversation_title()` after successful update
- [x] T035 [US5] Integrate `/edit-title` command handler in message review mode to call `edit_conversation_title()` with user input

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Edit Conversation Project (Priority: P2)

**Goal**: Update conversation project tag and keep `conversations` and `conversation_index` tables in sync

**Independent Test**: Run `/messages <conversation_id>`, type `/edit-project`, enter new project, verify project is updated in both tables

### Implementation for User Story 6

- [x] T036 [US6] Create `edit_conversation_project(conv_id: uuid.UUID, new_project: str)` function in `audit_conversations.py` to update conversation project
- [x] T037 [US6] Add project validation in `edit_conversation_project()` using `validate_project()` function
- [x] T038 [US6] Implement transaction in `edit_conversation_project()` to update both `conversations.project` and `conversation_index.project` atomically
- [x] T039 [US6] Add error handling in `edit_conversation_project()` to rollback transaction on failure
- [x] T040 [US6] Add success message display in `edit_conversation_project()` after successful update
- [x] T041 [US6] Integrate `/edit-project` command handler in message review mode to call `edit_conversation_project()` with user input

**Checkpoint**: At this point, User Stories 1-6 should all work independently

---

## Phase 9: User Story 7 - Delete Conversation (Priority: P3)

**Goal**: Delete conversation entirely with confirmation prompt

**Independent Test**: Run `/messages <conversation_id>`, type `/delete`, confirm with "yes", verify conversation and all messages are deleted from database

### Implementation for User Story 7

- [x] T042 [US7] Create `delete_conversation(conv_id: uuid.UUID)` function in `audit_conversations.py` to delete conversation
- [x] T043 [US7] Implement SQL DELETE query in `delete_conversation()` to delete from `conversations` table (CASCADE handles messages and conversation_index)
- [x] T044 [US7] Add confirmation prompt in `delete_conversation()` asking "Are you sure you want to delete this conversation? (yes/no)"
- [x] T045 [US7] Add confirmation logic in `delete_conversation()` to only delete if user enters "yes", cancel otherwise
- [x] T046 [US7] Add success message display in `delete_conversation()` after successful deletion
- [x] T047 [US7] Add error handling in `delete_conversation()` to display error message if deletion fails
- [x] T048 [US7] Integrate `/delete` command handler in message review mode to call `delete_conversation()` with confirmation

**Checkpoint**: At this point, all user stories should be independently functional

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T049 [P] Add `/back` command handler in message review mode to return to previous view (main menu or conversation list)
- [x] T050 [P] Add Ctrl+C handling throughout CLI to exit gracefully with "Exiting." message
- [x] T051 [P] Add input validation error messages throughout (invalid UUID format, invalid project, empty title)
- [x] T052 [P] Improve error messages to be more user-friendly and actionable
- [x] T053 [P] Add database connection error handling with clear messages
- [x] T054 [P] Verify all database queries use parameterized queries (no SQL injection vulnerabilities)
- [x] T055 [P] Add logging for audit operations (optional, for debugging)
- [x] T056 Run quickstart.md validation: Test all scenarios from quickstart.md to verify complete implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US1/US2/US3 for `/messages` command integration
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Depends on US4 for message review mode
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Depends on US4 for message review mode
- **User Story 7 (P3)**: Can start after Foundational (Phase 2) - Depends on US4 for message review mode

### Within Each User Story

- Core query functions before display formatting
- Display formatting before integration with menu
- Validation before database operations
- Error handling throughout

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1, 2, 3 can start in parallel
- User Stories 5, 6, 7 can run in parallel after US4 is complete
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# All tasks for User Story 1 are sequential (each depends on previous)
# But User Stories 1, 2, 3 can run in parallel after Foundational phase
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (List by project)
4. Complete Phase 4: User Story 2 (View by ID)
5. Complete Phase 5: User Story 3 (Search by title)
6. **STOP and VALIDATE**: Test all three P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Stories 1-3 (P1) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 4 (P2) → Test independently → Deploy/Demo
4. Add User Stories 5-6 (P2) → Test independently → Deploy/Demo
5. Add User Story 7 (P3) → Test independently → Deploy/Demo
6. Add Polish phase → Final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Stories 1, 4, 5
   - Developer B: User Stories 2, 6
   - Developer C: User Stories 3, 7
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All database queries must use parameterized queries
- Verify all error cases are handled gracefully
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

- **Total Tasks**: 56
- **Setup Tasks**: 2 (T001-T002)
- **Foundational Tasks**: 5 (T003-T007)
- **User Story 1 Tasks**: 5 (T008-T012)
- **User Story 2 Tasks**: 6 (T013-T018)
- **User Story 3 Tasks**: 5 (T019-T023)
- **User Story 4 Tasks**: 7 (T024-T030)
- **User Story 5 Tasks**: 5 (T031-T035)
- **User Story 6 Tasks**: 6 (T036-T041)
- **User Story 7 Tasks**: 7 (T042-T048)
- **Polish Tasks**: 8 (T049-T056)

**Parallel Opportunities**:

- Setup tasks: 1 parallel task
- Foundational: All can run in parallel
- User Stories 1-3: Can run in parallel after Foundational
- User Stories 5-7: Can run in parallel after US4
- Polish: 7 parallel tasks

**Suggested MVP Scope**: User Stories 1-3 (List by project, View by ID, Search by title) - 16 tasks total
