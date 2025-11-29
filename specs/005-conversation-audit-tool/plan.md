# Implementation Plan: Conversation Audit Tool

**Branch**: `005-conversation-audit-tool` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-conversation-audit-tool/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a CLI tool (`audit_conversations.py`) for managing and cleaning up conversation history. Users can list conversations by project, ID, or title; review message history; and edit conversation titles/projects or delete conversations. This tool helps clean up misclassified conversations and optimize the conversation index database.

**Technical Approach**: 
- Create standalone CLI script with interactive menu system
- Query PostgreSQL database for conversations and messages
- Support read operations (list, view) and write operations (edit, delete)
- Ensure data consistency between `conversations` and `conversation_index` tables using transactions
- Use parameterized queries for all database operations
- Reuse existing database connection and configuration from `brain_core`

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: psycopg2 (PostgreSQL), existing `brain_core.db` and `brain_core.config` modules  
**Storage**: PostgreSQL (conversations, messages, conversation_index tables)  
**Testing**: Manual testing via CLI (pytest optional for unit tests)  
**Target Platform**: CLI application (Linux/macOS/Windows)  
**Project Type**: Single CLI application  
**Performance Goals**: List queries should complete in under 2 seconds, individual conversation lookups in under 1 second  
**Constraints**: Must maintain data consistency, use parameterized queries, handle database errors gracefully  
**Scale/Scope**: Single-user application, handles hundreds of conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality
- ✅ **Readability First**: CLI interface with clear menu options and commands
- ✅ **Type Hints**: Use type hints for function signatures
- ✅ **Single Responsibility**: Separate functions for listing, viewing, editing, deleting

### Accuracy
- ✅ **Error Handling**: Handle database errors, invalid inputs, missing conversations
- ✅ **Data Validation**: Validate project names, non-empty titles, valid UUIDs
- ✅ **State Consistency**: Update both `conversations` and `conversation_index` when editing project

### Rapid Development
- ✅ **Pragmatic Over Perfect**: Simple CLI with basic menu system, no complex UI
- ✅ **Simple Solutions**: Reuse existing database connection and query patterns

### Personal Use Context
- ✅ **No Multi-Tenancy**: Single user, no additional complexity needed
- ✅ **Direct Configuration**: Reuse existing database configuration from `brain_core.config`

**GATE STATUS**: ✅ PASS - All constitution checks pass. Implementation is straightforward and follows existing patterns.

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
audit_conversations.py          # Main CLI script for conversation audit tool
brain_core/
├── db.py                      # Database operations - reuse get_conn()
└── config.py                  # Database configuration - reuse DB_CONFIG
```

**Structure Decision**: Single CLI application. New standalone script `audit_conversations.py` at repository root:
- Reuses existing database connection from `brain_core.db`
- Reuses database configuration from `brain_core.config`
- Implements interactive CLI menu system
- Handles all conversation management operations

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
