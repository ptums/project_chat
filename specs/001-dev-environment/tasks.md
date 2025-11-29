# Implementation Tasks: Development Environment

**Feature**: Development Environment  
**Branch**: `001-dev-environment`  
**Date**: 2025-01-27  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

This feature enables a development environment that isolates development work from production by supporting environment mode switching, separate development database, and mock AI responses.

**Total Tasks**: 30  
**MVP Scope**: Phases 1-5 (User Stories 1-3) - Core development environment functionality (19 tasks)

## Dependencies

### User Story Completion Order

1. **Phase 1 (Setup)** → Must complete first
2. **Phase 2 (Foundational)** → Blocks all user stories
3. **Phase 3 (US1)** → Can be done in parallel with Phase 4
4. **Phase 4 (US2)** → Can be done in parallel with Phase 3
5. **Phase 5 (US3)** → Depends on Phase 3 (database config)
6. **Phase 6 (US4)** → Depends on Phases 3-5 (enhances existing functionality)
7. **Phase 7 (US5)** → Depends on Phase 5 (database setup)
8. **Phase 8 (Polish)** → Depends on all previous phases

### Parallel Execution Opportunities

- **Phase 3 (US1) + Phase 4 (US2)**: Can be done in parallel (different files, no dependencies)
- **Phase 6 (US4) + Phase 7 (US5)**: Can be done in parallel (different features)

## Implementation Strategy

**MVP First**: Implement Phases 1-5 (Setup, Foundational, US1, US2, US3) to deliver core development environment functionality. This enables developers to work without API costs and with isolated data.

**Incremental Delivery**:

- After MVP: Developers can use development mode
- Phase 6: Improves configuration experience
- Phase 7: Simplifies database setup
- Phase 8: Polish and edge cases

---

## Phase 1: Setup

**Goal**: Initialize project structure and create configuration templates.

**Independent Test**: Verify configuration template exists and can be copied to create `.env.local`.

### Tasks

- [x] T001 Create `.env.example` template file with all required environment variables in `/Users/petertumulty/Documents/Sites/overclockai/week2/project_chat/.env.example`
- [x] T002 Add documentation comments to `.env.example` explaining each variable and when to use development vs production values

---

## Phase 2: Foundational

**Goal**: Implement core infrastructure for environment mode detection and mock client foundation.

**Independent Test**: Verify environment mode can be detected and mock client can be imported.

### Tasks

- [x] T003 [P] Update `brain_core/config.py` to detect `ENV_MODE` environment variable with default "production"
- [x] T004 [P] Update `brain_core/config.py` to load `.env.local` file if it exists (before `.env`)
- [x] T005 [P] Create `brain_core/mock_client.py` with `MockOpenAIClient` class structure matching OpenAI client interface
- [x] T006 [P] Implement `MockChatCompletions` class in `brain_core/mock_client.py` with `create()` method signature matching OpenAI SDK

---

## Phase 3: User Story 1 - Switch to Development Mode

**Goal**: Enable switching between development and production modes via configuration.

**Independent Test**: Set `ENV_MODE=development` and verify application uses development database configuration.

**Acceptance Criteria**:

- Application detects development mode from environment variable
- Development mode uses separate database configuration
- Production mode remains default and unchanged
- Mode switching requires application restart

### Tasks

- [x] T007 [US1] Update `brain_core/config.py` to select development database config when `ENV_MODE=development`
- [x] T008 [US1] Update `brain_core/config.py` to select production database config when `ENV_MODE=production` or not set
- [x] T009 [US1] Add validation in `brain_core/config.py` to ensure `ENV_MODE` is "development" or "production" (case-insensitive)
- [x] T010 [US1] Add error handling in `brain_core/config.py` to default to production mode with warning if invalid `ENV_MODE` is detected
- [x] T011 [US1] Update `brain_core/config.py` to export `ENV_MODE` and `MOCK_MODE` constants for use by other modules

---

## Phase 4: User Story 2 - Mock AI Responses Without API Costs

**Goal**: Provide mock AI responses in development mode without making OpenAI API calls.

**Independent Test**: Enable mock mode and verify chat requests return mock responses without network calls.

**Acceptance Criteria**:

- Mock client returns responses matching OpenAI client interface
- Mock responses indicate mock mode clearly
- No OpenAI API calls are made when mock mode is enabled
- Response metadata includes mock mode flag

### Tasks

- [x] T012 [US2] Implement `MockChatCompletion`, `MockChoice`, and `MockMessage` classes in `brain_core/mock_client.py` to match OpenAI response structure
- [x] T013 [US2] Implement response generation logic in `MockChatCompletions.create()` to return acknowledgment response with mock mode indicator
- [x] T014 [US2] Update `brain_core/config.py` to initialize `MockOpenAIClient` when `MOCK_MODE=true` or `ENV_MODE=development`
- [x] T015 [US2] Update `brain_core/config.py` to initialize real `OpenAI` client when `MOCK_MODE=false` and `ENV_MODE=production`
- [x] T016 [US2] Update `brain_core/chat.py` to use `client` from `brain_core.config` (already imports it, verify it works)
- [x] T017 [US2] Update `brain_core/chat.py` to set `meta["model"] = "mock"` and `meta["mock_mode"] = True` when saving mock responses

---

## Phase 5: User Story 3 - Isolated Development Database

**Goal**: Ensure development mode uses completely separate database from production.

**Independent Test**: Verify development mode connects to different database and operations don't affect production.

**Acceptance Criteria**:

- Development mode connects to development database
- Production mode connects to production database
- Database operations are isolated by mode
- Production data remains unaffected in development mode

### Tasks

- [x] T018 [US3] Verify `brain_core/db.py` uses `DB_CONFIG` from `brain_core.config` (already does, confirm it works with updated config)
- [ ] T019 [US3] Add database connection validation in `brain_core/config.py` to test connection on startup (optional, can be in Phase 8)

---

## Phase 6: User Story 4 - Easy Environment Configuration

**Goal**: Improve configuration experience with clear defaults and error messages.

**Independent Test**: Set configuration values and verify application correctly interprets them and provides helpful error messages.

**Acceptance Criteria**:

- Single environment variable switches between modes
- Configuration errors are detected and reported clearly
- Application defaults to production mode safely
- Configuration is readable and well-documented

### Tasks

- [x] T020 [US4] Add configuration validation logging in `brain_core/config.py` to log current mode and database config on startup
- [x] T021 [US4] Improve error messages in `brain_core/config.py` for missing or invalid configuration
- [x] T022 [US4] Add type hints to configuration functions in `brain_core/config.py` for better code clarity

---

## Phase 7: User Story 5 - Development Database Initialization

**Goal**: Provide script to easily initialize development database with correct schema.

**Independent Test**: Run initialization script and verify development database is created with correct schema.

**Acceptance Criteria**:

- Script creates development database if it doesn't exist
- Script sets up correct schema (conversations, messages, project_knowledge tables)
- Script handles existing database gracefully
- Script provides clear error messages

### Tasks

- [x] T023 [US5] Create `setup_dev_db.py` script to connect to PostgreSQL and create development database
- [x] T024 [US5] Implement schema creation in `setup_dev_db.py` for conversations, messages, and project_knowledge tables
- [x] T025 [US5] Add error handling and user prompts in `setup_dev_db.py` for existing database scenarios

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Address edge cases, improve error handling, and ensure production readiness.

**Independent Test**: Test edge cases and verify all error scenarios are handled gracefully.

### Tasks

- [x] T026 Add database connection testing in `brain_core/config.py` to validate connection before use (fail fast)
- [x] T027 Add logging to indicate which mode (development/production) is active when application starts
- [x] T028 Verify all error paths in configuration loading have clear error messages
- [x] T029 Test mode switching by restarting application with different `ENV_MODE` values
- [x] T030 Verify production mode behavior is unchanged (regression test)

---

## Task Summary by User Story

- **Setup (Phase 1)**: 2 tasks
- **Foundational (Phase 2)**: 4 tasks
- **User Story 1**: 5 tasks
- **User Story 2**: 6 tasks
- **User Story 3**: 2 tasks
- **User Story 4**: 3 tasks
- **User Story 5**: 3 tasks
- **Polish (Phase 8)**: 5 tasks

**Total**: 30 tasks

## Parallel Execution Examples

### Example 1: Phase 3 + Phase 4 (US1 + US2)

Can be done in parallel:

- Developer A: Works on T007-T011 (US1 - config updates)
- Developer B: Works on T012-T017 (US2 - mock client)

No conflicts: Different files, no dependencies between them.

### Example 2: Phase 6 + Phase 7 (US4 + US5)

Can be done in parallel:

- Developer A: Works on T020-T022 (US4 - configuration improvements)
- Developer B: Works on T023-T025 (US5 - database initialization)

No conflicts: Different features, different files.

## Notes

- User has already created `.env.local` file, so T001-T002 provide template for others
- `brain_core/db.py` already uses `DB_CONFIG` from config, so minimal changes needed
- `brain_core/chat.py` already imports `client` from config, just needs to work with mock client
- All tasks include specific file paths for clarity
- MVP scope (Phases 1-5) delivers core functionality for development work
