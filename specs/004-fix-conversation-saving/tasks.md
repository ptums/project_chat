# Tasks: Fix Conversation Saving and Project Switching

**Input**: Design documents from `/specs/004-fix-conversation-saving/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual testing via CLI (no automated test tasks - see quickstart.md for test scenarios)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single CLI application**: `chat_cli.py` at repository root, `brain_core/` for core modules
- All modifications are to existing files - no new files needed

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup needed - modifying existing codebase

No setup tasks required. All work is modifications to existing `chat_cli.py` and reuse of existing functions from `brain_core/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helper function that all user stories depend on

**⚠️ CRITICAL**: This helper function must be complete before ANY user story can be implemented

- [X] T001 Create `save_current_conversation(conv_id: UUID, current_project: str) -> bool` helper function in `chat_cli.py` that calls `index_session(conv_id, override_project=current_project)` with error handling, displays spinner during save, and returns True/False for success/failure

**Checkpoint**: Helper function ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Auto-Save on Project Switch (Priority: P1) 🎯 MVP

**Goal**: Automatically save current conversation when user switches projects, then prompt for new title, then switch project context, then continue conversation.

**Independent Test**: Start conversation in "general", add messages, type `/thn`, verify: (1) save completes, (2) title prompt appears, (3) after entering title, project context switches to "THN", (4) conversation continues under new project.

### Implementation for User Story 1

- [X] T002 [US1] Modify `handle_command()` in `chat_cli.py` to detect project switch commands (`/thn`, `/daas`, `/ff`, `/700b`, `/general`, `/project TAG`) and return special flag "project_switch" with new project value
- [X] T003 [US1] In main loop in `main()` function in `chat_cli.py`, when "project_switch" special flag detected: call `save_current_conversation(conv_id, current_project)` and wait for completion
- [X] T004 [US1] After save completes in project switch flow in `main()` function in `chat_cli.py`, prompt user "Conversation title for [PROJECT] (required):" and loop until non-empty title provided (display "A title is required" if empty)
- [X] T005 [US1] After title is provided in project switch flow in `main()` function in `chat_cli.py`, call `create_conversation(new_title, new_project)` from `brain_core.db` to create new conversation
- [X] T006 [US1] After creating new conversation in project switch flow in `main()` function in `chat_cli.py`, update `conv_id` variable to new conversation UUID and update `current_project` to new project
- [X] T007 [US1] After project switch completes in `main()` function in `chat_cli.py`, display "Switched active project context to [PROJECT] [emoji]" message and continue conversation loop with new conversation_id

**Checkpoint**: At this point, User Story 1 should be fully functional - project switches trigger save, title prompt, new conversation creation, and context switch

---

## Phase 4: User Story 2 - Auto-Save on Exit (Priority: P1) 🎯 MVP

**Goal**: Automatically save current conversation when user exits program via `/exit` or Ctrl+C.

**Independent Test**: Start conversation, exchange messages, type `/exit`, verify conversation was saved before program exits.

### Implementation for User Story 2

- [X] T008 [US2] Modify `/exit` command handler in `main()` function in `chat_cli.py` to call `save_current_conversation(conv_id, current_project)` before displaying usage summary and exiting
- [X] T009 [US2] Modify `_signal_handler()` function in `chat_cli.py` to call `save_current_conversation(conv_id, current_project)` before displaying usage summary and exiting (handle Ctrl+C)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - project switches and exits both trigger auto-save

---

## Phase 5: User Story 3 - Mandatory Conversation Titles (Priority: P2)

**Goal**: Require non-empty title when starting new conversation - cannot skip with Enter.

**Independent Test**: Start program, press Enter when prompted for title, verify system displays "A title is required" and prompts again instead of proceeding.

### Implementation for User Story 3

- [X] T010 [US3] Modify title input in `main()` function in `chat_cli.py` startup flow to use while loop that prompts "Conversation title (required):" and loops until non-empty title provided (after `.strip()`)
- [X] T011 [US3] Add "A title is required" error message display in title validation loop in `main()` function in `chat_cli.py` when user presses Enter without input or enters only whitespace

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - titles are mandatory at startup

---

## Phase 6: User Story 4 - Title Prompt on Project Switch (Priority: P2)

**Goal**: When switching projects, prompt for new title after save completes (this is part of US1 flow but separated for clarity).

**Independent Test**: Start conversation in "general" with title "Hobbit Discussion", switch to "THN" using `/thn`, verify exact sequence: (1) save completes, (2) title prompt appears, (3) after entering title, project context switches, (4) conversation continues.

### Implementation for User Story 4

**Note**: This user story is already implemented as part of User Story 1 (tasks T004-T007). The title prompt and validation logic is shared with User Story 3. This phase ensures the integration is complete.

- [X] T012 [US4] Verify title prompt after project switch in `main()` function in `chat_cli.py` uses same validation logic as User Story 3 (non-empty, loop until provided, display "A title is required" if empty)
- [X] T013 [US4] Verify new conversation creation in project switch flow in `main()` function in `chat_cli.py` uses the provided title and new project correctly

**Checkpoint**: All user stories should now be independently functional - complete flow from startup through project switches to exit

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and validation

- [X] T014 Add error handling in `save_current_conversation()` in `chat_cli.py` to catch exceptions (OllamaError, ValueError, generic Exception) and display user-friendly warning messages while allowing operation to continue
- [X] T015 Add error handling in project switch flow in `main()` function in `chat_cli.py` to handle save failures gracefully (warn user but continue with project switch)
- [X] T016 Add error handling in exit handlers in `main()` function and `_signal_handler()` in `chat_cli.py` to handle save failures gracefully (warn user but continue with exit)
- [X] T017 Handle edge case in project switch flow in `main()` function in `chat_cli.py`: if user cancels title input with Ctrl+C during project switch, handle cancellation gracefully
- [X] T018 Add logging for auto-save operations in `chat_cli.py` to track when saves are triggered (project switch, exit, Ctrl+C)
- [X] T019 Run quickstart.md validation: Test all scenarios from quickstart.md to verify complete implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - no setup needed
- **Foundational (Phase 2)**: No dependencies - can start immediately
- **User Stories (Phase 3+)**: All depend on Foundational phase (T001) completion
  - User Story 1 (Phase 3): Depends on T001 - can start after foundational
  - User Story 2 (Phase 4): Depends on T001 - can start after foundational (can run in parallel with US1)
  - User Story 3 (Phase 5): Depends on T001 - can start after foundational (can run in parallel with US1/US2)
  - User Story 4 (Phase 6): Depends on US1 completion (T002-T007) - must complete after US1
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1, can run in parallel
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2, can run in parallel
- **User Story 4 (P2)**: Must start after US1 completion - Depends on T002-T007 from US1

### Within Each User Story

- Helper function (T001) before any user story implementation
- Command detection before save logic
- Save logic before title prompt
- Title prompt before new conversation creation
- New conversation creation before context switch
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 2**: No parallel opportunities (single helper function)
- **Phase 3-5**: User Stories 1, 2, and 3 can be worked on in parallel after T001 completes (different parts of same file, but can be coordinated)
- **Phase 6**: Must wait for US1 completion
- **Phase 7**: All polish tasks can run in parallel after all user stories complete

---

## Parallel Example: User Stories 2 and 3

```bash
# After T001 completes, these can be worked on in parallel:
# Developer A: User Story 2 (exit handlers)
Task: "Modify /exit command handler in main() function in chat_cli.py"
Task: "Modify _signal_handler() function in chat_cli.py"

# Developer B: User Story 3 (title validation at startup)
Task: "Modify title input in main() function in chat_cli.py startup flow"
Task: "Add 'A title is required' error message display in title validation loop"
```

**Note**: Since all tasks modify `chat_cli.py`, true parallel execution requires coordination or sequential work on different functions within the file.

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only)

1. Complete Phase 2: Foundational (T001 - helper function)
2. Complete Phase 3: User Story 1 (T002-T007 - project switch with save)
3. Complete Phase 4: User Story 2 (T008-T009 - exit with save)
4. **STOP and VALIDATE**: Test both stories independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational → Helper function ready
2. Add User Story 1 → Test independently → Project switches work with save
3. Add User Story 2 → Test independently → Exits work with save
4. Add User Story 3 → Test independently → Titles mandatory at startup
5. Add User Story 4 → Test independently → Title prompt on project switch verified
6. Add Polish → Error handling and edge cases
7. Each story adds value without breaking previous stories

### Sequential Implementation (Recommended)

Since all tasks modify the same file (`chat_cli.py`), sequential implementation is recommended:

1. T001: Create helper function
2. T002-T007: User Story 1 (project switch flow)
3. T008-T009: User Story 2 (exit handlers)
4. T010-T011: User Story 3 (title validation at startup)
5. T012-T013: User Story 4 (verification)
6. T014-T019: Polish (error handling, edge cases, validation)

---

## Notes

- All tasks modify existing `chat_cli.py` file - coordinate changes carefully
- Helper function (T001) is critical - must complete before user stories
- User Stories 1 and 2 are both P1 (MVP) - prioritize these
- User Stories 3 and 4 are P2 - can follow after MVP
- No automated tests - use manual testing from quickstart.md
- Commit after each logical group (helper function, each user story, polish)
- Stop at any checkpoint to validate story independently
- Error handling should be graceful - warn but continue operation

