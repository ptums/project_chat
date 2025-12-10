# Tasks: RAG and Notes Improvements

**Feature**: RAG and Notes Improvements  
**Branch**: `015-rag-and-notes-improvements`  
**Generated**: 2025-01-27

## Summary

Three improvements to the project chat system:

1. Remove automatic RAG inclusion in system prompts - make RAG manual-only via `/rag` command
2. Fix `/mcp` sync to include all project directories (FF, 700B, etc.)
3. Rename `/mcp` command to `/notes` for clarity

**Total Tasks**: 25  
**Tasks by User Story**: US1 (9 tasks), US2 (5 tasks), US3 (8 tasks), Polish (3 tasks)

## Dependencies

**User Story Completion Order**:

- US1 (Manual RAG Only) → Can be done independently
- US2 (Fix MCP Sync) → Can be done independently
- US3 (Rename Command) → Should be done after US2 (uses same code paths)

**Parallel Execution Opportunities**:

- US1 and US2 can be done in parallel (different files)
- US3 should wait for US2 completion (both modify `chat_cli.py`)

## Implementation Strategy

**MVP Scope**: User Story 1 (Manual RAG Only) - Simplifies system prompt building and gives explicit control.

**Incremental Delivery**:

1. Phase 1: Remove automatic RAG (US1) - Simplest, highest impact
2. Phase 2: Fix MCP sync (US2) - Verification and testing
3. Phase 3: Rename command (US3) - User-facing change
4. Phase 4: Polish - Final validation

---

## Phase 1: Setup

**Purpose**: Project preparation and code review

- [x] T001 Review existing RAG inclusion logic in `brain_core/context_builder.py` (lines ~137-172) to understand removal scope
- [x] T002 Review RAG inclusion logic in `brain_core/chat.py` (lines ~70-95) to identify removal scope
- [x] T003 Review `should_include_daas_rag()` function in `brain_core/context_builder.py` (lines ~692-750) to understand deletion scope
- [x] T004 Review `/mcp` command implementation in `chat_cli.py` (lines ~678-909) to understand rename scope
- [x] T005 Review `NoteParser.find_notes()` in `src/services/note_parser.py` to verify recursive directory scanning
- [x] T006 Review `ProjectDirectoryMapper` in `src/services/project_filter.py` to verify all project mappings

---

## Phase 2: Foundational

**Purpose**: No blocking prerequisites - all user stories can proceed independently

No foundational tasks required. All changes are modifications to existing code.

---

## Phase 3: User Story 1 - Manual RAG Only

**Goal**: Remove automatic RAG inclusion from system prompts. RAG only available via manual `/rag` command.

**Independent Test Criteria**:

- Start new THN conversation, send first message, verify logs show NO "THN RAG included" message
- Start new DAAS conversation, send analysis request, verify logs show NO "DAAS RAG included" message
- Use `/rag` command in THN conversation, verify RAG context is displayed
- Use `/rag` command in DAAS conversation, verify RAG context is displayed

### Implementation for User Story 1

- [x] T007 [US1] Remove THN RAG inclusion block from `build_project_system_prompt()` in `brain_core/context_builder.py` (lines ~137-152)
- [x] T008 [US1] Remove DAAS RAG inclusion block from `build_project_system_prompt()` in `brain_core/context_builder.py` (lines ~154-172)
- [x] T009 [US1] Delete `should_include_daas_rag()` function from `brain_core/context_builder.py` (entire function, lines ~692-750)
- [x] T010 [US1] Update docstring for `build_project_system_prompt()` in `brain_core/context_builder.py` to reflect no automatic RAG inclusion
- [x] T011 [US1] Remove `include_thn_rag` and `include_daas_rag` logic from `chat_turn()` in `brain_core/chat.py` (lines ~73-79)
- [x] T012 [US1] Replace RAG inclusion logic with simple call `build_project_system_prompt(project, "")` in `brain_core/chat.py`
- [x] T013 [US1] Remove RAG-related logging from `chat_turn()` in `brain_core/chat.py` (lines ~84-95, keep only basic debug log)
- [x] T014 [US1] Remove `should_include_daas_rag` import from `brain_core/chat.py` if present
- [x] T015 [US1] Simplify `indexed_context` logic in `chat_turn()` in `brain_core/chat.py` (remove THN/DAAS skip logic, lines ~45-60)

---

## Phase 4: User Story 2 - Fix MCP Sync for All Project Directories

**Goal**: Ensure `/mcp sync` (or `/notes sync` after rename) indexes notes from all project directories (FF, 700B, etc.)

**Independent Test Criteria**:

- Run `/mcp sync` (or `/notes sync`), verify all project directories are scanned
- Run `/mcp list FF` (or `/notes list FF`), verify notes from `ff/` directory are shown
- Run `/mcp list 700B` (or `/notes list 700B`), verify notes from `700b/` directory are shown
- Verify `ProjectDirectoryMapper` correctly maps all project names to directory names

### Implementation for User Story 2

- [x] T016 [US2] Verify `NoteParser.find_notes()` in `src/services/note_parser.py` uses `rglob("*.md")` to recursively scan all subdirectories
- [x] T017 [US2] Verify `IndexBuilder.sync_and_rebuild()` in `src/services/index_builder.py` calls `find_notes()` correctly
- [x] T018 [US2] Verify `ProjectDirectoryMapper.get_directory()` in `src/services/project_filter.py` supports all projects (DAAS, THN, FF, General, 700B)
- [x] T019 [US2] Test that `NoteIndex.get_by_project()` in `src/models/index.py` correctly filters notes by project directory
- [x] T020 [US2] Test sync and verify notes from all project directories are indexed (FF, 700B, etc.)

---

## Phase 5: User Story 3 - Rename /mcp to /notes

**Goal**: Rename `/mcp` command to `/notes` for clarity. All functionality remains identical.

**Independent Test Criteria**:

- Type `/notes status`, verify it works (replaces `/mcp status`)
- Type `/notes list FF`, verify it shows FF directory notes
- Type `/notes list 700B`, verify it shows 700B directory notes
- Type `/notes sync`, verify it syncs repository
- Type `/mcp status`, verify it shows error or "unknown command"
- Verify all subcommands work: `status`, `list`, `read`, `search`, `sync`, `save`

### Implementation for User Story 3

- [x] T021 [US3] Rename `_handle_mcp_command()` to `_handle_notes_command()` in `chat_cli.py` (function definition, line ~678)
- [x] T022 [US3] Update command parsing in `handle_command()` in `chat_cli.py` to check `cmd == "notes"` instead of `cmd == "mcp"` (line ~570)
- [x] T023 [US3] Update handler call in `handle_command()` in `chat_cli.py` to call `_handle_notes_command()` instead of `_handle_mcp_command()` (line ~1448)
- [x] T024 [US3] Update function docstring for `_handle_notes_command()` in `chat_cli.py` to reference `/notes` command instead of `/mcp`
- [x] T025 [US3] Update help text in `_handle_notes_command()` in `chat_cli.py` to show `/notes` usage instead of `/mcp` (line ~691)
- [x] T026 [US3] Update user-facing error messages in `_handle_notes_command()` in `chat_cli.py` to reference "notes" instead of "MCP" (user-facing only, keep internal MCP references)
- [x] T027 [US3] Update status output in `_handle_notes_command()` in `chat_cli.py` to show "Notes Server Status:" instead of "MCP Server Status:" (line ~706)
- [x] T028 [US3] Update resource listing output in `_handle_notes_command()` in `chat_cli.py` to show "Notes" instead of "MCP Resources" (lines ~728, 735)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T029 [P] Verify RAG is never automatically included in system prompts (test THN and DAAS first messages)
- [x] T030 [P] Verify `/rag` command works for both THN and DAAS projects
- [x] T031 [P] Verify all `/notes` subcommands work correctly (`status`, `list`, `read`, `search`, `sync`, `save`)
- [x] T032 [P] Verify project filtering works for all projects (FF, 700B, DAAS, THN, General)
- [x] T033 [P] Run quickstart.md validation steps to ensure all requirements met
- [x] T034 [P] Verify no references to automatic RAG inclusion remain in code comments or docstrings
- [x] T035 [P] Verify no references to `/mcp` command remain in user-facing help text or error messages

---

## Parallel Execution Examples

### User Story 1 (Manual RAG Only)

Can be done independently. All tasks modify `brain_core/` files:

- T007-T010: Modify `context_builder.py` (can be done together)
- T011-T015: Modify `chat.py` (can be done together)

### User Story 2 (Fix MCP Sync)

Can be done independently. All tasks are verification/testing:

- T016-T020: Verification tasks (can be done in parallel)

### User Story 3 (Rename Command)

Should be done after US2. All tasks modify `chat_cli.py`:

- T021-T028: Sequential modifications to same file (should be done in order)

### Cross-Story Parallelism

- US1 and US2 can be done in parallel (different files)
- US3 should wait for US2 (both touch `chat_cli.py`)

---

## Notes

- All changes are modifications to existing files - no new modules required
- No database migrations required
- No new dependencies required
- Keep MCP API/server code unchanged (internal implementation)
- RAG generation functions (`build_thn_rag_context()`, `build_daas_rag_context()`) remain available for `/rag` command
