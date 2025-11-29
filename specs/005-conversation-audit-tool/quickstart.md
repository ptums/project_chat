# Quickstart: Conversation Audit Tool

## Overview

The conversation audit tool (`audit_conversations.py`) allows you to manage and clean up your conversation history. You can list conversations, review message history, edit titles and projects, and delete conversations.

## Running the Tool

```bash
python3 audit_conversations.py
```

## Usage Examples

### Example 1: List Conversations by Project

```bash
$ python3 audit_conversations.py

Conversation Audit Tool
======================
1. List conversations by project
2. View conversation by ID
3. Search conversation by title
4. Exit

Select an option (1-4): 1

Enter project name (THN/DAAS/FF/700B/general): THN

Conversations for project: THN
================================
ID: abc-123-def-456
Title: Bitcoin Project Ideas
Project: THN
Messages: 15

ID: xyz-789-ghi-012
Title: Future blockchain/bitcoin projects
Project: THN
Messages: 8

Enter /messages <id> to review, or press Enter to return to main menu:
```

### Example 2: Review Message History

```bash
Enter /messages <id> to review, or press Enter to return to main menu: /messages abc-123-def-456

Message History for: Bitcoin Project Ideas (THN)
================================================

[1] [USER] How do I generate passive income with Bitcoin?
[2] [ASSISTANT] There are several ways to generate passive income...
[3] [USER] What about blockchain projects?
[4] [ASSISTANT] Blockchain projects can include...

Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

### Example 3: Edit Conversation Title

```bash
Enter command: /edit-title
Enter new title: Updated Bitcoin Project Ideas
Title updated successfully.

Conversation: Updated Bitcoin Project Ideas (THN)
Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

### Example 4: Edit Conversation Project

```bash
Enter command: /edit-project
Enter new project (THN/DAAS/FF/700B/general): DAAS
Project updated successfully.

Conversation: Updated Bitcoin Project Ideas (DAAS)
Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

### Example 5: Delete Conversation

```bash
Enter command: /delete
Are you sure you want to delete this conversation? (yes/no): yes
Conversation deleted successfully.

Returning to main menu...
```

### Example 6: Search by Title

```bash
Select an option (1-4): 3

Enter title (or partial title): bitcoin

Search Results for: "bitcoin"
=============================
ID: abc-123-def-456
Title: Bitcoin Project Ideas
Project: THN
Messages: 15

ID: xyz-789-ghi-012
Title: Future blockchain/bitcoin projects
Project: THN
Messages: 8

Enter /messages <id> to review, or press Enter to return to main menu:
```

### Example 7: View by ID

```bash
Select an option (1-4): 2

Enter conversation ID: abc-123-def-456

Conversation Details
====================
ID: abc-123-def-456
Title: Bitcoin Project Ideas
Project: THN
Messages: 15
Created: 2025-01-27 10:30:00

Enter /messages <id> to review, or press Enter to return to main menu:
```

## Common Workflows

### Workflow 1: Clean Up Misclassified Conversations

1. Run `python3 audit_conversations.py`
2. Select option 1 (List conversations by project)
3. Enter project name (e.g., "THN")
4. Review the list - identify conversations with titles that don't match the project
5. Type `/messages <id>` for suspicious conversations
6. Review message history to confirm misclassification
7. Type `/edit-project` to change project tag
8. Enter correct project name
9. Repeat for other misclassified conversations

### Workflow 2: Delete Jumbled Conversations

1. Run `python3 audit_conversations.py`
2. Select option 1 (List conversations by project)
3. Enter project name
4. Review list for conversations that seem mixed/jumbled
5. Type `/messages <id>` to review
6. Confirm the conversation contains multiple unrelated topics
7. Type `/delete`
8. Confirm with "yes"
9. Conversation and all messages are deleted

### Workflow 3: Fix Conversation Titles

1. Run `python3 audit_conversations.py`
2. Select option 3 (Search conversation by title)
3. Enter partial title to find conversations
4. Type `/messages <id>` to review
5. Type `/edit-title` to update title
6. Enter new, more descriptive title
7. Title is updated

## Implementation Checklist

- [ ] Create `audit_conversations.py` script with main menu
- [ ] Implement `list_conversations_by_project(project: str)` function
- [ ] Implement `get_conversation_by_id(conv_id: UUID)` function
- [ ] Implement `search_conversations_by_title(title: str)` function
- [ ] Implement `view_messages(conv_id: UUID)` function
- [ ] Implement `edit_conversation_title(conv_id: UUID, new_title: str)` function
- [ ] Implement `edit_conversation_project(conv_id: UUID, new_project: str)` function with transaction
- [ ] Implement `delete_conversation(conv_id: UUID)` function with confirmation
- [ ] Add input validation (UUID, project names, non-empty titles)
- [ ] Add error handling for database operations
- [ ] Test all workflows above

## Key Functions to Implement

### `audit_conversations.py`

1. **`main()`** - Entry point, displays main menu, handles routing
2. **`list_by_project(project: str)`** - Query and display conversations for a project
3. **`get_by_id(conv_id: str)`** - Query and display single conversation by ID
4. **`search_by_title(title: str)`** - Search conversations by title pattern
5. **`view_messages(conv_id: UUID)`** - Display message history for a conversation
6. **`edit_title(conv_id: UUID, new_title: str)`** - Update conversation title
7. **`edit_project(conv_id: UUID, new_project: str)`** - Update conversation project (both tables)
8. **`delete_conversation(conv_id: UUID)`** - Delete conversation with confirmation
9. **`validate_uuid(uuid_str: str) -> UUID`** - Validate and parse UUID
10. **`validate_project(project: str) -> bool`** - Validate project name

## Database Verification

After editing, verify changes in database:

```sql
-- Check conversation was updated
SELECT id, title, project FROM conversations WHERE id = 'abc-123-def-456';

-- Check conversation_index was updated (if exists)
SELECT session_id, project FROM conversation_index WHERE session_id = 'abc-123-def-456';

-- Verify message count
SELECT COUNT(*) FROM messages WHERE conversation_id = 'abc-123-def-456';
```

Expected: Both `conversations` and `conversation_index` tables should reflect the updated project.

