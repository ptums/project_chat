# Tasks: DAAS Semantic Dream Retrieval and Streaming Responses

**Input**: Design documents from `/specs/002-daas-semantic-retrieval/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies and configuration required for vector embeddings and streaming responses.

- [x] T001 [P] Add `pgvector` installation instructions to `README.md` (PostgreSQL extension setup)
- [x] T002 [P] Document `DAAS_VECTOR_TOP_K` environment variable in `.env.example` with default value (5)
- [x] T003 [P] Verify OpenAI API key is configured for embedding generation (check `.env.example`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks needed by all user stories - database schema and core modules.

- [x] T004 Create database migration script to install pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;` in `db/migrations/002_add_pgvector.sql` or similar
- [x] T005 Create database migration script to add `embedding vector(1536)` column to `conversation_index` table in `db/migrations/002_add_embedding_column.sql`
- [x] T006 Create database migration script to create vector similarity index `idx_conversation_index_embedding` in `db/migrations/002_add_embedding_index.sql`
- [x] T007 Implement `brain_core/embedding_service.py` with `generate_embedding(text: str) -> List[float]` function using OpenAI `text-embedding-3-small` model
- [x] T008 Implement `brain_core/daas_retrieval.py` with `detect_quoted_title(message: str) -> Optional[str]` function using regex pattern `"([^"]+)"`
- [x] T009 Implement `brain_core/daas_retrieval.py` with `retrieve_single_dream(title: str) -> Optional[Dict]` function for title-based matching
- [x] T010 Implement `brain_core/daas_retrieval.py` with `retrieve_pattern_dreams(query: str, top_k: int) -> List[Dict]` function for vector similarity search
- [x] T011 Implement `brain_core/daas_retrieval.py` with `retrieve_daas_context(user_message: str, top_k: int) -> Dict` main routing function

---

## Phase 3: User Story 1 - Single Dream Analysis by Title (Priority: P1) 🎯 MVP

**Goal**: Users can reference specific dreams by quoted title and receive analysis using only that dream's context.
**Independent Test**: Ask "What does 'My Flying Dream' mean from a Jungian perspective?" in DAAS project and verify only that specific dream is retrieved, no other dreams included, response focuses solely on that dream.

- [x] T012 [US1] Integrate DAAS retrieval routing into `brain_core/context_builder.py` by adding DAAS-specific check at start of `build_project_context()` function
- [x] T013 [US1] Modify `brain_core/context_builder.py` to call `retrieve_daas_context()` when `project == 'DAAS'` and use single-dream mode result
- [x] T014 [US1] Update `brain_core/context_builder.py` to handle no-match case for single-dream mode with user-friendly error message
- [ ] T015 [US1] Test single-dream retrieval: Create test DAAS conversation, query with quoted title, verify only that dream is retrieved

---

## Phase 4: User Story 2 - Pattern-Based Dream Analysis Across Dreams (Priority: P2)

**Goal**: Users can explore themes and patterns across multiple dreams using semantic similarity search.
**Independent Test**: Ask "What patterns do I have with water in my dreams?" in DAAS project and verify system uses vector similarity search, retrieves top-k semantically similar dreams, provides analysis across those dreams.

- [x] T016 [US2] Modify `brain_core/conversation_indexer.py` `index_session()` function to generate embedding for DAAS entries after indexing completes
- [x] T017 [US2] Add embedding generation logic in `brain_core/conversation_indexer.py` that combines `title`, `summary_detailed`, and `memory_snippet` for embedding text
- [x] T018 [US2] Add embedding storage logic in `brain_core/conversation_indexer.py` that updates `conversation_index.embedding` column with generated vector
- [x] T019 [US2] Update `brain_core/context_builder.py` to use pattern-based mode (vector search) when no quoted title detected in DAAS queries
- [x] T020 [US2] Implement `backfill_embeddings.py` script at repository root to generate embeddings for existing DAAS entries missing them
- [x] T021 [US2] Add batch processing logic to `backfill_embeddings.py` (batches of 50 with 1s delay between batches)
- [x] T022 [US2] Add progress logging and resumable logic to `backfill_embeddings.py` (skip entries with existing embeddings)
- [ ] T023 [US2] Test pattern-based retrieval: Create multiple DAAS conversations with similar themes, query without quoted title, verify top-k relevant dreams retrieved

---

## Phase 5: User Story 3 - Streaming Response Display (Priority: P3)

**Goal**: Responses appear progressively word-by-word or chunk-by-chunk, mimicking ChatGPT experience.
**Independent Test**: Send any query and observe response text appears incrementally rather than as single complete block, text cascades down screen as generated.

- [x] T024 [US3] Modify `brain_core/chat.py` `chat_turn()` function to accept optional `stream: bool = False` parameter
- [x] T025 [US3] Implement streaming mode in `brain_core/chat.py` that uses OpenAI `stream=True` and yields chunks via generator
- [x] T026 [US3] Modify `brain_core/chat.py` to save complete response after streaming completes (accumulate chunks, then save)
- [x] T027 [US3] Update `chat_cli.py` main loop to call `chat_turn()` with `stream=True` and handle generator response
- [x] T028 [US3] Implement streaming display in `chat_cli.py` that prints chunks as received using `sys.stdout.write()` and `sys.stdout.flush()`
- [x] T029 [US3] Add graceful Ctrl+C handling for streaming responses in `chat_cli.py` (interrupt streaming, display message)
- [ ] T030 [US3] Modify `api_server.py` `/api/chat` endpoint to support streaming responses via Server-Sent Events (SSE) when `Accept: text/event-stream` header present (SKIP: api_server.py does not exist)
- [ ] T031 [US3] Implement SSE streaming in `api_server.py` that sends chunks as `data: {"chunk": "text"}\n\n` format (SKIP: api_server.py does not exist)
- [ ] T032 [US3] Test streaming in CLI: Send query, verify text appears progressively, verify complete response saved correctly
- [ ] T033 [US3] Test streaming in API: Send request with SSE header, verify chunks received progressively, verify complete response returned (SKIP: api_server.py does not exist)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T034 [P] Add error handling for embedding generation failures in `brain_core/embedding_service.py` (rate limits, API errors, network issues)
- [x] T035 [P] Add error handling for vector search failures in `brain_core/daas_retrieval.py` (pgvector errors, missing embeddings, empty results)
- [x] T036 [P] Add fallback logic in `brain_core/context_builder.py` to use existing keyword search when vector search fails for DAAS
- [x] T037 [P] Update `brain_core/config.py` to load `DAAS_VECTOR_TOP_K` environment variable with default value of 5
- [x] T038 [P] Add logging for DAAS retrieval mode selection (single-dream vs pattern-based) in `brain_core/daas_retrieval.py`
- [x] T039 [P] Add logging for embedding generation and vector search operations in `brain_core/embedding_service.py` and `brain_core/daas_retrieval.py`
- [x] T040 [P] Update `README.md` with instructions for running database migrations and backfill script
- [ ] T041 [P] Run manual end-to-end test: Create DAAS dreams, test single-dream query, test pattern query, test streaming, verify all work together
- [x] T042 [P] Document edge cases handling in code comments: malformed quotes, no matches, multiple title matches, streaming interruptions

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **User Story phases (3–5)** → **Phase 6 (Polish)**
- **Phase 2** must complete before any user story (database schema and core modules required)
- **User Story 1 (P1)** can start after Phase 2, provides MVP functionality
- **User Story 2 (P2)** depends on embedding generation from Phase 2 and requires backfill for existing data
- **User Story 3 (P3)** can proceed in parallel with US1/US2 but requires chat.py modifications
- **Phase 6** depends on all user stories completing

## Parallel Opportunities

- **T001–T003** can run in parallel (distinct documentation files)
- **T004–T006** (database migrations) should run sequentially but can be prepared in parallel
- **T007–T011** (foundational modules) can run in parallel after T004–T006 complete
- **Within US1**: T012–T014 can run in parallel after T011 completes
- **Within US2**: T016–T018 can run in parallel; T019 can start after T011; T020–T022 can run in parallel
- **Within US3**: T024–T026 can run in parallel; T027–T029 (CLI) can run in parallel with T030–T031 (API)
- **Polish tasks T034–T042** marked [P] for parallel execution after user stories complete

## Implementation Strategy

1. **MVP Delivery**: Complete Phases 1–3 (Setup, Foundational, User Story 1) to enable single-dream retrieval by quoted title
2. **Pattern Recognition**: Layer User Story 2 to enable semantic pattern detection across dreams
3. **User Experience**: Add User Story 3 for streaming responses to improve perceived responsiveness
4. **Hardening**: Finish with Phase 6 polish tasks for error handling, logging, and documentation

## Task Summary

- **Total Tasks**: 42
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 8 tasks
- **User Story 1 (P1)**: 4 tasks
- **User Story 2 (P2)**: 8 tasks
- **User Story 3 (P3)**: 10 tasks
- **Polish Phase**: 9 tasks

## Independent Test Criteria

- **User Story 1**: Ask "Analyze 'Dream Title Here' from a Christian perspective" and verify only matching dream retrieved, no other dreams included, response focuses solely on that dream
- **User Story 2**: Ask "What patterns do I have with water in my dreams?" and verify vector similarity search used, top-k semantically similar dreams retrieved, analysis provided across those dreams
- **User Story 3**: Send any query and observe response text appears incrementally (word-by-word or chunk-by-chunk) rather than as single complete block, text cascades down screen

## Suggested MVP Scope

**MVP = Phases 1–3 (Setup + Foundational + User Story 1)**
- Enables single-dream retrieval by quoted title
- Provides immediate value for most common use case
- Establishes foundation for pattern-based search (US2) and streaming (US3)
- Can be tested and validated independently before adding complexity

