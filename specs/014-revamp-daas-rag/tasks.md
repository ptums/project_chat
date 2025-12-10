---
description: "Task list for Revamp DAAS RAG System feature"
---

# Tasks: Revamp DAAS RAG System

**Input**: Design documents from `/specs/014-revamp-daas-rag/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual testing (consistent with project standards) - no automated test tasks included

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `brain_core/` at repository root
- Paths shown below assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project preparation and code review

- [x] T001 Review existing DAAS RAG implementation in `brain_core/daas_retrieval.py` to understand current code structure
- [x] T002 Review DAAS retrieval integration in `brain_core/context_builder.py` (lines 704-786) to identify removal scope
- [x] T003 Review "Thinking" spinner implementation in `chat_cli.py` (lines 1356, 1502, 1625) to identify removal scope

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks required - using existing infrastructure

**Status**: No blocking prerequisites. All required infrastructure (database, embeddings, vector search) already exists.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Remove Old DAAS RAG Code (Priority: P1) 🎯 MVP

**Goal**: Completely remove the existing DAAS RAG implementation that uses conversation history, including the `daas_retrieval.py` file and all related code from `context_builder.py`.

**Independent Test**: Verify that DAAS project conversations no longer use old retrieval logic by checking that `daas_retrieval.py` is deleted and no imports reference it.

### Implementation for User Story 1

- [x] T004 [US1] Delete `brain_core/daas_retrieval.py` file completely
- [x] T005 [US1] Remove import statement `from .daas_retrieval import retrieve_daas_context` from `brain_core/context_builder.py` (line 707)
- [x] T006 [US1] Remove import statement `from .config import DAAS_VECTOR_TOP_K` from `brain_core/context_builder.py` (line 708) if only used for DAAS
- [x] T007 [US1] Remove entire DAAS-specific retrieval block (lines 704-786) from `build_project_context()` function in `brain_core/context_builder.py`
- [x] T008 [US1] Verify no other files import or reference `daas_retrieval` module
- [ ] T009 [US1] Test that DAAS project conversations still work (should fall back to default behavior temporarily)

**Checkpoint**: At this point, old DAAS RAG code should be completely removed. DAAS conversations will temporarily use default keyword-based search until new RAG is implemented.

---

## Phase 4: User Story 2 - Implement New DAAS RAG System (Priority: P1) 🎯 MVP

**Goal**: Implement new DAAS RAG system that retrieves related dreams by themes, symbols, or events using vector similarity search, with clear separation between dreams and optimized token usage.

**Independent Test**: Start a DAAS conversation and verify that related dreams are retrieved and formatted correctly when querying about themes/symbols/events. Verify RAG context appears in system messages.

### Implementation for User Story 2

- [x] T010 [US2] Implement `build_daas_rag_context()` function in `brain_core/context_builder.py` with signature `(user_message: str, top_k: int = 3) -> Dict[str, Any]`
- [x] T011 [US2] Add input validation in `build_daas_rag_context()` to handle empty user_message and validate top_k (cap at 5, default to 3)
- [x] T012 [US2] Implement embedding generation in `build_daas_rag_context()` using `generate_embedding(user_message)` from `embedding_service.py`
- [x] T013 [US2] Implement vector similarity search query in `build_daas_rag_context()` to retrieve dreams from `conversation_index` table filtered by `project = 'DAAS'` and `embedding IS NOT NULL`
- [x] T014 [US2] Implement dream formatting in `build_daas_rag_context()` with markdown headers, truncating `summary_short` to 300 chars and `memory_snippet` to 200 chars
- [x] T015 [US2] Add clear separators between dreams in formatted output (use `---` markdown separator)
- [x] T016 [US2] Add header "### Related Dreams for Analysis" to formatted context
- [x] T017 [US2] Implement error handling in `build_daas_rag_context()` to return empty context on embedding or database errors
- [x] T018 [US2] Add logging for DAAS RAG operations in `build_daas_rag_context()` (debug level for normal operations, error level for failures)
- [x] T019 [US2] Integrate `build_daas_rag_context()` into `build_project_context()` function in `brain_core/context_builder.py` by adding DAAS-specific check after THN check (around line 788)
- [x] T020 [US2] Add call to `build_daas_rag_context(user_message, top_k=3)` in `build_project_context()` for DAAS project with error handling fallback
- [ ] T021 [US2] Test new DAAS RAG with various queries (themes, symbols, events) to verify retrieval and formatting
- [ ] T022 [US2] Verify RAG context stays under 1000 tokens (test with 3-5 dreams)
- [ ] T023 [US2] Verify RAG generation completes in <500ms (measure performance)

**Checkpoint**: At this point, new DAAS RAG system should be fully functional, retrieving and formatting related dreams correctly with proper separation and token optimization.

---

## Phase 5: User Story 3 - Remove Debugging Messages (Priority: P2)

**Goal**: Remove "Thinking for [PROJECT]" spinner messages from chat interface to provide cleaner user experience.

**Independent Test**: Start any project conversation and verify that no "Thinking for [PROJECT]" spinner appears during message processing.

### Implementation for User Story 3

- [x] T024 [US3] Remove `thinking_label` variable assignment at line 1356 in `chat_cli.py`
- [x] T025 [US3] Remove spinner thread creation and start code (lines 1357-1364) in `chat_cli.py` for first location
- [x] T026 [US3] Remove `stop_event.set()` call that stops spinner in `chat_cli.py` for first location (find corresponding stop call)
- [x] T027 [US3] Remove `thinking_label` variable assignment at line 1502 in `chat_cli.py`
- [x] T028 [US3] Remove spinner thread creation and start code for second location in `chat_cli.py` (around line 1502)
- [x] T029 [US3] Remove `stop_event.set()` call for second location in `chat_cli.py`
- [x] T030 [US3] Remove `thinking_label` variable assignment at line 1625 in `chat_cli.py`
- [x] T031 [US3] Remove spinner thread creation and start code for third location in `chat_cli.py` (around line 1625)
- [x] T032 [US3] Remove `stop_event.set()` call for third location in `chat_cli.py`
- [ ] T033 [US3] Verify no "Thinking for [PROJECT]" messages appear in chat interface during any project conversation
- [ ] T034 [US3] Verify chat functionality still works correctly without spinner (messages process and display normally)

**Checkpoint**: At this point, all debugging "Thinking" messages should be removed and chat interface should work smoothly without visual noise.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T035 [P] Verify all old DAAS RAG code is removed (no references to `daas_retrieval` anywhere)
- [x] T036 [P] Verify new DAAS RAG follows same pattern as THN RAG for consistency
- [x] T037 [P] Review and optimize token usage in `build_daas_rag_context()` if needed
- [x] T038 [P] Add performance logging for DAAS RAG generation (similar to THN RAG timing logs)
- [ ] T039 [P] Test DAAS RAG with edge cases (no dreams found, empty database, malformed data)
- [x] T040 [P] Verify error handling gracefully falls back to default behavior when RAG fails
- [ ] T041 [P] Run quickstart.md validation steps to ensure all requirements met
- [ ] T042 [P] Update any documentation that references old DAAS retrieval system

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: No tasks - infrastructure already exists
- **User Stories (Phase 3+)**: Can proceed sequentially or in parallel after setup
  - User Story 1 (Remove old code) should complete before User Story 2 (Implement new)
  - User Story 3 (Remove debugging) can be done in parallel with User Story 2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start immediately after Setup - Removes old code
- **User Story 2 (P1)**: Must start after User Story 1 completes - Implements new RAG system
- **User Story 3 (P2)**: Can start after Setup - Independent of RAG implementation, can run in parallel with US2

### Within Each User Story

- User Story 1: Delete file → Remove imports → Remove code block → Verify
- User Story 2: Implement function → Add validation → Add search → Add formatting → Integrate → Test
- User Story 3: Remove spinner code from all 3 locations → Verify

### Parallel Opportunities

- Setup tasks (T001-T003) can be done in parallel (different files to review)
- User Story 3 tasks (T024-T032) can be done in parallel (different locations in same file, but sequential is safer)
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2

```bash
# These can be done in parallel (different aspects of same function):
Task: "Add input validation in build_daas_rag_context()"
Task: "Implement embedding generation in build_daas_rag_context()"
Task: "Implement vector similarity search query in build_daas_rag_context()"

# These must be sequential (depend on previous):
Task: "Implement dream formatting" (needs search results)
Task: "Integrate into build_project_context()" (needs complete function)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (review existing code)
2. Complete Phase 3: User Story 1 (remove old code)
3. Complete Phase 4: User Story 2 (implement new RAG)
4. **STOP and VALIDATE**: Test new DAAS RAG independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup → Code reviewed
2. Add User Story 1 → Old code removed → Verify fallback works
3. Add User Story 2 → New RAG implemented → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 → Debugging removed → Polish → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together (code review)
2. Developer A: User Story 1 (remove old code)
3. Once US1 complete:
   - Developer A: User Story 2 (implement new RAG)
   - Developer B: User Story 3 (remove debugging) - can start in parallel
4. Stories complete and integrate

---

## Notes

- [P] tasks = different files or independent operations, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing only (no automated tests per project standards)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- User Story 1 must complete before User Story 2 (new code replaces old)
- User Story 3 is independent and can be done anytime after Setup
