# Tasks: Enhance THN RAG System

**Input**: Design documents from `/specs/013-enhance-thn-rag/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Manual testing (consistent with project standards)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `brain_core/` at repository root
- Paths shown below assume single project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and preparation

- [x] T001 Backup current THN RAG implementation in brain_core/context_builder.py (lines 489-562)
- [x] T002 Verify database tables exist: conversation_index and code_index
- [x] T003 Verify THN data exists: Check conversation_index has THN entries and code_index has entries with embeddings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Review existing code structure in brain_core/context_builder.py to understand current THN RAG implementation
- [x] T005 [P] Review existing code structure in brain_core/thn_code_retrieval.py to understand code retrieval functions
- [x] T006 [P] Review existing code structure in brain_core/chat.py to understand message ordering and wrapper text

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Remove Current THN RAG Implementation (Priority: P1) 🎯 MVP

**Goal**: Clean up existing THN-specific RAG code to prepare for new implementation

**Independent Test**: Verify THN project falls back to default behavior (no errors) when old RAG code is removed

### Implementation for User Story 1

- [x] T007 [US1] Remove THN-specific block (lines 489-562) from build_project_context() function in brain_core/context_builder.py
- [x] T008 [US1] Remove import of get_thn_code_context from thn_code_retrieval.py in brain_core/context_builder.py (if present)
- [x] T009 [US1] Remove MCP notes retrieval logic for THN project in brain_core/context_builder.py (if present in removed block)
- [x] T010 [US1] Verify THN project falls back to default keyword-based search behavior after removal
- [x] T011 [US1] Test that THN conversations still work (with default behavior) after old code removal

**Checkpoint**: At this point, old THN RAG is removed and THN falls back to default behavior without errors

---

## Phase 4: User Story 2 - Implement New THN RAG Functions (Priority: P1) 🎯 MVP

**Goal**: Implement helper functions and main function for new THN RAG format with History & Context and Relevant Code Snippets sections

**Independent Test**: Verify new RAG functions can be called independently and return correctly formatted output with test data

### Implementation for User Story 2

- [x] T012 [P] [US2] Implement \_retrieve_thn_conversations(limit: int = 5) function in brain_core/context_builder.py to query conversation_index for last N THN conversations
- [x] T013 [P] [US2] Implement \_format_conversation_entry(row: Tuple) function in brain_core/context_builder.py to format conversation_index row into RAG format
- [x] T014 [P] [US2] Implement \_retrieve_thn_code(user_message: str, top_k: int = 5) function in brain_core/context_builder.py to query code_index using vector similarity search
- [x] T015 [US2] Implement \_format_code_snippet(chunk: Dict[str, Any]) function in brain_core/context_builder.py to format code_index chunk into RAG format (depends on T014 for understanding chunk structure)
- [x] T016 [US2] Implement build_thn_rag_context(user_message: str) function in brain_core/context_builder.py that combines conversation and code retrieval (depends on T012, T013, T014, T015)
- [x] T017 [US2] Add error handling for database errors in \_retrieve_thn_conversations() function in brain_core/context_builder.py
- [x] T018 [US2] Add error handling for embedding generation failures in \_retrieve_thn_code() function in brain_core/context_builder.py
- [x] T019 [US2] Add NULL field handling in \_format_conversation_entry() function in brain_core/context_builder.py
- [x] T020 [US2] Add truncation logic (summary_detailed: 500 chars, memory_snippet: 300 chars) in \_format_conversation_entry() function in brain_core/context_builder.py
- [x] T021 [US2] Add truncation logic (chunk_text: 1000 chars) in \_format_code_snippet() function in brain_core/context_builder.py
- [x] T022 [US2] Add JSONB array formatting (tags, key_entities) in \_format_conversation_entry() function in brain_core/context_builder.py
- [x] T023 [US2] Add brief_description generation from metadata (function_name/class_name) or file path in \_format_code_snippet() function in brain_core/context_builder.py
- [x] T024 [US2] Add logging for RAG generation operations in build_thn_rag_context() function in brain_core/context_builder.py
- [ ] T025 [US2] Test \_retrieve_thn_conversations() with THN project data and verify returns last 5 conversations ordered by indexed_at DESC
- [ ] T026 [US2] Test \_format_conversation_entry() with sample data including NULL fields and verify formatting
- [ ] T027 [US2] Test \_retrieve_thn_code() with sample user_message and verify vector similarity search returns top 5 code chunks
- [ ] T028 [US2] Test \_format_code_snippet() with sample code chunks including metadata and without metadata
- [ ] T029 [US2] Test build_thn_rag_context() end-to-end with sample data and verify output format matches specification

**Checkpoint**: At this point, new THN RAG functions are implemented and tested independently

---

## Phase 5: User Story 3 - Integrate New RAG and Update Wrapper Text (Priority: P1) 🎯 MVP

**Goal**: Replace old THN block in build_project_context() with new RAG implementation and update wrapper text in chat.py

**Independent Test**: Verify THN project uses new RAG format in chat system messages, appearing after project_knowledge section

### Implementation for User Story 3

- [x] T030 [US3] Replace THN-specific block in build_project_context() function in brain_core/context_builder.py with call to build_thn_rag_context(user_message)
- [x] T031 [US3] Add error handling and fallback behavior in build_project_context() for THN project in brain_core/context_builder.py
- [x] T032 [US3] Update wrapper text in chat.py (lines 67-72) to be more concise (remove verbose introduction, use concise one-liner or remove entirely)
- [x] T033 [US3] Verify message ordering in chat.py: System prompt (overview/rules) → THN RAG → Note reads → Conversation history
- [ ] T034 [US3] Test THN RAG appears correctly in system messages after project_knowledge section
- [ ] T035 [US3] Test THN RAG format matches specification (History & Context section with 5 conversations, Relevant Code Snippets section with 5 code chunks)
- [ ] T036 [US3] Verify performance: RAG generation completes in <500ms for THN project
- [ ] T037 [US3] Test error handling: Verify graceful fallback when no conversations found or no code found
- [ ] T038 [US3] Test error handling: Verify graceful fallback when embedding generation fails

**Checkpoint**: At this point, new THN RAG is fully integrated and working in chat system

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T039 [P] Add debug logging for RAG generation performance metrics in brain_core/context_builder.py
- [x] T040 [P] Verify code follows project patterns and maintainability standards in brain_core/context_builder.py
- [x] T041 [P] Update documentation comments in build_thn_rag_context() and helper functions in brain_core/context_builder.py
- [ ] T042 Run quickstart.md validation steps to verify implementation matches documentation
- [ ] T043 Test with various data states: NULL fields, empty tables, partial data in brain_core/context_builder.py
- [ ] T044 Verify RAG output format matches quickstart.md examples exactly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories should proceed sequentially: US1 → US2 → US3
  - US1 must complete before US2 (removes old code first)
  - US2 must complete before US3 (implements new functions first)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Must start after US1 completes - Implements new functions that will replace old code
- **User Story 3 (P1)**: Must start after US2 completes - Integrates new functions into existing system

### Within Each User Story

- Helper functions before main function
- Error handling added during implementation
- Testing after implementation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Within User Story 2: Helper functions (T012, T013, T014) can be implemented in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch helper function implementations in parallel:
Task: "Implement _retrieve_thn_conversations() function in brain_core/context_builder.py"
Task: "Implement _format_conversation_entry() function in brain_core/context_builder.py"
Task: "Implement _retrieve_thn_code() function in brain_core/context_builder.py"

# Then implement formatting and main function sequentially:
Task: "Implement _format_code_snippet() function" (depends on understanding chunk structure)
Task: "Implement build_thn_rag_context() function" (depends on all helpers)
```

---

## Implementation Strategy

### MVP First (All User Stories Required)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Remove old code)
4. Complete Phase 4: User Story 2 (Implement new functions)
5. Complete Phase 5: User Story 3 (Integrate new RAG)
6. **STOP and VALIDATE**: Test complete THN RAG system independently
7. Complete Phase 6: Polish

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Remove old code → Verify fallback works
3. Add User Story 2 → Implement new functions → Test independently
4. Add User Story 3 → Integrate → Test end-to-end → Deploy/Demo
5. Add Polish → Final validation

### Sequential Execution (Recommended)

Since this is a refactoring task with clear dependencies:

1. Team completes Setup + Foundational together
2. Complete User Story 1 (remove old code)
3. Complete User Story 2 (implement new functions) - can parallelize helper functions
4. Complete User Story 3 (integrate)
5. Complete Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Performance target: RAG generation <500ms
- Format: RAG sections are self-explanatory, wrapper text should be concise or removed
