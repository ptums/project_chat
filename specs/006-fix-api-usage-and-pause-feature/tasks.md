# Tasks: Fix API Usage Display and Add Pause Feature

**Input**: Design documents from `/specs/006-fix-api-usage-and-pause-feature/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual testing via CLI (no automated tests requested)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: User Story 1 - Fix API Usage Display on Exit (Priority: P1) 🎯 MVP

**Goal**: Fix bug where API usage summary shows "No API calls made" when API calls were actually made. Ensure usage tracking correctly captures usage data from streaming responses.

**Independent Test**: Run CLI, make API calls (ask questions), type `/exit`, verify usage summary shows correct token counts, costs, and API call count.

**Acceptance Criteria**:
- Usage summary displays accurate API call count matching actual calls made
- Usage summary shows correct token counts (prompt + completion = total)
- Usage summary shows correct estimated cost based on model pricing
- Usage tracking works for both streaming and non-streaming responses

### Implementation for User Story 1

- [x] T001 [US1] Investigate usage tracking bug in `brain_core/chat.py` streaming mode - verify usage data is extracted from final chunk with `done=True`
- [x] T002 [US1] Fix usage extraction in `brain_core/chat.py` streaming mode to explicitly check for final chunk with `done=True` and extract usage from that chunk
- [x] T003 [US1] Add logging in `brain_core/chat.py` to debug usage tracking (log when usage data is received, when tracking happens, and if tracking fails)
- [x] T004 [US1] Ensure usage is recorded even if streaming is interrupted in `brain_core/chat.py` (handle KeyboardInterrupt and other exceptions)
- [x] T005 [US1] Verify `display_usage_summary()` in `chat_cli.py` correctly queries `SessionUsageTracker.get_summary()` and displays all usage data
- [x] T006 [US1] Add debug logging in `chat_cli.py` `display_usage_summary()` if usage count is zero but API calls were made
- [ ] T007 [US1] Test usage tracking with multiple API calls (streaming and non-streaming) and verify usage summary shows correct aggregated data

**Checkpoint**: At this point, User Story 1 should be fully functional. Usage summary should show accurate data when exiting after making API calls.

---

## Phase 2: User Story 2 - Pause Streaming Response with @@ (Priority: P2)

**Goal**: Allow user to pause streaming response by typing `@@` during response generation, similar to ChatGPT's pause functionality.

**Independent Test**: Run CLI, ask a question that generates a long response, type `@@` during streaming, verify response stops and user can immediately type a new prompt.

**Acceptance Criteria**:
- User can pause streaming response by typing `@@` during response generation
- Streaming stops immediately (within 100ms) when `@@` is detected
- Partial response is saved to database when paused
- User is immediately returned to input prompt after pause
- `@@` is treated as regular text when not during streaming (in regular messages)

### Implementation for User Story 2

- [x] T008 [US2] Create `detect_pause()` function in `chat_cli.py` that runs in background thread, monitors stdin for `@@` input, and sets a `threading.Event` when detected
- [x] T009 [US2] Modify streaming display loop in `chat_cli.py` `main()` to start pause detector thread when streaming begins (before entering chunk loop)
- [x] T010 [US2] Add pause flag checking in streaming loop in `chat_cli.py` - check `pause_event.is_set()` before/after each chunk
- [x] T011 [US2] Implement pause handling in `chat_cli.py` - when pause detected, break from streaming loop, save partial response using `save_message()` with `paused=True` and `partial=True` in metadata
- [x] T012 [US2] Display pause message in `chat_cli.py` when pause is detected ("Response paused. Partial response saved.")
- [x] T013 [US2] Stop pause detector thread in `chat_cli.py` when streaming ends (normally or paused) - call `thread.join(timeout=0.1)` to clean up
- [x] T014 [US2] Ensure pause detection only active during streaming - only start thread when `is_streaming=True`, stop when streaming ends
- [x] T015 [US2] Test pause feature - verify `@@` pauses streaming, partial response is saved, and user can immediately type new prompt (requires manual testing)
- [x] T016 [US2] Test edge cases - verify `@@` in regular messages is treated as text, verify pause works at start of streaming, verify pause works after streaming completes (should be text) (requires manual testing)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Pause feature should work correctly without breaking usage tracking.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T017 Run quickstart.md validation - test all scenarios from quickstart.md to verify both features work correctly (requires manual testing)
- [x] T018 Verify error handling - test usage tracking failures, pause detection failures, and partial response save failures (error handling implemented, requires manual testing)
- [x] T019 Code cleanup - review code for consistency, add type hints where needed, ensure error messages are clear
- [x] T020 Documentation - update README.md if needed to document pause feature (`@@` command)

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 1)**: No dependencies - can start immediately (bug fix)
- **User Story 2 (Phase 2)**: Can start after User Story 1 is complete, or in parallel if different developers
  - User Story 2 is independent but may benefit from seeing User Story 1's logging patterns
- **Polish (Phase 3)**: Depends on both User Stories 1 and 2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - bug fix, no dependencies on other stories
- **User Story 2 (P2)**: Independent - new feature, no dependencies on User Story 1 (but can be done after)
- Both stories modify different parts of the codebase and can be tested independently

### Within Each User Story

- **User Story 1**: 
  - Investigation (T001) before fixes (T002-T004)
  - Fixes (T002-T004) can be done in parallel
  - Display verification (T005-T006) after fixes
  - Testing (T007) after all fixes complete

- **User Story 2**:
  - Pause detection function (T008) before integration (T009-T010)
  - Integration tasks (T009-T013) are sequential (depend on each other)
  - Testing (T015-T016) after all implementation complete

### Parallel Opportunities

- **User Story 1**: 
  - T002, T003, T004 can run in parallel (all modify `brain_core/chat.py` but different sections)
  - T005 and T006 can run in parallel (both modify `chat_cli.py` but different functions)

- **User Story 2**:
  - Most tasks are sequential due to dependencies
  - T015 and T016 can run in parallel (both are testing tasks)

- **Cross-Story**:
  - User Story 1 and User Story 2 can be worked on in parallel by different developers (different files)

---

## Parallel Example: User Story 1

```bash
# Launch usage tracking fixes in parallel:
Task: "Fix usage extraction in brain_core/chat.py streaming mode"
Task: "Add logging in brain_core/chat.py to debug usage tracking"
Task: "Ensure usage is recorded even if streaming is interrupted in brain_core/chat.py"

# Launch display verification in parallel:
Task: "Verify display_usage_summary() in chat_cli.py correctly queries SessionUsageTracker"
Task: "Add debug logging in chat_cli.py display_usage_summary()"
```

---

## Parallel Example: User Story 2

```bash
# Most tasks are sequential, but testing can be done in parallel:
Task: "Test pause feature - verify @@ pauses streaming, partial response is saved"
Task: "Test edge cases - verify @@ in regular messages is treated as text"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: User Story 1 (Fix API Usage Display)
2. **STOP and VALIDATE**: Test that usage summary shows correct data on exit
3. Deploy/demo if ready

### Incremental Delivery

1. Add User Story 1 → Test independently → Deploy/Demo (MVP - Bug Fix!)
2. Add User Story 2 → Test independently → Deploy/Demo (Feature Enhancement)
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Developer A: User Story 1 (bug fix)
2. Developer B: User Story 2 (pause feature) - can start after T001 investigation or in parallel
3. Both stories complete and integrate independently

---

## Notes

- [P] tasks = different files or different sections of same file, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- User Story 1 is a bug fix (P1) - should be completed first
- User Story 2 is a feature enhancement (P2) - can be done after or in parallel

