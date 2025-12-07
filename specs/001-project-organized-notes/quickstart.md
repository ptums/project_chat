# Quickstart: Project-Organized Meditation Notes

## Overview

This feature enables project-scoped meditation note retrieval and conversation saving. Notes are organized by project directories in the Obsidian notebook (daas, thn, ff, general, 700b), and the system automatically filters notes based on the current project context.

## Prerequisites

1. MCP server integration working (from previous feature)
2. Obsidian notebook repository organized by project directories
3. GitLab repository accessible

## Project Directory Structure

Your Obsidian notebook should have this structure:

```
meditation-repo/
├── daas/
│   ├── morning-meditation-2024-12-01.md
│   └── evening-reflection.md
├── thn/
│   ├── learning-notes.md
│   └── project-ideas.md
├── ff/
│   └── ...
├── general/
│   └── ...
└── 700b/
    └── ...
```

## Usage

### Automatic Note Retrieval

When you're working in a project conversation, relevant notes from that project's directory are automatically included. The system will recall and reference information from these notes naturally throughout the conversation:

```
You (DAAS) 🟣: What did I write about morning routines?
```

The system will:

1. Detect you're in DAAS project
2. Filter notes from `daas/` directory
3. Search for "morning routines" in those notes
4. Include relevant notes in the AI's context

### Saving Conversations

Save the current conversation as a note:

```
You (DAAS) 🟣: /mcp save "Morning Planning Session"
✓ Conversation saved as note: daas/morning-planning-session.md
Note synced to repository.
```

Or without a title (system generates one):

```
You (THN) 🟣: /mcp save
✓ Conversation saved as note: thn/conversation-2025-12-07-103045.md
Note synced to repository.
```

## Project Mapping

The system maps project names to directory names:

- **DAAS** → `daas/`
- **THN** → `thn/`
- **FF** → `ff/`
- **General** → `general/`
- **700B** → `700b/`

## Saved Note Format

Saved conversations are formatted as Obsidian markdown:

```markdown
---
title: Morning Planning Session
project: DAAS
created: 2025-12-07T10:30:00Z
tags: [conversation, ai-chat]
---

# Morning Planning Session

## User Message (10:30 AM)

What should I focus on today?

## Assistant Response (10:30 AM)

Based on your notes, you should focus on...

## User Message (10:31 AM)

Thanks!
```

## Troubleshooting

### Notes not appearing in context

1. Check that notes exist in the project directory
2. Run `/mcp sync` to update the index
3. Verify project name matches directory name (case-insensitive)

### Save command fails

1. Check repository sync status: `/mcp status`
2. Ensure you have write permissions to the repository
3. Check if repository is out of sync (may need to pull first)

### Wrong project directory

Verify the project mapping is correct. The system uses lowercase directory names regardless of project name casing.
