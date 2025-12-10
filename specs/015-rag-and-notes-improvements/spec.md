# RAG and Notes Improvements

## Overview

Three improvements to the project chat system:

1. Remove automatic RAG inclusion in system prompts - make RAG manual-only via `/rag` command
2. Fix `/mcp` sync to include all project directories (FF, 700B, etc.)
3. Rename `/mcp` command to `/notes` for clarity

## Requirements

### 1. Manual RAG Only

**Current Behavior:**

- THN RAG automatically included in system prompt on first message
- DAAS RAG automatically included when analysis intent detected

**New Behavior:**

- RAG is NEVER automatically included in system prompts
- RAG only available via manual `/rag` command
- `/rag` command works for both THN and DAAS projects

**Changes Required:**

- Remove automatic RAG inclusion logic from `build_project_system_prompt()`
- Remove automatic RAG inclusion logic from `chat_turn()` in `chat.py`
- Keep `/rag` command functionality intact
- Remove `should_include_daas_rag()` function (no longer needed)

### 2. Fix MCP Sync for All Project Directories

**Current Behavior:**

- `/mcp sync` may not be syncing notes from all project directories
- `/mcp list FF` should show notes from FF directory
- `/mcp list 700B` should show notes from 700B directory

**New Behavior:**

- `/mcp sync` (or `/notes sync` after rename) syncs ALL project directories
- `/mcp list FF` returns notes from `ff/` directory
- `/mcp list 700B` returns notes from `700b/` directory
- All project directories are indexed during sync

**Changes Required:**

- Verify `IndexBuilder.sync_and_rebuild()` scans all directories
- Ensure `ProjectDirectoryMapper` supports all project names (FF, 700B, etc.)
- Test that sync includes notes from all project directories

### 3. Rename /mcp to /notes

**Current Behavior:**

- Command is `/mcp` with subcommands: `status`, `list`, `read`, `search`, `sync`, `save`

**New Behavior:**

- Command is `/notes` with same subcommands
- All functionality remains identical
- Only command name changes

**Changes Required:**

- Rename command handler from `_handle_mcp_command` to `_handle_notes_command`
- Update command parsing in `handle_command()` function
- Update all user-facing help text and error messages
- Update any internal references to "mcp" in command context (keep MCP API/server code as-is)

## Technical Details

### RAG Removal

**Files to Modify:**

- `brain_core/context_builder.py`: Remove RAG inclusion in `build_project_system_prompt()`
- `brain_core/chat.py`: Remove RAG inclusion logic from `chat_turn()`
- `brain_core/context_builder.py`: Remove `should_include_daas_rag()` function

**Logic to Remove:**

- THN RAG inclusion check (first message)
- DAAS RAG inclusion check (analysis intent)
- `user_message_for_rag` parameter passing
- RAG-related logging in system prompt builder

**Logic to Keep:**

- `/rag` command in `chat_cli.py`
- `build_thn_rag_context()` and `build_daas_rag_context()` functions
- RAG generation functions remain available for manual use

### MCP Sync Fix

**Files to Review:**

- `src/services/index_builder.py`: Verify directory scanning logic
- `src/services/project_filter.py`: Verify project mapping
- `src/models/index.py`: Verify `get_by_project()` filtering

**Verification:**

- Ensure sync scans all subdirectories in repository
- Verify project name to directory mapping works for all projects
- Test that `list_resources_by_project()` returns correct notes

### Command Rename

**Files to Modify:**

- `chat_cli.py`: Rename command handler and update command parsing
- Update help text and error messages

**Naming:**

- Function: `_handle_mcp_command()` → `_handle_notes_command()`
- Command: `/mcp` → `/notes`
- Keep MCP API/server code unchanged (internal implementation)

## Success Criteria

1. ✅ RAG never automatically included in system prompts
2. ✅ `/rag` command works for THN and DAAS
3. ✅ `/notes sync` indexes all project directories
4. ✅ `/notes list FF` shows FF directory notes
5. ✅ `/notes list 700B` shows 700B directory notes
6. ✅ `/notes` command works identically to previous `/mcp` command
7. ✅ All functionality preserved after rename
