# Tasks: Fix Ollama JSON Extraction Bug

**Input**: Design documents from `/specs/007-fix-ollama-json-extraction/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Manual testing only (as per project standards)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification

- [X] T001 Verify existing code structure in brain_core/conversation_indexer.py
- [X] T002 Verify existing code structure in brain_core/ollama_client.py
- [X] T003 [P] Review current error handling in chat_cli.py save_current_conversation function

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Research Ollama API format parameter support in brain_core/ollama_client.py
- [X] T005 Create test cases for various Ollama response formats (JSON, markdown, mixed) for manual testing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Robust JSON Extraction (Priority: P1) 🎯 MVP

**Goal**: Enhance JSON extraction to handle markdown responses and search entire response text

**Independent Test**: Test with markdown response containing JSON in code blocks - extraction should succeed

### Implementation for User Story 1

- [X] T006 [US1] Enhance extract_json_from_text to search for JSON code blocks (```json ... ```) in brain_core/conversation_indexer.py
- [X] T007 [US1] Enhance extract_json_from_text to search entire text for '{' character (not just start) in brain_core/conversation_indexer.py
- [X] T008 [US1] Add multiple extraction strategies (code blocks, anywhere in text) in extract_json_from_text in brain_core/conversation_indexer.py
- [X] T009 [US1] Add logging when extraction strategies are used in extract_json_from_text in brain_core/conversation_indexer.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Improved Prompt Engineering (Priority: P1) 🎯 MVP

**Goal**: Improve prompt to make Ollama consistently return JSON format

**Independent Test**: Test with improved prompt - Ollama should return JSON more reliably

### Implementation for User Story 2

- [X] T010 [US2] Add explicit JSON-only instruction at start of prompt in build_index_prompt in brain_core/conversation_indexer.py
- [X] T011 [US2] Add CRITICAL emphasis about JSON format in build_index_prompt in brain_core/conversation_indexer.py
- [X] T012 [US2] Add warning about no markdown/explanatory text in build_index_prompt in brain_core/conversation_indexer.py
- [X] T013 [US2] Add logging of actual prompt sent to Ollama in index_session in brain_core/conversation_indexer.py
- [X] T014 [US2] Add format parameter support to generate_with_ollama if Ollama API supports it in brain_core/ollama_client.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Enhanced Error Handling (Priority: P2)

**Goal**: Improve error messages and logging when JSON extraction fails

**Independent Test**: Test with unparseable response - should log full response and provide clear error message

### Implementation for User Story 3

- [X] T015 [US3] Enhance error logging to include full Ollama response (truncated if >1000 chars) in index_session in brain_core/conversation_indexer.py
- [X] T016 [US3] Add error messages indicating what was received vs. expected in index_session in brain_core/conversation_indexer.py
- [X] T017 [US3] Add logging when fallback extraction methods are attempted in index_session in brain_core/conversation_indexer.py
- [X] T018 [US3] Add clear indication of whether conversation was saved despite indexing failure in index_session in brain_core/conversation_indexer.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Fallback JSON Generation (Priority: P2)

**Goal**: Generate valid JSON from markdown responses when extraction fails

**Independent Test**: Test with markdown response - fallback generation should create valid JSON with all required fields

### Implementation for User Story 4

- [X] T019 [US4] Create generate_json_from_markdown function in brain_core/conversation_indexer.py
- [X] T020 [US4] Implement markdown parsing for title field in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T021 [US4] Implement markdown parsing for project field in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T022 [US4] Implement markdown parsing for tags field in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T023 [US4] Implement markdown parsing for summary fields in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T024 [US4] Implement markdown parsing for key_entities field in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T025 [US4] Implement markdown parsing for key_topics field in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T026 [US4] Add default values for missing fields using conversation metadata in generate_json_from_markdown in brain_core/conversation_indexer.py
- [X] T027 [US4] Add logging when fallback generation is used in index_session in brain_core/conversation_indexer.py
- [X] T028 [US4] Integrate fallback generation into index_session error handling flow in brain_core/conversation_indexer.py
- [X] T029 [US4] Validate generated JSON before use in index_session in brain_core/conversation_indexer.py

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Verify Ctrl+C Interruption Impact (Priority: P3)

**Goal**: Verify if interrupted conversations cause indexing issues and handle them appropriately

**Independent Test**: Test indexing with interrupted conversation - should handle partial responses gracefully

### Implementation for User Story 5

- [X] T030 [US5] Test indexing with interrupted conversation (simulate Ctrl+C) manually
- [X] T031 [US5] Check if partial responses in transcript cause markdown responses from Ollama
- [X] T032 [US5] If needed, add handling for partial responses in build_transcript in brain_core/conversation_indexer.py
- [X] T033 [US5] If needed, adjust prompt to handle incomplete conversations in build_index_prompt in brain_core/conversation_indexer.py
- [X] T034 [US5] Document findings about interruption impact in research.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Graceful Degradation Implementation

**Purpose**: Ensure conversations are saved even if indexing fails completely

- [X] T035 Modify index_session to return None instead of raising exception on complete failure in brain_core/conversation_indexer.py
- [X] T036 Update save_current_conversation to handle None return from index_session in chat_cli.py
- [X] T037 Add user-friendly error message when indexing fails but conversation is saved in chat_cli.py
- [X] T038 Ensure conversation save proceeds even if indexing fails in save_current_conversation in chat_cli.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Add type hints to enhanced extraction functions in brain_core/conversation_indexer.py
- [X] T040 [P] Add type hints to generate_json_from_markdown function in brain_core/conversation_indexer.py
- [X] T041 Code cleanup and refactoring in brain_core/conversation_indexer.py
- [X] T042 [P] Update function docstrings with new behavior in brain_core/conversation_indexer.py
- [X] T043 Run quickstart.md validation scenarios
- [X] T044 Verify backward compatibility with existing successful indexing flows

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Graceful Degradation (Phase 8)**: Depends on User Stories 1-4 completion
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run in parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Benefits from US1/US2 but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Benefits from US1/US2 but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent verification task

### Within Each User Story

- Core implementation before integration
- Extraction enhancements before fallback generation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel (both P1)
- User Stories 3 and 4 can run in parallel (both P2)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# All extraction enhancements can be worked on together:
Task: "Enhance extract_json_from_text to search for JSON code blocks"
Task: "Enhance extract_json_from_text to search entire text for '{' character"
Task: "Add multiple extraction strategies"
```

---

## Parallel Example: User Story 2

```bash
# Prompt improvements can be worked on together:
Task: "Add explicit JSON-only instruction at start of prompt"
Task: "Add CRITICAL emphasis about JSON format"
Task: "Add warning about no markdown/explanatory text"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Robust JSON Extraction)
4. Complete Phase 4: User Story 2 (Improved Prompt Engineering)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Partial MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add Graceful Degradation → Test independently → Deploy/Demo
8. Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Robust JSON Extraction)
   - Developer B: User Story 2 (Improved Prompt Engineering)
3. After US1 and US2 complete:
   - Developer A: User Story 3 (Enhanced Error Handling)
   - Developer B: User Story 4 (Fallback JSON Generation)
4. Developer C: User Story 5 (Verify Ctrl+C Impact)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing only (as per project standards)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 44

**Tasks by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 2 tasks
- Phase 3 (US1 - Robust JSON Extraction): 4 tasks
- Phase 4 (US2 - Improved Prompt Engineering): 5 tasks
- Phase 5 (US3 - Enhanced Error Handling): 4 tasks
- Phase 6 (US4 - Fallback JSON Generation): 11 tasks
- Phase 7 (US5 - Verify Ctrl+C Impact): 5 tasks
- Phase 8 (Graceful Degradation): 4 tasks
- Phase 9 (Polish): 6 tasks

**Tasks by User Story**:
- US1: 4 tasks
- US2: 5 tasks
- US3: 4 tasks
- US4: 11 tasks
- US5: 5 tasks

**Parallel Opportunities**: 8 tasks marked [P]

**Suggested MVP Scope**: User Stories 1 & 2 (Robust JSON Extraction + Improved Prompt Engineering) - 9 tasks total

**Independent Test Criteria**:
- US1: Test with markdown response containing JSON in code blocks - extraction should succeed
- US2: Test with improved prompt - Ollama should return JSON more reliably
- US3: Test with unparseable response - should log full response and provide clear error message
- US4: Test with markdown response - fallback generation should create valid JSON with all required fields
- US5: Test indexing with interrupted conversation - should handle partial responses gracefully

