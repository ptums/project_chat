# Quickstart: RAG and Notes Improvements

## Overview

Three improvements to the project chat system:

1. Remove automatic RAG inclusion - make RAG manual-only via `/rag`
2. Fix notes sync to include all project directories
3. Rename `/mcp` command to `/notes`

## Implementation Steps

### 1. Remove Automatic RAG Inclusion

**File**: `brain_core/context_builder.py`

**Step 1.1**: Remove THN RAG inclusion from `build_project_system_prompt()`

```python
# REMOVE this block (lines ~137-152):
if project.upper() == "THN" and user_message:
    try:
        rag_result = build_thn_rag_context(user_message)
        # ... RAG inclusion code ...
```

**Step 1.2**: Remove DAAS RAG inclusion from `build_project_system_prompt()`

```python
# REMOVE this block (lines ~154-172):
if project.upper() == "DAAS" and user_message:
    if should_include_daas_rag(user_message):
        try:
            rag_result = build_daas_rag_context(user_message, top_k=3)
            # ... RAG inclusion code ...
```

**Step 1.3**: Remove `should_include_daas_rag()` function

```python
# DELETE entire function (lines ~692-750):
def should_include_daas_rag(user_message: str) -> bool:
    # ... entire function ...
```

**Step 1.4**: Update docstring for `build_project_system_prompt()`

```python
def build_project_system_prompt(project: str, user_message: str = "") -> str:
    """
    Build the complete system prompt for a given project.

    Loads the base system prompt and appends project-specific extension.
    Does NOT include RAG context automatically - use /rag command for RAG.

    Args:
        project: Project tag (THN, DAAS, FF, 700B, or "general")
        user_message: Ignored (kept for backward compatibility)

    Returns:
        Composed system prompt string (base + project extension, NO RAG)
    """
```

**File**: `brain_core/chat.py`

**Step 1.5**: Remove RAG inclusion logic from `chat_turn()`

```python
# REMOVE these lines (~73-79):
include_thn_rag = project.upper() == "THN" and is_first_message
include_daas_rag = project.upper() == "DAAS" and should_include_daas_rag(user_text)

user_message_for_rag = ""
if include_thn_rag or include_daas_rag:
    user_message_for_rag = user_text

system_prompt = build_project_system_prompt(project, user_message_for_rag)
```

**Step 1.6**: Replace with simple call

```python
# REPLACE with:
system_prompt = build_project_system_prompt(project, "")
```

**Step 1.7**: Remove RAG-related logging

```python
# REMOVE RAG inclusion status logging (~84-95)
# Keep only:
logger.debug(f"System prompt for project {project} (length: {len(system_prompt)} chars)")
```

**Step 1.8**: Remove import

```python
# REMOVE from imports:
from .context_builder import should_include_daas_rag
```

**Step 1.9**: Update skip RAG logic

```python
# SIMPLIFY this block (~45-60):
# Remove THN/DAAS skip logic since RAG is never auto-included
indexed_context = {}
try:
    indexed_context = build_project_context(project, user_text)
except Exception as e:
    logger.warning(f"Failed to build indexed context for project {project}: {e}")
```

### 2. Fix Notes Sync (Verification)

**File**: `src/services/note_parser.py`

**Step 2.1**: Verify `find_notes()` uses `rglob()`

- Already uses `rglob("*.md")` which recursively scans all subdirectories
- No changes needed if this is working correctly

**File**: `src/services/project_filter.py`

**Step 2.2**: Verify project mapping

- Check that all projects are mapped: DAAS, THN, FF, General, 700B
- Mapping already exists, verify it's correct

**Testing**:

```bash
# Test sync indexes all directories
python -c "from src.mcp.api import get_mcp_api; api = get_mcp_api(); api.sync_repository()"

# Test project filtering
python -c "from src.mcp.api import get_mcp_api; api = get_mcp_api(); notes = api.list_resources_by_project('FF'); print(f'FF notes: {len(notes)}')"
python -c "from src.mcp.api import get_mcp_api; api = get_mcp_api(); notes = api.list_resources_by_project('700B'); print(f'700B notes: {len(notes)}')"
```

### 3. Rename /mcp to /notes

**File**: `chat_cli.py`

**Step 3.1**: Rename handler function

```python
# RENAME:
def _handle_mcp_command(...) → def _handle_notes_command(...)
```

**Step 3.2**: Update command parsing

```python
# CHANGE:
if cmd == "mcp":
    return current_project, True, arg, "mcp"

# TO:
if cmd == "notes":
    return current_project, True, arg, "notes"
```

**Step 3.3**: Update handler call

```python
# CHANGE:
elif special == "mcp":
    _handle_mcp_command(msg, current_project, conv_id)

# TO:
elif special == "notes":
    _handle_notes_command(msg, current_project, conv_id)
```

**Step 3.4**: Update help text

```python
# CHANGE all occurrences:
"/mcp [status|list [server]|read <uri>|search <server> <query>|sync [server]]"

# TO:
"/notes [status|list [project]|read <uri|title|slug> [project]|search <query> [limit]|sync|save [title]]"
```

**Step 3.5**: Update function docstring

```python
def _handle_notes_command(args: str, current_project: str, conversation_id: uuid.UUID = None):
    """
    Handle /notes command with subcommands.

    Commands:
    - /notes status - Show status of notes server
    - /notes list [project] - List all notes (optionally filtered by project)
    - /notes read <uri|title|slug> [project] - Read a specific note
    - /notes search <query> [limit] - Search notes
    - /notes sync - Sync repository from GitLab
    - /notes save [title] - Save current conversation as a note
    """
```

**Step 3.6**: Update error messages (user-facing only)

```python
# CHANGE user-facing messages:
"MCP Server Status:" → "Notes Server Status:"
"MCP Resources" → "Notes"
"MCP integration not available" → "Notes integration not available"
"MCP command error" → "Notes command error"

# KEEP internal references:
# MCP API, MCP server, MCP protocol (these are internal)
```

## Testing

### Test 1: RAG Not Auto-Included

1. Start a new THN conversation
2. Send first message
3. Check logs - should NOT see "THN RAG included in system prompt"
4. Check system prompt - should NOT contain RAG context

### Test 2: Manual RAG Works

1. In THN conversation, type: `/rag`
2. Should see RAG context displayed
3. In DAAS conversation, type: `/rag analyze this dream`
4. Should see DAAS RAG context displayed

### Test 3: Notes Sync

1. Type: `/notes sync`
2. Should sync repository and index all notes
3. Check logs for note count from all directories

### Test 4: Project Filtering

1. Type: `/notes list FF`
2. Should show only notes from `ff/` directory
3. Type: `/notes list 700B`
4. Should show only notes from `700b/` directory

### Test 5: Command Rename

1. Type: `/notes status`
2. Should work (replaces `/mcp status`)
3. Type: `/mcp status`
4. Should show error or "unknown command"

## Validation Checklist

- [ ] RAG never automatically included in system prompts
- [ ] `/rag` command works for THN
- [ ] `/rag` command works for DAAS
- [ ] `/notes sync` indexes all project directories
- [ ] `/notes list FF` shows FF directory notes
- [ ] `/notes list 700B` shows 700B directory notes
- [ ] `/notes` command works identically to previous `/mcp` command
- [ ] All subcommands work: `status`, `list`, `read`, `search`, `sync`, `save`
- [ ] Help text updated
- [ ] Error messages updated (user-facing only)
- [ ] No references to `/mcp` in user-facing text
