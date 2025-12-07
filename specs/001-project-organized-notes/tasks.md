# Tasks: Project-Organized Meditation Notes Integration

**Input**: Design documents from `/specs/001-project-organized-notes/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in the feature specification, so test tasks are not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify existing MCP server structure in src/models/, src/services/, src/mcp/
- [x] T002 Verify existing dependencies (GitPython, python-frontmatter) in requirements.txt
- [x] T003 [P] Review existing Note, Repository, and NoteIndex models for extension points

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [US3] Create ProjectDirectoryMapper class in src/services/project_filter.py with mapping dictionary
- [x] T005 [US3] Implement get_directory(project: str) method in src/services/project_filter.py
- [x] T006 [US3] Implement is_valid_project(project: str) method in src/services/project_filter.py

**Checkpoint**: Foundation ready - project directory mapping available for all user stories

---

## Phase 3: User Story 1 - Project-Scoped Note Retrieval and Recall (Priority: P1) 🎯 MVP

**Goal**: Enable project-scoped meditation note retrieval and natural recall/referencing throughout conversations

**Independent Test**: Set project context to "DAAS", ask "What did I write about morning routines?", verify system recalls and references relevant content from "daas" directory notes

### Implementation for User Story 1

- [x] T007 [P] [US1] Add project_directory property to Note model in src/models/note.py (extract from file_path)
- [x] T008 [P] [US1] Add get_by_project(project: str) method to NoteIndex in src/models/index.py
- [x] T009 [P] [US1] Add search_by_project(project: str, query: str, limit: int) method to NoteIndex in src/models/index.py
- [x] T010 [US1] Add list_resources_by_project(project: str) method to MCPApi in src/mcp/api.py (uses ProjectDirectoryMapper and NoteIndex.get_by_project)
- [x] T011 [US1] Add get_project_notes(project: str, user_message: str, limit: int) method to MCPApi in src/mcp/api.py (uses NoteIndex.search_by_project)
- [x] T012 [US1] Update ResourcesHandler.list_resources() in src/mcp/resources.py to support optional project filter parameter
- [x] T013 [US1] Integrate project-scoped note retrieval into build_project_context() in brain_core/context_builder.py
- [x] T014 [US1] Add MCP note context to conversation context when project-scoped notes are available
- [x] T015 [US1] Update context messages to emphasize natural recall and referencing of note content

**Checkpoint**: At this point, User Story 1 should be fully functional - project-scoped notes are retrieved and included in conversation context, and system can recall/reference them naturally

---

## Phase 4: User Story 2 - Save Conversation as Note (Priority: P1)

**Goal**: Enable saving conversations as markdown notes in the appropriate project directory with Git commit/push

**Independent Test**: Run `/mcp save "Test Title"` in a DAAS conversation, verify markdown file created in "daas/" directory and pushed to repository

### Implementation for User Story 2

- [x] T016 [P] [US2] Create ConversationNote class in src/services/note_saver.py with title, project, messages, created_at, metadata fields
- [x] T017 [P] [US2] Implement to_markdown() method in ConversationNote in src/services/note_saver.py (Obsidian format with YAML frontmatter)
- [x] T018 [P] [US2] Implement generate_filename() method in ConversationNote in src/services/note_saver.py (slug from title or timestamp fallback)
- [x] T019 [US2] Create NoteSaver service class in src/services/note_saver.py with save_conversation() method
- [x] T020 [US2] Implement file creation logic in NoteSaver.save_conversation() in src/services/note_saver.py (create project directory if needed)
- [x] T021 [US2] Implement Git commit logic in NoteSaver.save_conversation() in src/services/note_saver.py (add, commit with descriptive message)
- [x] T022 [US2] Implement Git push logic in NoteSaver.save_conversation() in src/services/note_saver.py (handle sync, merge conflicts, errors)
- [x] T023 [US2] Add save_conversation() method to MCPApi in src/mcp/api.py (wraps NoteSaver)
- [x] T024 [US2] Add save_conversation tool handler to ToolsHandler in src/mcp/tools.py
- [x] T025 [US2] Register save_conversation tool in MCP server in src/mcp/server.py
- [x] T026 [US2] Implement /mcp save command handler in chat_cli.py (collects conversation messages, calls MCPApi.save_conversation)
- [x] T027 [US2] Add conversation message collection logic in chat_cli.py (loads messages from database for current conversation)
- [x] T028 [US2] Update saved note in NoteIndex after successful save in src/mcp/api.py

**Checkpoint**: At this point, User Story 2 should be fully functional - conversations can be saved as notes in project directories and pushed to repository

---

## Phase 5: User Story 3 - Project Directory Mapping (Priority: P2)

**Goal**: Ensure correct mapping between project names and directory names

**Independent Test**: Verify ProjectDirectoryMapper correctly translates "DAAS" → "daas", "THN" → "thn", "General" → "general", "700B" → "700b"

### Implementation for User Story 3

**Note**: This story is mostly complete in Phase 2 (T004-T006), but needs integration and validation

- [ ] T029 [US3] Add unit tests for ProjectDirectoryMapper.get_directory() with all 5 project types
- [ ] T030 [US3] Add unit tests for ProjectDirectoryMapper.is_valid_project() with valid and invalid projects
- [x] T031 [US3] Integrate ProjectDirectoryMapper into NoteIndex.get_by_project() in src/models/index.py
- [x] T032 [US3] Integrate ProjectDirectoryMapper into NoteSaver.save_conversation() in src/services/note_saver.py
- [x] T033 [US3] Add error handling for unmapped projects (default to lowercase or "general")

**Checkpoint**: At this point, User Story 3 should be fully functional - all project mappings work correctly and handle edge cases

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T034 [P] Update quickstart.md with project-organized notes examples
- [x] T035 [P] Add error handling for Git operations (permissions, disk space, network issues)
- [x] T036 [P] Add logging for note save operations in src/services/note_saver.py
- [x] T037 [P] Add validation for conversation message format before saving
- [x] T038 [P] Handle duplicate note filenames (append number: conversation-title-2.md)
- [x] T039 [P] Add repository sync check before saving (pull if out of sync)
- [x] T040 [P] Update documentation in specs/001-project-organized-notes/ with implementation notes
- [ ] T041 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) and User Story 2 (P1) can proceed in parallel after Foundational
  - User Story 3 (P2) depends on Foundational and integrates with US1/US2
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent from US1, but both are P1 priority
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before API/MCP integration
- API/MCP integration before CLI integration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- T007, T008, T009 (US1 models) can run in parallel
- T016, T017, T018 (US2 ConversationNote) can run in parallel
- T010, T011 (US1 MCP API methods) can run in parallel after models
- T023, T024, T025 (US2 MCP integration) can run in parallel after NoteSaver
- User Story 1 and User Story 2 can be worked on in parallel after Foundational phase
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all model extensions for User Story 1 together:
Task: "Add project_directory property to Note model in src/models/note.py"
Task: "Add get_by_project(project: str) method to NoteIndex in src/models/index.py"
Task: "Add search_by_project(project: str, query: str, limit: int) method to NoteIndex in src/models/index.py"

# Then launch MCP API methods together:
Task: "Add list_resources_by_project(project: str) method to MCPApi in src/mcp/api.py"
Task: "Add get_project_notes(project: str, user_message: str, limit: int) method to MCPApi in src/mcp/api.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch ConversationNote implementation together:
Task: "Create ConversationNote class in src/services/note_saver.py"
Task: "Implement to_markdown() method in ConversationNote in src/services/note_saver.py"
Task: "Implement generate_filename() method in ConversationNote in src/services/note_saver.py"

# Then launch MCP integration together:
Task: "Add save_conversation() method to MCPApi in src/mcp/api.py"
Task: "Add save_conversation tool handler to ToolsHandler in src/mcp/tools.py"
Task: "Register save_conversation tool in MCP server in src/mcp/server.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently - verify project-scoped note retrieval and recall work
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - project-scoped notes!)
3. Add User Story 2 → Test independently → Deploy/Demo (Complete loop - save conversations!)
4. Add User Story 3 → Test independently → Deploy/Demo (Polish - mapping validation)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (project-scoped retrieval)
   - Developer B: User Story 2 (save conversations)
3. Both complete independently, then integrate
4. Developer C: User Story 3 (mapping validation) can start after US1/US2 or in parallel

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- User Story 1 and User Story 2 are both P1 - can be prioritized based on immediate need
- User Story 3 is P2 - can be done after P1 stories or in parallel if team capacity allows
