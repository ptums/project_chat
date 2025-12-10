# Data Model: RAG and Notes Improvements

## Overview

No new data models required. This feature modifies behavior of existing systems without changing data structures.

## Existing Entities (Unchanged)

### System Prompt Building

**Location**: `brain_core/context_builder.py`

**Current Behavior**:

- `build_project_system_prompt()` includes RAG automatically for THN/DAAS
- RAG context appended to system prompt string

**New Behavior**:

- `build_project_system_prompt()` does NOT include RAG automatically
- System prompt contains only: base prompt + project overview + project rules
- RAG only available via manual `/rag` command

**Data Flow**:

```
User Message → chat_turn() → build_project_system_prompt() → System Prompt (NO RAG)
User Command → /rag → build_thn_rag_context() / build_daas_rag_context() → RAG Context
```

### Note Index

**Location**: `src/models/index.py`

**Current Behavior**:

- `NoteIndex` stores all notes from repository
- `get_by_project()` filters notes by project directory
- Notes indexed from all subdirectories via `rglob()`

**New Behavior**:

- No changes to data model
- Verification that sync indexes all project directories
- Verification that `get_by_project()` works for all projects

**Data Flow**:

```
Repository → IndexBuilder.sync_and_rebuild() → NoteParser.find_notes() → NoteIndex
NoteIndex.get_by_project("FF") → Notes from ff/ directory
NoteIndex.get_by_project("700B") → Notes from 700b/ directory
```

### Project Directory Mapper

**Location**: `src/services/project_filter.py`

**Current Behavior**:

- Maps project names to directory names
- Supports: DAAS → daas, THN → thn, FF → ff, General → general, 700B → 700b

**New Behavior**:

- No changes to data model
- Verification that all projects are mapped correctly

**Mapping Table**:
| Project Name | Directory Name |
|-------------|----------------|
| DAAS | daas |
| THN | thn |
| FF | ff |
| General | general |
| 700B | 700b |

## Command Handler

**Location**: `chat_cli.py`

**Current Behavior**:

- Command: `/mcp [subcommand]`
- Handler: `_handle_mcp_command()`

**New Behavior**:

- Command: `/notes [subcommand]`
- Handler: `_handle_notes_command()`
- Functionality unchanged

**Command Structure**:

```
/notes status          → Show server status
/notes list [project]  → List notes (optionally filtered by project)
/notes read <uri>      → Read specific note
/notes search <query>  → Search notes
/notes sync            → Sync repository and rebuild index
/notes save [title]    → Save conversation as note
```

## No Schema Changes

- No database migrations required
- No new tables or columns
- No changes to existing data structures
- All changes are behavioral/functional only
