# API Contracts: RAG and Notes Improvements

## Modified Functions

### `build_project_system_prompt(project: str, user_message: str = "") -> str`

**Location**: `brain_core/context_builder.py`

**Changes**: Remove automatic RAG inclusion

**Before**:

- Included THN RAG when `user_message` provided (first message)
- Included DAAS RAG when analysis intent detected
- RAG context appended to system prompt

**After**:

- Does NOT include RAG automatically
- `user_message` parameter ignored for RAG purposes (kept for backward compatibility)
- System prompt contains only: base prompt + project overview + project rules

**Signature**: Unchanged

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

**Behavior**:

- Load base system prompt
- Add project overview from `project_knowledge` table
- Add project rules from `project_knowledge` table
- Return combined prompt (NO RAG)

### `chat_turn(conversation_id, user_text: str, project: str, stream: bool = False)`

**Location**: `brain_core/chat.py`

**Changes**: Remove automatic RAG inclusion logic

**Before**:

- Checked if first message for THN RAG
- Checked analysis intent for DAAS RAG
- Passed `user_text` to `build_project_system_prompt()` conditionally

**After**:

- Always calls `build_project_system_prompt(project, "")` (empty user_message)
- No RAG inclusion checks
- RAG only available via `/rag` command

**Signature**: Unchanged

```python
def chat_turn(conversation_id, user_text: str, project: str, stream: bool = False):
    """
    Handle a chat turn.

    System prompt does NOT include RAG automatically.
    Use /rag command to manually include RAG context.

    Args:
        conversation_id: Conversation UUID
        user_text: User message text
        project: Project tag
        stream: Whether to stream response

    Returns:
        Chat response
    """
```

**Behavior**:

- Build system prompt WITHOUT RAG
- Process user message
- Return response

### Removed Function: `should_include_daas_rag(user_message: str) -> bool`

**Location**: `brain_core/context_builder.py`

**Status**: DELETE

**Reason**: No longer needed - RAG is manual-only

## Command API

### `/notes [subcommand]`

**Location**: `chat_cli.py`

**Changes**: Renamed from `/mcp`

**Before**: `/mcp [subcommand]`  
**After**: `/notes [subcommand]`

**Subcommands** (unchanged):

- `status` - Show server status
- `list [project]` - List notes (optionally filtered by project)
- `read <uri|title|slug> [project]` - Read specific note
- `search <query> [limit]` - Search notes
- `sync` - Sync repository and rebuild index
- `save [title]` - Save conversation as note

**Handler Function**:

```python
def _handle_notes_command(args: str, current_project: str, conversation_id: uuid.UUID = None):
    """
    Handle /notes command with subcommands.

    Renamed from _handle_mcp_command().
    Functionality unchanged.
    """
```

## Unchanged Functions (Available for Manual Use)

### `build_thn_rag_context(user_message: str) -> Dict[str, Any]`

**Location**: `brain_core/context_builder.py`

**Status**: UNCHANGED

**Usage**: Called by `/rag` command for THN project

### `build_daas_rag_context(user_message: str, top_k: int = 3) -> Dict[str, Any]`

**Location**: `brain_core/context_builder.py`

**Status**: UNCHANGED

**Usage**: Called by `/rag` command for DAAS project

### `/rag` Command

**Location**: `chat_cli.py`

**Status**: UNCHANGED

**Usage**: Manually generate and display RAG context for THN or DAAS project

## MCP API (Internal - Unchanged)

All MCP API functions remain unchanged:

- `MCPApi.list_resources()`
- `MCPApi.list_resources_by_project(project: str)`
- `MCPApi.read_resource(identifier: str, project: Optional[str] = None)`
- `MCPApi.search_notes(query: str, limit: int = 10)`
- `MCPApi.sync_repository()`
- `MCPApi.save_conversation(...)`

These are internal implementation details and not affected by command rename.
