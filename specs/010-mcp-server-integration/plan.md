# Implementation Plan: MCP Server Integration

**Branch**: `010-mcp-server-integration` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-mcp-server-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate Model Context Protocol (MCP) server support into project_chat to enable access to external resources and tools. Initial integration supports the meditation MCP server, providing access to meditation notes stored in a GitLab repository. The integration uses JSON-RPC 2.0 over stdio for communication, supports resource discovery/retrieval and tool invocation, and integrates MCP resources into conversation context. Implementation includes MCP client with subprocess management, configuration system, CLI commands for manual MCP operations, and automatic context integration for project-specific MCP servers.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: Existing dependencies (psycopg2-binary, python-dotenv, openai, requests, gitpython), subprocess (stdlib), json (stdlib), asyncio (stdlib) or threading for async operations  
**Storage**: N/A (MCP resources cached in memory, no persistent storage required)  
**Testing**: Manual testing (consistent with project standards), integration tests for MCP client  
**Target Platform**: macOS/Linux (same as existing project)  
**Project Type**: Single project (CLI application with shared brain_core modules)  
**Performance Goals**: MCP resource retrieval <500ms, tool invocation <1s, graceful degradation on failures  
**Constraints**: Must not break existing functionality; handle MCP server failures gracefully; support async/background operations; cache MCP resources; respect rate limits  
**Scale/Scope**: Support multiple MCP servers (initially 1: meditation-notes); handle 100+ resources per server; support 10+ concurrent tool invocations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Phase 0**: Constitution file contains placeholders, so no blocking gates. This is an integration feature that extends existing functionality without breaking changes.

**Post-Phase 1**:

- ✅ Extends existing infrastructure (context building, CLI commands) rather than creating new systems
- ✅ Maintains simplicity: optional feature, graceful degradation if MCP unavailable
- ✅ Uses existing technologies (Python subprocess, JSON) with no new external dependencies
- ✅ No breaking changes to existing APIs or CLI commands
- ✅ Incremental enhancement to existing chat flow

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
brain_core/
├── mcp_client.py              # NEW - MCP client implementation
├── mcp_config.py              # NEW - MCP server configuration management
├── context_builder.py          # MODIFIED - integrate MCP resources into context
├── chat.py                    # MODIFIED - integrate MCP tools into chat flow
└── [other existing files]

chat_cli.py                    # MODIFIED - add /mcp command handler

config.py                      # MODIFIED - add MCP server configuration support

mcp_config.json                # NEW - MCP server configuration file (optional)
```

**Structure Decision**: Single project structure maintained. New MCP client module follows existing brain_core pattern. Configuration can be in config.py or separate JSON file. MCP client uses subprocess for stdio communication, with async support for non-blocking operations.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                      |
