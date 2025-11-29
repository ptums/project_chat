# CLI Contracts: Conversation Audit Tool

## Main Menu

### Startup

**Purpose**: Display main menu and handle user selection.

**Request Flow**:
1. Script starts: `python audit_conversations.py`
2. System displays main menu:
   ```
   Conversation Audit Tool
   =======================
   1. List conversations by project
   2. View conversation by ID
   3. Search conversation by title
   4. Exit
   
   Select an option (1-4):
   ```
3. User enters option number
4. System routes to appropriate handler

**Success Output**: Menu displayed, user selection processed

**Error Handling**:
- Invalid option: Display "Invalid option. Please enter 1-4." and show menu again
- Ctrl+C: Exit gracefully with "Exiting."

---

## Option 1: List Conversations by Project

**Purpose**: Display all conversations for a specific project.

**Request Flow**:
1. User selects option 1
2. System prompts: "Enter project name (THN/DAAS/FF/700B/general): "
3. User enters project name
4. System queries database for conversations with that project
5. System displays list with columns: ID, Title, Project, Message Count
6. System prompts: "Enter /messages <id> to review, or press Enter to return to main menu"

**Success Output** (stdout):
```
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

**Error Handling**:
- Invalid project name: Display "Invalid project. Must be one of: THN, DAAS, FF, 700B, general" and prompt again
- No conversations found: Display "No conversations found for project [PROJECT]"
- Database error: Display "Database error: [error message]" and return to main menu

---

## Option 2: View Conversation by ID

**Purpose**: Display details for a specific conversation.

**Request Flow**:
1. User selects option 2
2. System prompts: "Enter conversation ID: "
3. User enters UUID
4. System queries database for conversation
5. System displays conversation details
6. System prompts: "Enter /messages <id> to review, or press Enter to return to main menu"

**Success Output** (stdout):
```
Conversation Details
====================
ID: abc-123-def-456
Title: Bitcoin Project Ideas
Project: THN
Messages: 15
Created: 2025-01-27 10:30:00

Enter /messages <id> to review, or press Enter to return to main menu:
```

**Error Handling**:
- Invalid UUID format: Display "Invalid conversation ID format" and prompt again
- Conversation not found: Display "Conversation not found: [ID]"
- Database error: Display "Database error: [error message]" and return to main menu

---

## Option 3: Search Conversation by Title

**Purpose**: Find conversations by title (exact or partial match).

**Request Flow**:
1. User selects option 3
2. System prompts: "Enter title (or partial title): "
3. User enters search term
4. System queries database with ILIKE pattern matching
5. System displays matching conversations
6. System prompts: "Enter /messages <id> to review, or press Enter to return to main menu"

**Success Output** (stdout):
```
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

**Error Handling**:
- No matches: Display "No conversations found matching '[search term]'"
- Database error: Display "Database error: [error message]" and return to main menu

---

## Message Review Mode

### `/messages <conversation_id>`

**Purpose**: Display message history for a conversation.

**Request Flow**:
1. User types `/messages <conversation_id>`
2. System validates UUID format
3. System queries messages from database
4. System displays messages in chronological order
5. System displays command prompt

**Success Output** (stdout):
```
Message History for: Bitcoin Project Ideas (THN)
================================================

[1] [USER] How do I generate passive income with Bitcoin?
[2] [ASSISTANT] There are several ways to generate passive income...
[3] [USER] What about blockchain projects?
[4] [ASSISTANT] Blockchain projects can include...

Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

**Error Handling**:
- Invalid UUID: Display "Invalid conversation ID format"
- Conversation not found: Display "Conversation not found: [ID]"
- No messages: Display "No messages found for this conversation"
- Database error: Display "Database error: [error message]"

---

### `/edit-title`

**Purpose**: Update conversation title.

**Request Flow**:
1. User types `/edit-title` while viewing messages
2. System prompts: "Enter new title: "
3. User enters new title
4. System validates title is non-empty
5. System updates `conversations.title` in database
6. System displays success message and updated conversation info

**Success Output** (stdout):
```
Enter new title: Updated Bitcoin Project Ideas
Title updated successfully.

Conversation: Updated Bitcoin Project Ideas (THN)
Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

**Error Handling**:
- Empty title: Display "Title cannot be empty" and prompt again
- Database error: Display "Error updating title: [error message]"

---

### `/edit-project`

**Purpose**: Update conversation project tag.

**Request Flow**:
1. User types `/edit-project` while viewing messages
2. System prompts: "Enter new project (THN/DAAS/FF/700B/general): "
3. User enters project name
4. System validates project name
5. System begins transaction
6. System updates `conversations.project`
7. System updates `conversation_index.project` (if entry exists)
8. System commits transaction
9. System displays success message

**Success Output** (stdout):
```
Enter new project (THN/DAAS/FF/700B/general): DAAS
Project updated successfully.

Conversation: Bitcoin Project Ideas (DAAS)
Commands: /edit-title, /edit-project, /delete, /back
Enter command:
```

**Error Handling**:
- Invalid project: Display "Invalid project. Must be one of: THN, DAAS, FF, 700B, general" and prompt again
- Database error: Display "Error updating project: [error message]", rollback transaction

---

### `/delete`

**Purpose**: Delete conversation and all related data.

**Request Flow**:
1. User types `/delete` while viewing messages
2. System prompts: "Are you sure you want to delete this conversation? (yes/no): "
3. User enters response
4. If "yes": System deletes from `conversations` table (CASCADE handles messages and conversation_index)
5. System displays success message and returns to main menu
6. If "no" or other: System cancels deletion and returns to message view

**Success Output** (stdout):
```
Are you sure you want to delete this conversation? (yes/no): yes
Conversation deleted successfully.

Returning to main menu...
```

**Error Handling**:
- Database error: Display "Error deleting conversation: [error message]"
- User cancels: Display "Deletion cancelled." and return to message view

---

### `/back`

**Purpose**: Return to previous view (main menu or conversation list).

**Request Flow**:
1. User types `/back` while viewing messages
2. System returns to previous context (main menu or conversation list)

**Success Output**: Returns to previous menu/view

---

## Database Operations

### Query Conversations by Project

```sql
SELECT 
    c.id,
    c.title,
    c.project,
    COUNT(m.id) as message_count,
    c.created_at
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.project = %s
GROUP BY c.id, c.title, c.project, c.created_at
ORDER BY c.created_at DESC;
```

### Query Conversation by ID

```sql
SELECT 
    c.id,
    c.title,
    c.project,
    COUNT(m.id) as message_count,
    c.created_at
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.id = %s
GROUP BY c.id, c.title, c.project, c.created_at;
```

### Search Conversations by Title

```sql
SELECT 
    c.id,
    c.title,
    c.project,
    COUNT(m.id) as message_count,
    c.created_at
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.title ILIKE %s
GROUP BY c.id, c.title, c.project, c.created_at
ORDER BY c.created_at DESC;
```

### Load Messages for Conversation

```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = %s
ORDER BY created_at ASC
LIMIT 50;
```

### Update Conversation Title

```sql
UPDATE conversations
SET title = %s
WHERE id = %s;
```

### Update Conversation Project (Transaction)

```sql
BEGIN;
UPDATE conversations SET project = %s WHERE id = %s;
UPDATE conversation_index SET project = %s WHERE session_id = %s;
COMMIT;
```

### Delete Conversation

```sql
DELETE FROM conversations WHERE id = %s;
-- CASCADE automatically deletes:
-- - All messages in messages table
-- - Entry in conversation_index table
```

