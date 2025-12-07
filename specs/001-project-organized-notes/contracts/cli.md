# CLI Contracts: Project-Organized Notes

## `/mcp save` Command

### Command Format

```
/mcp save [title]
```

### Description

Saves the current conversation as a markdown note in the appropriate project directory of the Obsidian notebook repository.

### Parameters

- `title` (optional): Title for the saved note. If not provided, system generates a title from conversation content.

### Behavior

1. Collects all messages from the current conversation
2. Determines project directory based on current project context
3. Generates markdown content with YAML frontmatter
4. Creates file in project directory (e.g., `daas/conversation-title.md`)
5. Commits and pushes to GitLab repository
6. Updates note index

### Success Response

```
✓ Conversation saved as note: daas/my-conversation-title.md
Note synced to repository.
```

### Error Responses

```
Error: No active conversation to save.
```

```
Error: Failed to save note: [error message]
```

### Examples

```
You (DAAS) 🟣: /mcp save "Morning Planning Session"
✓ Conversation saved as note: daas/morning-planning-session.md
Note synced to repository.
```

```
You (THN) 🟣: /mcp save
✓ Conversation saved as note: thn/conversation-2025-12-07-103045.md
Note synced to repository.
```

## Project-Scoped Note Retrieval

### Automatic Behavior

When building conversation context, the system automatically filters meditation notes by project directory:

- **DAAS project**: Only notes from `daas/` directory
- **THN project**: Only notes from `thn/` directory
- **FF project**: Only notes from `ff/` directory
- **General project**: Only notes from `general/` directory
- **700B project**: Only notes from `700b/` directory

### Integration

This happens automatically in `build_project_context()` - no user command needed. Notes are included in the context when relevant to the user's message.
