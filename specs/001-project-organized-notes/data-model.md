# Data Model: Project-Organized Meditation Notes

## Overview

This feature extends the existing MCP server data model to support project-based organization and conversation saving. No new database tables are required - all data is managed in-memory and via the GitLab repository.

## Extended Entities

### Note Entity (Extended)

**Location**: `src/models/note.py`

**Existing Fields**:

- `slug`: String identifier for the note
- `title`: Note title
- `content`: Note content (markdown)
- `frontmatter`: Dict of YAML frontmatter metadata
- `file_path`: Relative path from repository root (e.g., `daas/morning-meditation.md`)
- `last_modified`: Optional datetime

**New Derived Property**:

- `project_directory`: String - extracted from file_path (e.g., `daas` from `daas/morning-meditation.md`)

**Example**:

```python
Note(
    slug="morning-meditation",
    title="Morning Meditation",
    content="# Morning Meditation\n\n...",
    frontmatter={"tags": ["meditation"]},
    file_path="daas/morning-meditation.md",
    last_modified=datetime(2025, 12, 7, 10, 0)
)
# project_directory = "daas" (derived)
```

### NoteIndex Entity (Extended)

**Location**: `src/models/index.py`

**Existing Methods**:

- `add(note)`: Add note to index
- `get_by_slug(slug)`: Get note by slug
- `get_by_uri(uri)`: Get note by URI
- `get_by_file_path(file_path)`: Get note by file path
- `all_notes()`: Get all notes
- `search(query, limit)`: Search notes by content

**New Methods**:

- `get_by_project(project: str) -> list[Note]`: Filter notes by project directory
- `search_by_project(project: str, query: str, limit: int) -> list[Note]`: Search notes within a project

**Implementation**: Filter `all_notes()` by checking if `file_path` starts with project directory name.

## New Entities

### ProjectDirectoryMapper

**Location**: `src/services/project_filter.py`

**Purpose**: Maps project names to directory names

**Fields**:

- `_mapping`: Dict[str, str] - project name to directory name mapping

**Methods**:

- `get_directory(project: str) -> str`: Get directory name for project
- `is_valid_project(project: str) -> bool`: Check if project has a mapping

**Mapping**:

```python
{
    "DAAS": "daas",
    "THN": "thn",
    "FF": "ff",
    "General": "general",
    "700B": "700b"
}
```

### ConversationNote

**Location**: `src/services/note_saver.py`

**Purpose**: Represents a conversation to be saved as a note

**Fields**:

- `title`: String - note title
- `project`: String - project name (DAAS, THN, etc.)
- `messages`: List[Dict] - conversation messages with role, content, timestamp
- `created_at`: Datetime - conversation creation time
- `metadata`: Dict - additional metadata (tags, etc.)

**Methods**:

- `to_markdown() -> str`: Convert conversation to Obsidian markdown format
- `generate_filename() -> str`: Generate filename from title or content

## Data Flow

### Note Retrieval Flow

1. User sends message in project context (e.g., "DAAS")
2. `build_project_context()` calls MCP API with project filter
3. MCP API uses `ProjectDirectoryMapper` to get directory name ("daas")
4. `NoteIndex.get_by_project("daas")` filters notes by file_path prefix
5. Relevant notes are included in conversation context

### Conversation Saving Flow

1. User runs `/mcp save "Title"` command
2. System collects current conversation messages
3. `ConversationNote` entity created with messages and metadata
4. `ConversationNote.to_markdown()` generates markdown content
5. File created in project directory (e.g., `daas/conversation-title.md`)
6. Git operations: add, commit, push to repository
7. Note added to index for future retrieval

## No Database Changes

- No new tables required
- All data managed in-memory (NoteIndex) or filesystem (repository)
- Conversation saving writes directly to Git repository
- No schema modifications needed
