# Tasks: Ollama Conversation Organizer

**Input**: Design documents from `/specs/001-ollama-organizer/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies and configuration knobs required for Ollama integration.

- [x] T001 Add `requests` dependency (if missing) to `requirements.txt` for Ollama HTTP calls
- [x] T002 Document `OLLAMA_BASE_URL` usage in `.env.example`
- [x] T003 Update `README.md` with instructions for configuring Ollama endpoints on local and tumultymedia hosts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks needed by every user story.

- [x] T004 Create SQL migration `db/migrations/2025XX_conversation_index.sql` defining the `conversation_index` table per spec
- [x] T005 Implement `brain_core/ollama_client.py` with `generate_with_ollama` helper reading `OLLAMA_BASE_URL`
- [x] T006 Wire new env var (`OLLAMA_BASE_URL`) into `brain_core/config.py` load path with sane default and validation

---

## Phase 3: User Story 1 - Save Conversation to Memory Layer (Priority: P1) 🎯 MVP

**Goal**: `/save` indexes a session through Ollama and stores structured memory in `conversation_index`.
**Independent Test**: Conduct a chat, run `/save`, confirm CLI success output and new DB row populated with required fields.

- [x] T007 [US1] Implement transcript builder + prompt helper in `brain_core/conversation_indexer.py`
- [x] T008 [US1] Add `index_session` workflow (load messages, call Ollama, parse JSON, upsert) in `brain_core/conversation_indexer.py`
- [x] T009 [US1] Extend `brain_core/db.py` with helpers to fetch session messages and upsert `conversation_index`
- [x] T010 [US1] Update `chat_cli.py` `/save` command to resolve session id, invoke `index_session`, and print title/project confirmation
- [x] T011 [US1] Create `reindex_conversations.py` script to batch index sessions missing entries or outdated versions

---

## Phase 4: User Story 2 - Load Project Memory Before New Sessions (Priority: P2)

**Goal**: Automatically build project-aware context for GPT-5.1-mini using stored memories.
**Independent Test**: With indexed entries present, start a new session and verify system prompt includes generated context; fallback works when no entries.

- [x] T012 [US2] Implement `build_project_context` helper in `brain_core/context_builder.py` (query, relevance scoring, Ollama prompt, JSON parse)
- [x] T013 [US2] Integrate project context builder into `brain_core/chat.py` (prepend system message when context available, fallback otherwise)
- [x] T019 [US2] Update `build_project_context` prompt in `brain_core/context_builder.py` to include `project_knowledge` summaries (stable overview) before conversation_index memories, following strategic ordering: project summary first, then specific conversation details

---

## Phase 5: User Story 3 - Inspect and Manage Conversation Memory (Priority: P3)

**Goal**: Provide CLI tooling to view, refresh, and delete indexed memories.
**Independent Test**: Run `/memory list/view/refresh/delete` and confirm DB state changes plus user feedback per command.

- [x] T014 [US3] Implement memory listing/view helpers (query + formatting) in `brain_core/conversation_indexer.py`
- [x] T015 [US3] Extend `chat_cli.py` with `/memory list`, `/memory view <id>`, `/memory refresh <id>`, `/memory delete <id>` commands wired to helpers

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T016 [P] Add developer quickstart steps validating Ollama + `/save` in `specs/001-ollama-organizer/quickstart.md`
- [x] T017 Review logging/error handling for Ollama failures across `brain_core/ollama_client.py`, `conversation_indexer.py`, and `context_builder.py`
- [x] T018 [P] Run manual end-to-end test following quickstart and capture issues in `README.md` or TODO list

---

## Dependencies & Execution Order

- Phase 1 (Setup) → Phase 2 (Foundational) → User Story phases (3–5) → Phase 6 (Polish).
- User Story 1 (P1) must complete before relying on stored memories. User Story 2 depends on indexed data existing but can run after US1 foundation. User Story 3 depends on conversation index + CLI wiring from US1.

## Parallel Opportunities

- T001–T003 can run in parallel (distinct files).
- T004–T006 can run concurrently once Setup done.
- Within US1, T007–T009 are parallelizable after DB helper scaffolding; T010 depends on indexer completion; T011 can start after T008/T009.
- US2 tasks (T012, T013) can proceed once US1 data path works.
- US3 tasks (T014, T015) can overlap after US1 DB helpers exist.
- Polish tasks T016 & T018 marked [P] for parallel execution.

## Implementation Strategy

1. Deliver MVP by completing Phases 1–3 (Setup, Foundational, User Story 1) so `/save` writes structured memories.
2. Layer User Story 2 to improve chat context, then User Story 3 for inspection tooling.
3. Finish with polish tasks to document and harden the experience.

