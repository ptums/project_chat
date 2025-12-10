# Implementation Plan: RAG and Notes Improvements

**Branch**: `015-rag-and-notes-improvements` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-rag-and-notes-improvements/spec.md`

## Summary

Three improvements to the project chat system:

1. Remove automatic RAG inclusion in system prompts - make RAG manual-only via `/rag` command
2. Fix `/mcp` sync to include all project directories (FF, 700B, etc.)
3. Rename `/mcp` command to `/notes` for clarity

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: Existing dependencies (psycopg2, OpenAI, pgvector)  
**Storage**: PostgreSQL with `conversation_index` table (existing schema)  
**Testing**: Manual testing (consistent with project standards)  
**Target Platform**: Linux/macOS CLI application  
**Project Type**: Single project (Python CLI)  
**Performance Goals**: No performance impact (removing code, renaming commands)  
**Constraints**:

- Must preserve `/rag` command functionality
- Must preserve all MCP/notes functionality (only rename command)
- No breaking changes to existing API or database schema
- Backward compatibility: old `/mcp` command should not break (will be removed)

**Scale/Scope**:

- Three independent changes (can be implemented separately)
- Affects: `brain_core/context_builder.py`, `brain_core/chat.py`, `chat_cli.py`, `src/services/index_builder.py`
- No database migrations required
- No new dependencies required

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

No constitution violations identified. This feature:

- Removes code (simplification)
- Renames command (clarity improvement)
- Fixes existing functionality (bug fix)
- No breaking changes to core functionality
- Maintains separation of concerns

## Project Structure

### Documentation (this feature)

```text
specs/015-rag-and-notes-improvements/
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
├── context_builder.py    # Modify: Remove automatic RAG inclusion, remove should_include_daas_rag()
└── chat.py              # Modify: Remove automatic RAG inclusion logic

chat_cli.py              # Modify: Rename /mcp to /notes, update handler name

src/services/
└── index_builder.py     # Review: Verify sync scans all directories
```

**Structure Decision**: Single project structure. All changes are modifications to existing files. No new modules required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.

## Phase 0: Research & Design Decisions ✅

**Status**: Complete - See `research.md` for all decisions.

### Research Tasks

1. **RAG Removal Scope**

   - Research: What code paths automatically include RAG in system prompts?
   - Decision: Remove RAG inclusion from `build_project_system_prompt()` and `chat_turn()`
   - Rationale: Keep RAG generation functions available for `/rag` command, just remove automatic inclusion

2. **MCP Sync Directory Scanning**

   - Research: How does `NoteParser.find_notes()` discover notes? Does it scan all subdirectories?
   - Decision: Verify `find_notes()` recursively scans all directories
   - Rationale: Need to ensure all project directories (ff/, 700b/, etc.) are indexed

3. **Command Rename Impact**

   - Research: Where is `/mcp` command referenced?
   - Decision: Rename command handler and update command parsing
   - Rationale: Keep MCP API/server code unchanged (internal implementation)

4. **Project Directory Mapping**
   - Research: Does `ProjectDirectoryMapper` support all project names (FF, 700B)?
   - Decision: Verify mapping includes all projects
   - Rationale: Need to ensure `/notes list FF` and `/notes list 700B` work correctly

## Phase 1: Design & Contracts ✅

**Status**: Complete - See `data-model.md`, `contracts/api.md`, and `quickstart.md`.

### Data Model

**No Schema Changes Required**

- Existing `conversation_index` table unchanged
- Existing note index structure unchanged
- No new entities required

### API Contracts

**Function: `build_project_system_prompt(project: str, user_message: str = "") -> str`**

- **Location**: `brain_core/context_builder.py`
- **Purpose**: Build system prompt WITHOUT automatic RAG inclusion
- **Input**: Project name, optional user message (ignored for RAG purposes)
- **Output**: System prompt string (base + project extension, NO RAG)
- **Behavior**:
  - Load base system prompt
  - Add project overview and rules
  - DO NOT include RAG context automatically
  - RAG only available via `/rag` command

**Function: `chat_turn(conversation_id, user_text: str, project: str, stream: bool = False)`**

- **Location**: `brain_core/chat.py`
- **Purpose**: Handle chat turn WITHOUT automatic RAG inclusion
- **Input**: Conversation ID, user text, project, stream flag
- **Output**: Chat response
- **Behavior**:
  - Build system prompt WITHOUT RAG
  - DO NOT check for first message or analysis intent
  - RAG only available via `/rag` command

**Command: `/notes [subcommand]`**

- **Location**: `chat_cli.py`
- **Purpose**: Access notes from Obsidian notebook (renamed from `/mcp`)
- **Subcommands**: `status`, `list [project]`, `read <uri>`, `search <query>`, `sync`, `save [title]`
- **Behavior**: Identical to previous `/mcp` command, only name changed

### Quickstart Guide

**For Developers:**

1. **Remove Automatic RAG:**

   - Remove RAG inclusion from `build_project_system_prompt()` in `context_builder.py`
   - Remove RAG inclusion logic from `chat_turn()` in `chat.py`
   - Remove `should_include_daas_rag()` function
   - Keep `build_thn_rag_context()` and `build_daas_rag_context()` for `/rag` command

2. **Fix MCP Sync:**

   - Verify `NoteParser.find_notes()` scans all subdirectories
   - Test that sync indexes notes from all project directories
   - Verify `ProjectDirectoryMapper` supports all projects

3. **Rename Command:**
   - Rename `_handle_mcp_command()` to `_handle_notes_command()` in `chat_cli.py`
   - Update command parsing: `cmd == "mcp"` → `cmd == "notes"`
   - Update help text and error messages
   - Keep MCP API/server code unchanged

**For Users:**

- Use `/rag` command to manually include RAG context when needed
- Use `/notes sync` to sync all project directories
- Use `/notes list FF` to see notes from FF directory
- Use `/notes list 700B` to see notes from 700B directory
