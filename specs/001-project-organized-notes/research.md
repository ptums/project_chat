# Research: Project-Organized Meditation Notes Integration

## Project Directory Mapping

### Decision: Lowercase mapping with explicit configuration

**Rationale**: Project names in the system (DAAS, THN, FF, General, 700B) need to map to directory names in the Obsidian repository (daas, thn, ff, general, 700b). The mapping should be explicit and configurable to handle edge cases.

**Implementation approach**:

- Create a mapping dictionary: `{"DAAS": "daas", "THN": "thn", "FF": "ff", "General": "general", "700B": "700b"}`
- Default to lowercase conversion if no explicit mapping exists
- Handle case-insensitive matching for robustness

**Alternatives considered**:

- Automatic lowercase conversion: Rejected - "700B" → "700b" works, but explicit mapping is clearer
- Case-sensitive matching: Rejected - too fragile if directory names change slightly

## Note Filtering by Project Directory

### Decision: Filter by file path prefix

**Rationale**: Notes are organized in project directories (e.g., `daas/note1.md`, `thn/note2.md`). The Note entity already has a `file_path` field that includes the relative path from repository root. We can filter notes by checking if the file_path starts with the project directory name.

**Implementation approach**:

- Add project directory path to Note model (or derive from file_path)
- Filter NoteIndex results by checking file_path prefix
- Support notes in subdirectories (e.g., `daas/subfolder/note.md`)

**Alternatives considered**:

- Separate indexes per project: Rejected - adds complexity, current single index is sufficient
- Database storage: Rejected - notes are already in-memory for performance, no need for DB

## Conversation Saving Format

### Decision: Obsidian markdown with YAML frontmatter

**Rationale**: Saved conversations should be readable in Obsidian and follow the same format as existing notes. Obsidian uses YAML frontmatter for metadata and standard markdown for content.

**Format structure**:

```markdown
---
title: Conversation Title
project: DAAS
created: 2025-12-07T10:30:00Z
tags: [conversation, ai-chat]
---

# Conversation Title

## User Message (10:30 AM)

User's message content here...

## Assistant Response (10:31 AM)

Assistant's response here...

## User Message (10:32 AM)

...
```

**Alternatives considered**:

- Plain markdown without frontmatter: Rejected - loses metadata that could be useful
- JSON format: Rejected - not readable in Obsidian, defeats purpose of integration

## Git Operations for Saving Notes

### Decision: Commit and push via GitPython

**Rationale**: Notes must be saved to the GitLab repository. GitPython is already a dependency and provides programmatic Git operations. We need to:

1. Create/update the markdown file
2. Stage the file (`git add`)
3. Commit with a descriptive message
4. Push to remote repository

**Implementation approach**:

- Use GitPython's Repo class to get repository handle
- Create file in appropriate project directory
- Use `repo.index.add()` and `repo.index.commit()`
- Use `repo.remotes.origin.push()` to push changes

**Error handling**:

- Handle case where repository is out of sync (pull first, then push)
- Handle merge conflicts (abort and report error)
- Handle permission issues (report clearly)

**Alternatives considered**:

- Shell out to git command: Rejected - less reliable, harder error handling
- Only commit locally: Rejected - user requirement is to save to repository (implies push)

## Filename Generation

### Decision: Slug from title with timestamp fallback

**Rationale**: Filenames should be readable and unique. Use the conversation title to generate a slug, with timestamp as fallback if no title provided.

**Implementation approach**:

- If title provided: convert to slug (lowercase, hyphens, alphanumeric)
- If no title: generate from first user message or use timestamp
- Format: `{slug}.md` or `conversation-{timestamp}.md`
- Handle duplicate filenames by appending number: `{slug}-2.md`

**Alternatives considered**:

- UUID-based filenames: Rejected - not human-readable in Obsidian
- Always use timestamp: Rejected - less meaningful than title-based names

## Integration with Context Builder

### Decision: Extend MCP API with project filtering, integrate into context_builder

**Rationale**: The existing `context_builder.py` builds project-aware context. We need to add MCP note retrieval that's filtered by project. The MCP API should support project filtering, and context_builder should call it with the current project.

**Implementation approach**:

- Add `list_resources_by_project(project: str)` method to MCPApi
- Add `get_project_notes(project: str, user_message: str)` method that filters and searches
- Integrate into `build_project_context()` to include relevant notes
- Maintain existing behavior if MCP notes unavailable

**Alternatives considered**:

- Separate context builder for notes: Rejected - adds complexity, better to extend existing
- Always include all notes: Rejected - defeats purpose of project organization
