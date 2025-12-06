# Tasks: MCP Server Integration

**Input**: Design documents from `/specs/010-mcp-server-integration/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Manual testing only (as per project standards)

**Organization**: Tasks are grouped by requirement to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which requirement this task belongs to (e.g., R1, R2, R3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify Python 3.10+ and required dependencies are available
- [X] T002 [P] Create brain_core/mcp_client.py module structure with imports
- [X] T003 [P] Create brain_core/mcp_config.py module structure with imports
- [X] T004 Verify subprocess and json modules are available (stdlib)

---

## Phase 2: Foundational - MCP Client Infrastructure (Blocking Prerequisites)

**Purpose**: Core MCP client that MUST be complete before ANY other MCP features can be implemented

**⚠️ CRITICAL**: No MCP feature work can begin until this phase is complete

- [X] T005 Create MCPClient class structure in brain_core/mcp_client.py with basic initialization
- [X] T006 Implement subprocess management in MCPClient (start, stop, restart on failure) in brain_core/mcp_client.py
- [X] T007 Implement JSON-RPC request/response handling in MCPClient in brain_core/mcp_client.py
- [X] T008 Implement initialize method in MCPClient to negotiate protocol version in brain_core/mcp_client.py
- [X] T009 Implement error handling and timeout support in MCPClient in brain_core/mcp_client.py
- [X] T010 Implement process health checks and automatic restart with backoff in brain_core/mcp_client.py
- [X] T011 Implement graceful shutdown handling for MCP server processes in brain_core/mcp_client.py

**Checkpoint**: Foundation ready - MCP client can communicate with servers, other features can now begin

---

## Phase 3: Requirement 1 - Configuration Management (Priority: P1) 🎯 MVP

**Goal**: Add MCP server configuration system to project_chat

**Independent Test**: Load MCP configuration from file or environment, verify configuration is accessible

### Implementation for Requirement 1

- [X] T012 [R1] Create load_mcp_config function in brain_core/mcp_config.py to read mcp_config.json
- [X] T013 [R1] Implement environment variable support for MCP configuration in brain_core/mcp_config.py
- [X] T014 [R1] Add MCP server configuration support to config.py (fallback if JSON not present)
- [X] T015 [R1] Implement server-specific environment variable resolution in brain_core/mcp_config.py
- [X] T016 [R1] Create MCPConfig class to manage server configurations in brain_core/mcp_config.py
- [X] T017 [R1] Implement configuration validation (command, args, env) in brain_core/mcp_config.py
- [X] T018 [R1] Add project-to-server mapping support in MCPConfig in brain_core/mcp_config.py

**Checkpoint**: At this point, Requirement 1 should be complete with configuration system functional

---

## Phase 4: Requirement 2 - Resource Discovery and Retrieval (Priority: P1) 🎯 MVP

**Goal**: Support listing and reading MCP resources

**Independent Test**: Connect to MCP server, list resources, read a resource, verify content returned

### Implementation for Requirement 2

- [X] T019 [R2] Implement resources/list method in MCPClient in brain_core/mcp_client.py
- [X] T020 [R2] Implement resources/read method in MCPClient in brain_core/mcp_client.py
- [X] T021 [R2] Implement resource caching with TTL in MCPClient in brain_core/mcp_client.py
- [X] T022 [R2] Implement resource list caching with TTL in MCPClient in brain_core/mcp_client.py
- [X] T023 [R2] Add cache invalidation logic in MCPClient in brain_core/mcp_client.py
- [X] T024 [R2] Implement error handling for resource not found in MCPClient in brain_core/mcp_client.py

**Checkpoint**: At this point, Requirement 2 should be complete with resource operations functional

---

## Phase 5: Requirement 3 - Tool Invocation (Priority: P1) 🎯 MVP

**Goal**: Support calling MCP tools (search_notes, sync_repository)

**Independent Test**: List available tools, call search_notes tool, verify results returned

### Implementation for Requirement 3

- [X] T025 [R3] Implement tools/list method in MCPClient in brain_core/mcp_client.py
- [X] T026 [R3] Implement tools/call method in MCPClient in brain_core/mcp_client.py
- [X] T027 [R3] Add tool argument validation in MCPClient in brain_core/mcp_client.py
- [X] T028 [R3] Implement error handling for tool not found in MCPClient in brain_core/mcp_client.py
- [X] T029 [R3] Add timeout handling for tool invocations in MCPClient in brain_core/mcp_client.py

**Checkpoint**: At this point, Requirement 3 should be complete with tool operations functional

---

## Phase 6: Requirement 4 - Context Integration (Priority: P2)

**Goal**: Automatically include MCP resources in conversation context

**Independent Test**: Start chat in DAAS project, mention meditation topic, verify MCP resources included in context

### Implementation for Requirement 4

- [X] T030 [R4] Add get_mcp_resources_for_project function in brain_core/mcp_config.py
- [X] T031 [R4] Implement MCP resource retrieval in context_builder.py for project-specific servers
- [X] T032 [R4] Add keyword matching logic to identify relevant MCP resources in context_builder.py
- [X] T033 [R4] Implement background thread loading for MCP resources in context_builder.py
- [X] T034 [R4] Add MCP context to conversation messages in brain_core/chat.py
- [X] T035 [R4] Implement graceful degradation when MCP unavailable in context_builder.py
- [X] T036 [R4] Add logging for MCP context integration in context_builder.py

**Checkpoint**: At this point, Requirement 4 should be complete with automatic context integration functional

---

## Phase 7: Requirement 5 - CLI Integration (Priority: P2)

**Goal**: Add /mcp command for manual MCP operations

**Independent Test**: Run /mcp status, /mcp list, /mcp read, /mcp search, /mcp sync commands, verify output

### Implementation for Requirement 5

- [X] T037 [R5] Add /mcp command handler in handle_command function in chat_cli.py
- [X] T038 [R5] Implement /mcp status command to show server status in chat_cli.py
- [X] T039 [R5] Implement /mcp list command to list resources in chat_cli.py
- [X] T040 [R5] Implement /mcp read command to read a resource in chat_cli.py
- [X] T041 [R5] Implement /mcp search command to search resources in chat_cli.py
- [X] T042 [R5] Implement /mcp sync command to sync repositories in chat_cli.py
- [X] T043 [R5] Add error message formatting for MCP commands in chat_cli.py
- [X] T044 [R5] Implement output formatting for MCP command results in chat_cli.py

**Checkpoint**: At this point, Requirement 5 should be complete with CLI commands functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and improvements

- [X] T045 [P] Add comprehensive error handling throughout MCP client in brain_core/mcp_client.py
- [X] T046 [P] Add logging for MCP operations in brain_core/mcp_client.py
- [X] T047 [P] Add type hints to all MCP functions in brain_core/mcp_client.py
- [X] T048 [P] Add type hints to all MCP config functions in brain_core/mcp_config.py
- [X] T049 [P] Update function docstrings with comprehensive documentation in brain_core/mcp_client.py
- [X] T050 [P] Update function docstrings with comprehensive documentation in brain_core/mcp_config.py
- [X] T051 Code cleanup and refactoring in brain_core/mcp_client.py
- [X] T052 Code cleanup and refactoring in brain_core/mcp_config.py
- [X] T053 Verify graceful degradation when MCP servers unavailable
- [ ] T054 Test with meditation MCP server end-to-end
- [ ] T055 Run quickstart.md validation scenarios
- [X] T056 Verify backward compatibility with existing chat flows

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all MCP features
- **Requirement 1 (Phase 3)**: Depends on Foundational completion - can proceed independently
- **Requirement 2 (Phase 4)**: Depends on Foundational completion - can proceed independently
- **Requirement 3 (Phase 5)**: Depends on Foundational completion - can proceed independently
- **Requirement 4 (Phase 6)**: Depends on Requirements 1, 2, 3 completion
- **Requirement 5 (Phase 7)**: Depends on Requirements 1, 2, 3 completion
- **Polish (Phase 8)**: Depends on all requirements being complete

### Requirement Dependencies

- **Requirement 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other requirements
- **Requirement 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other requirements
- **Requirement 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other requirements
- **Requirement 4 (P2)**: Depends on Requirements 1, 2, 3 - Needs config, resources, and tools
- **Requirement 5 (P2)**: Depends on Requirements 1, 2, 3 - Needs config, resources, and tools

### Within Each Requirement

- Configuration loading before validation
- Resource operations before caching
- Tool operations before integration
- Core implementation before CLI integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks can run sequentially (process management dependencies)
- Requirements 1, 2, 3 can be worked on in parallel after Foundational
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: Requirements 1, 2, 3

```bash
# After Foundational phase, these can be developed in parallel:
Task: "Create load_mcp_config function in brain_core/mcp_config.py"
Task: "Implement resources/list method in MCPClient in brain_core/mcp_client.py"
Task: "Implement tools/list method in MCPClient in brain_core/mcp_client.py"
```

---

## Implementation Strategy

### MVP First (Requirements 1, 2, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all features)
3. Complete Phase 3: Requirement 1 (Configuration Management)
4. Complete Phase 4: Requirement 2 (Resource Discovery)
5. Complete Phase 5: Requirement 3 (Tool Invocation)
6. **STOP and VALIDATE**: Test MCP client with meditation server manually
7. Add Requirements 4 & 5 for full integration

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add Requirement 1 → Test configuration loading → Commit
3. Add Requirement 2 → Test resource operations → Commit
4. Add Requirement 3 → Test tool operations → Commit
5. Add Requirement 4 → Test context integration → Commit
6. Add Requirement 5 → Test CLI commands → Commit
7. Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Requirement 1 (Configuration)
   - Developer B: Requirement 2 (Resources)
   - Developer C: Requirement 3 (Tools)
3. After Requirements 1, 2, 3 complete:
   - Developer A: Requirement 4 (Context Integration)
   - Developer B: Requirement 5 (CLI Integration)
4. Team collaborates on Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific requirement for traceability
- Each requirement should be independently completable and testable
- Manual testing only (as per project standards)
- Commit after each requirement or logical group
- Stop at any checkpoint to validate requirement independently
- Avoid: vague tasks, same file conflicts, cross-requirement dependencies that break independence

---

## Task Summary

**Total Tasks**: 56

**Tasks by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational - MCP Client Infrastructure): 7 tasks
- Phase 3 (Requirement 1 - Configuration Management): 7 tasks
- Phase 4 (Requirement 2 - Resource Discovery): 6 tasks
- Phase 5 (Requirement 3 - Tool Invocation): 5 tasks
- Phase 6 (Requirement 4 - Context Integration): 7 tasks
- Phase 7 (Requirement 5 - CLI Integration): 8 tasks
- Phase 8 (Polish): 12 tasks

**Tasks by Requirement**:
- R1 (Configuration): 7 tasks
- R2 (Resources): 6 tasks
- R3 (Tools): 5 tasks
- R4 (Context): 7 tasks
- R5 (CLI): 8 tasks

**Parallel Opportunities**: 20 tasks marked [P]

**Suggested MVP Scope**: Requirements 1, 2, 3 (Configuration, Resources, Tools) - 18 tasks total

**Independent Test Criteria**:
- R1: Load MCP configuration from file or environment, verify configuration is accessible
- R2: Connect to MCP server, list resources, read a resource, verify content returned
- R3: List available tools, call search_notes tool, verify results returned
- R4: Start chat in DAAS project, mention meditation topic, verify MCP resources included in context
- R5: Run /mcp status, /mcp list, /mcp read, /mcp search, /mcp sync commands, verify output

