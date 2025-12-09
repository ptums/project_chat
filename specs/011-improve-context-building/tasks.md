---
description: "Task list for Improve Context Building with Base System Prompt feature"
---

# Tasks: Improve Context Building with Base System Prompt

**Input**: Design documents from `/specs/011-improve-context-building/`
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

**Purpose**: Project initialization and basic structure

- [x] T001 Create base system prompt file at brain_core/base_system_prompt.txt with content from spec.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Implement load_base_system_prompt() function in brain_core/context_builder.py with file loading and caching
- [x] T003 Add error handling and fallback prompt in load_base_system_prompt() function in brain_core/context_builder.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Base System Prompt Integration (Priority: P1) 🎯 MVP

**Goal**: Base system prompt is loaded from file and applied to all conversations regardless of project

**Independent Test**: Start chat CLI, verify base system prompt is loaded and used in all conversations (general and project-specific). Check logs for file loading.

### Implementation for User Story 1

- [x] T004 [US1] Implement build_project_system_prompt(project: str) function in brain_core/context_builder.py that loads base prompt and returns it (no project extension yet)
- [x] T005 [US1] Update chat_turn() function in brain_core/chat.py to remove hardcoded base_system string (lines 75-89) and call build_project_system_prompt(project) instead
- [ ] T006 [US1] Verify base system prompt is applied to general conversations in brain_core/chat.py
- [ ] T007 [US1] Verify base system prompt is applied to all project conversations (THN, DAAS, FF, 700B) in brain_core/chat.py

**Checkpoint**: At this point, User Story 1 should be fully functional - base prompt loads from file and is used in all conversations

---

## Phase 4: User Story 2 - Project-Specific Context Extension (Priority: P1)

**Goal**: Project-specific context is appended to base system prompt when user is in a specific project

**Independent Test**: Switch to a project (e.g., /daas), verify system prompt includes base prompt + project extension with format "In this current conversation is tagged as project DAAS and here we are going to discuss <overview>." Switch to /general, verify only base prompt is used.

### Implementation for User Story 2

- [x] T008 [US2] Add project_knowledge overview retrieval logic to build_project_system_prompt() function in brain_core/context_builder.py
- [x] T009 [US2] Implement project extension format "In this current conversation is tagged as project <project_name> and here we are going to discuss <overview column from project_knowledge>." in build_project_system_prompt() function in brain_core/context_builder.py
- [x] T010 [US2] Ensure project extension is only appended when project != "general" in build_project_system_prompt() function in brain_core/context_builder.py
- [ ] T011 [US2] Test project extension with all project types (THN, DAAS, FF, 700B) in brain_core/context_builder.py
- [x] T012 [US2] Verify project extension uses overview from project_knowledge table with key='overview' in brain_core/context_builder.py
- [x] T013 [US2] Handle missing project_knowledge overview gracefully (omit extension, use base prompt only) in build_project_system_prompt() function in brain_core/context_builder.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - base prompt + project extensions are functional

---

## Phase 5: User Story 3 - Code Cleanup and RAG Separation (Priority: P2)

**Goal**: Remove hardcoded system prompts from THN/DAAS code paths and ensure RAG is only used for project-specific conversations

**Independent Test**: Verify no hardcoded system prompt text remains in context_builder.py for THN/DAAS. Verify RAG retrieval only happens when in project-specific conversations. Verify existing RAG functionality (DAAS dreams, THN code) still works.

### Implementation for User Story 3

- [x] T014 [US3] Review build_project_context() function in brain_core/context_builder.py to identify hardcoded prompt text in THN/DAAS code paths
- [x] T015 [US3] Remove any hardcoded system prompt text from DAAS retrieval section in build_project_context() function in brain_core/context_builder.py
- [x] T016 [US3] Remove any hardcoded system prompt text from THN retrieval section in build_project_context() function in brain_core/context_builder.py
- [x] T017 [US3] Ensure build_project_context() returns only RAG context (no system prompt) in brain_core/context_builder.py
- [ ] T018 [US3] Verify RAG retrieval logic is only executed for project-specific conversations (not general) in build_project_context() function in brain_core/context_builder.py
- [ ] T019 [US3] Test DAAS dream retrieval still works correctly after cleanup in brain_core/context_builder.py
- [ ] T020 [US3] Test THN code retrieval still works correctly after cleanup in brain_core/context_builder.py
- [x] T021 [US3] Verify message order in chat_turn() function: system prompt (base + project extension) → RAG context → note reads → history in brain_core/chat.py

**Checkpoint**: All user stories should now be independently functional - code is clean, RAG separated from system prompts

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T022 [P] Add logging for base system prompt loading in load_base_system_prompt() function in brain_core/context_builder.py
- [x] T023 [P] Add logging for project extension composition in build_project_system_prompt() function in brain_core/context_builder.py
- [ ] T024 [P] Verify error handling works correctly when base_system_prompt.txt is missing in brain_core/context_builder.py
- [ ] T025 [P] Verify error handling works correctly when project_knowledge overview is missing in brain_core/context_builder.py
- [ ] T026 Test with all project types (THN, DAAS, FF, 700B, general) to ensure backward compatibility
- [ ] T027 Run quickstart.md validation steps to verify implementation matches documentation
- [ ] T028 Verify system prompt caching works correctly (file loaded once, reused) in brain_core/context_builder.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 (uses build_project_system_prompt function)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 (cleanup requires new system to be in place)

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority
- Manual testing after each story completion

### Parallel Opportunities

- All Setup tasks can run in parallel (only one task in this phase)
- Foundational tasks T002 and T003 can run in parallel (different concerns: loading vs error handling)
- Once Foundational phase completes, US1 and US2 can start (US2 depends on US1 function, but can be worked on together)
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational tasks together:
Task: "Implement load_base_system_prompt() function in brain_core/context_builder.py with file loading and caching"
Task: "Add error handling and fallback prompt in load_base_system_prompt() function in brain_core/context_builder.py"
```

---

## Parallel Example: User Story 2

```bash
# After US1 is complete, these US2 tasks can be worked on together:
Task: "Add project_knowledge overview retrieval logic to build_project_system_prompt() function in brain_core/context_builder.py"
Task: "Test project extension with all project types (THN, DAAS, FF, 700B) in brain_core/context_builder.py"
Task: "Handle missing project_knowledge overview gracefully (omit extension, use base prompt only) in build_project_system_prompt() function in brain_core/context_builder.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (create base_system_prompt.txt)
2. Complete Phase 2: Foundational (load function with error handling)
3. Complete Phase 3: User Story 1 (base prompt integration)
4. **STOP and VALIDATE**: Test base prompt loads and is used in all conversations
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - base prompt working!)
3. Add User Story 2 → Test independently → Deploy/Demo (project extensions working!)
4. Add User Story 3 → Test independently → Deploy/Demo (code cleanup complete)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (base prompt integration)
   - Developer B: Can help with US1 or prepare for US2
3. Once US1 is complete:
   - Developer A: User Story 2 (project extensions)
   - Developer B: User Story 3 (code cleanup)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing after each task or logical group
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks include explicit file paths for clarity
- No automated tests per project standards (manual testing only)
