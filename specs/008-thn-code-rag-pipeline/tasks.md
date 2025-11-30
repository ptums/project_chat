# Tasks: THN Code RAG Pipeline Enhancement

**Input**: Design documents from `/specs/008-thn-code-rag-pipeline/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Manual testing only (as per project standards)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create repos directory structure at project root
- [X] T002 Create repos/.metadata directory for repository metadata storage
- [X] T003 [P] Verify gitpython dependency is available or add to requirements.txt
- [X] T004 [P] Verify pgvector extension is installed in PostgreSQL (already exists for DAAS)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database migration file for code_index table in db/migrations/003_thn_code_index.sql
- [ ] T006 Run database migration to create code_index table and indexes
- [X] T007 Create brain_core/thn_code_indexer.py module structure with imports
- [X] T008 Create brain_core/thn_code_retrieval.py module structure with imports
- [X] T009 Create scripts/index_thn_code.py script structure with argument parsing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Repository Code Indexing (Priority: P1) 🎯 MVP

**Goal**: Index all THN-related repository code with vector embeddings for retrieval

**Independent Test**: Clone a test repository, run indexing script, verify code chunks and embeddings are stored in code_index table

### Implementation for User Story 1

- [X] T010 [US1] Implement clone_repository function in brain_core/thn_code_indexer.py
- [X] T011 [US1] Implement update_repository function in brain_core/thn_code_indexer.py
- [X] T012 [US1] Implement repository metadata storage functions in brain_core/thn_code_indexer.py
- [X] T013 [US1] Implement file scanning function to discover code files in brain_core/thn_code_indexer.py
- [X] T014 [US1] Implement detect_language function to identify file language in brain_core/thn_code_indexer.py
- [X] T015 [US1] Implement parse_python_file function using AST in brain_core/thn_code_indexer.py
- [X] T016 [US1] Implement parse_shell_file function to extract functions in brain_core/thn_code_indexer.py
- [X] T017 [US1] Implement parse_config_file function for YAML/JSON/TOML in brain_core/thn_code_indexer.py
- [X] T018 [US1] Implement parse_code_file function that routes to language-specific parsers in brain_core/thn_code_indexer.py
- [X] T019 [US1] Implement generate_code_embedding function with metadata context in brain_core/thn_code_indexer.py
- [X] T020 [US1] Implement store_code_chunk function to save chunks to code_index table in brain_core/thn_code_indexer.py
- [X] T021 [US1] Implement index_repository function that orchestrates full indexing workflow in brain_core/thn_code_indexer.py
- [X] T022 [US1] Implement incremental indexing logic to detect changed files in brain_core/thn_code_indexer.py
- [X] T023 [US1] Implement batch processing for embedding generation with rate limit handling in brain_core/thn_code_indexer.py
- [X] T024 [US1] Complete scripts/index_thn_code.py with CLI argument parsing and main execution flow
- [X] T025 [US1] Add error handling and logging throughout indexing functions in brain_core/thn_code_indexer.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Code Retrieval for THN Context (Priority: P1) 🎯 MVP

**Goal**: Automatically retrieve relevant code snippets when discussing THN topics

**Independent Test**: Index a repository, start chat in THN context, ask code-related question, verify code snippets are retrieved and included in response

### Implementation for User Story 2

- [X] T026 [US2] Implement retrieve_thn_code function for vector similarity search in brain_core/thn_code_retrieval.py
- [X] T027 [US2] Implement retrieve_code_by_file function for file-specific retrieval in brain_core/thn_code_retrieval.py
- [X] T028 [US2] Implement get_thn_code_context function to format code chunks for LLM prompt in brain_core/thn_code_retrieval.py
- [X] T029 [US2] Add repository filtering logic to restrict to THN repositories in brain_core/thn_code_retrieval.py
- [X] T030 [US2] Modify context_builder.py to detect THN project context and call code retrieval in brain_core/context_builder.py
- [X] T031 [US2] Integrate code context with existing conversation context in context_builder.py in brain_core/context_builder.py
- [X] T032 [US2] Add error handling for code retrieval failures with graceful degradation in brain_core/thn_code_retrieval.py
- [X] T033 [US2] Add logging for code retrieval operations in brain_core/thn_code_retrieval.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Production Environment Awareness (Priority: P2)

**Goal**: Associate code with production machines and enable environment-specific filtering

**Independent Test**: Index repository with production targets, query code for specific machine, verify only relevant code is retrieved

### Implementation for User Story 3

- [X] T034 [US3] Add production_targets parameter to index_repository function in brain_core/thn_code_indexer.py
- [X] T035 [US3] Store production_targets array in code_index table during indexing in brain_core/thn_code_indexer.py
- [X] T036 [US3] Add production_filter parameter to retrieve_thn_code function in brain_core/thn_code_retrieval.py
- [X] T037 [US3] Implement production target filtering in database queries in brain_core/thn_code_retrieval.py
- [X] T038 [US3] Update scripts/index_thn_code.py to accept production-targets argument
- [X] T039 [US3] Add production environment context to code retrieval responses in brain_core/thn_code_retrieval.py
- [X] T040 [US3] Document deployment workflow mapping in code metadata in brain_core/thn_code_indexer.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Teaching and Learning Support (Priority: P2)

**Goal**: Enable THN to explain code concepts and propose learning projects

**Independent Test**: Ask THN to explain a code concept, verify explanation uses actual code from repository and is educational

### Implementation for User Story 4

- [X] T041 [US4] Enhance prompt building to include teaching instructions for THN context in brain_core/context_builder.py
- [X] T042 [US4] Add code pattern detection logic to identify learning opportunities in brain_core/thn_code_retrieval.py
- [X] T043 [US4] Integrate code examples into explanation responses in brain_core/context_builder.py
- [X] T044 [US4] Add lesson plan generation prompts for THN conversations in brain_core/context_builder.py
- [X] T045 [US4] Add project proposal generation based on codebase patterns in brain_core/context_builder.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T046 [P] Create scripts/backfill_thn_embeddings.py for existing code chunks
- [X] T047 [P] Add type hints to all functions in brain_core/thn_code_indexer.py
- [X] T048 [P] Add type hints to all functions in brain_core/thn_code_retrieval.py
- [X] T049 [P] Update function docstrings with comprehensive documentation in brain_core/thn_code_indexer.py
- [X] T050 [P] Update function docstrings with comprehensive documentation in brain_core/thn_code_retrieval.py
- [X] T051 Code cleanup and refactoring in brain_core/thn_code_indexer.py
- [X] T052 Code cleanup and refactoring in brain_core/thn_code_retrieval.py
- [X] T053 Add .gitignore entries for repos/ directory
- [ ] T054 Run quickstart.md validation scenarios
- [X] T055 Verify backward compatibility with existing chat flows for non-THN projects

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for code_index table and indexing functions
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 for indexing and retrieval infrastructure
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US2 for code retrieval functionality

### Within Each User Story

- Repository management before file parsing
- File parsing before embedding generation
- Embedding generation before storage
- Storage before retrieval
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start (US2 depends on US1)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Language-specific parsers can be developed in parallel:
Task: "Implement parse_python_file function using AST"
Task: "Implement parse_shell_file function to extract functions"
Task: "Implement parse_config_file function for YAML/JSON/TOML"
```

---

## Parallel Example: User Story 2

```bash
# Retrieval functions can be developed in parallel:
Task: "Implement retrieve_thn_code function for vector similarity search"
Task: "Implement retrieve_code_by_file function for file-specific retrieval"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Repository Code Indexing)
4. Complete Phase 4: User Story 2 (Code Retrieval for THN Context)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Partial MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Repository Code Indexing)
   - Developer B: Prepares for User Story 2 (can start after US1 indexing functions complete)
3. After US1 indexing complete:
   - Developer A: User Story 3 (Production Environment Awareness)
   - Developer B: User Story 2 (Code Retrieval)
4. Developer C: User Story 4 (Teaching Support)
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

**Total Tasks**: 55

**Tasks by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - Repository Code Indexing): 16 tasks
- Phase 4 (US2 - Code Retrieval for THN Context): 8 tasks
- Phase 5 (US3 - Production Environment Awareness): 7 tasks
- Phase 6 (US4 - Teaching and Learning Support): 5 tasks
- Phase 7 (Polish): 10 tasks

**Tasks by User Story**:
- US1: 16 tasks
- US2: 8 tasks
- US3: 7 tasks
- US4: 5 tasks

**Parallel Opportunities**: 12 tasks marked [P]

**Suggested MVP Scope**: User Stories 1 & 2 (Repository Code Indexing + Code Retrieval) - 24 tasks total

**Independent Test Criteria**:
- US1: Clone a test repository, run indexing script, verify code chunks and embeddings are stored in code_index table
- US2: Index a repository, start chat in THN context, ask code-related question, verify code snippets are retrieved and included in response
- US3: Index repository with production targets, query code for specific machine, verify only relevant code is retrieved
- US4: Ask THN to explain a code concept, verify explanation uses actual code from repository and is educational

