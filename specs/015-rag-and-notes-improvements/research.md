# Research: RAG and Notes Improvements

## Research Questions

### 1. RAG Removal Scope

**Question**: What code paths automatically include RAG in system prompts?

**Findings**:

- `build_project_system_prompt()` in `context_builder.py` includes THN RAG when `user_message` is provided (first message)
- `build_project_system_prompt()` includes DAAS RAG when `user_message` indicates analysis intent
- `chat_turn()` in `chat.py` passes `user_text` to `build_project_system_prompt()` conditionally
- `/rag` command in `chat_cli.py` manually calls RAG generation functions

**Decision**: Remove RAG inclusion from `build_project_system_prompt()` and `chat_turn()`. Keep RAG generation functions (`build_thn_rag_context()`, `build_daas_rag_context()`) for `/rag` command use.

**Rationale**:

- Simplifies system prompt building
- Gives user explicit control over RAG inclusion
- Reduces token usage by default
- Maintains RAG functionality for manual use

**Alternatives Considered**:

- Keep automatic RAG but make it opt-out: More complex, user might forget to opt-out
- Remove RAG entirely: Too restrictive, user wants manual control

### 2. MCP Sync Directory Scanning

**Question**: How does `NoteParser.find_notes()` discover notes? Does it scan all subdirectories?

**Findings**:

- `NoteParser.find_notes()` uses `Path.rglob("*.md")` to recursively find all markdown files
- `rglob()` recursively searches all subdirectories
- `IndexBuilder.rebuild_index()` calls `NoteParser.find_notes()` with repository path and notes directory
- Repository `notes_dir` property returns either `notes/` subdirectory or repository root

**Decision**: Verify that `find_notes()` recursively scans all directories. If notes are in project subdirectories (e.g., `ff/`, `700b/`), they should be discovered.

**Rationale**:

- `rglob()` should find all `.md` files recursively
- Need to verify notes are in expected directory structure
- May need to check if notes are in `notes/` subdirectory or repository root

**Alternatives Considered**:

- Explicitly list project directories: More complex, requires maintenance
- Use glob patterns: Already handled by `rglob()`

### 3. Command Rename Impact

**Question**: Where is `/mcp` command referenced?

**Findings**:

- Command parsing in `handle_command()` function checks `cmd == "mcp"`
- Handler function `_handle_mcp_command()` processes subcommands
- Help text references `/mcp` command
- Error messages reference "MCP" in user-facing text

**Decision**: Rename command handler and update command parsing. Keep MCP API/server code unchanged (internal implementation).

**Rationale**:

- Command name is user-facing, should be clear
- MCP is internal protocol name, not user-facing
- `/notes` is more intuitive for users
- Internal MCP code can stay as-is

**Alternatives Considered**:

- Keep `/mcp` but add alias `/notes`: More complex, two commands to maintain
- Rename everything including internal code: Unnecessary, MCP is accurate internal name

### 4. Project Directory Mapping

**Question**: Does `ProjectDirectoryMapper` support all project names (FF, 700B)?

**Findings**:

- `ProjectDirectoryMapper` has explicit mapping for: DAAS, THN, FF, General, 700B
- `get_directory()` method handles case variations
- Falls back to lowercase if no explicit mapping
- `get_by_project()` in `NoteIndex` uses mapper to filter notes

**Decision**: Verify mapping works for all projects. Test that `/notes list FF` and `/notes list 700B` return correct notes.

**Rationale**:

- Mapping exists for all projects
- Need to verify directory names match (e.g., `700B` → `700b`)
- Need to verify notes are in correct directories in repository

**Alternatives Considered**:

- Add more explicit mappings: Already handled by fallback
- Case-insensitive directory matching: Already handled by mapper

## Implementation Notes

### RAG Removal

**Code to Remove**:

1. In `build_project_system_prompt()`:

   - THN RAG inclusion block (lines ~137-152)
   - DAAS RAG inclusion block (lines ~154-172)
   - `user_message` parameter usage for RAG

2. In `chat_turn()`:

   - `include_thn_rag` and `include_daas_rag` logic
   - `user_message_for_rag` parameter passing
   - RAG-related logging

3. In `context_builder.py`:
   - `should_include_daas_rag()` function (entire function)

**Code to Keep**:

- `build_thn_rag_context()` function
- `build_daas_rag_context()` function
- `/rag` command handler in `chat_cli.py`

### MCP Sync Fix

**Verification Steps**:

1. Check that `NoteParser.find_notes()` uses `rglob()` recursively
2. Verify repository structure has notes in project directories
3. Test that sync indexes notes from all directories
4. Verify `ProjectDirectoryMapper` mapping for all projects

**Potential Issues**:

- Notes might be in `notes/` subdirectory, not repository root
- Directory names might not match project names exactly
- Case sensitivity issues

### Command Rename

**Changes Required**:

1. Rename `_handle_mcp_command()` → `_handle_notes_command()`
2. Update `handle_command()`: `cmd == "mcp"` → `cmd == "notes"`
3. Update help text: `/mcp` → `/notes`
4. Update error messages: "MCP" → "notes" (user-facing only)
5. Keep internal MCP references (API, server, protocol)

**Testing**:

- Verify all subcommands work: `status`, `list`, `read`, `search`, `sync`, `save`
- Verify project filtering works: `list FF`, `list 700B`
- Verify error messages are clear
