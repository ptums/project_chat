# Data Model: Conversation Audit Tool

## 1. conversations (EXISTING - Read/Update/Delete Operations)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | Conversation identifier (used for lookups) |
| title | TEXT | NOT NULL | Conversation title (editable) |
| project | TEXT | NOT NULL, CHECK project IN ('THN','DAAS','FF','700B','general') | Project tag (editable) |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp (read-only) |

**Operations**:
- **Read**: Query by project, ID, or title
- **Update**: Edit `title` or `project` fields
- **Delete**: Remove conversation (CASCADE deletes messages and conversation_index entry)

## 2. messages (EXISTING - Read Operations Only)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | Message identifier |
| conversation_id | UUID | FK → conversations.id, ON DELETE CASCADE | Links message to conversation |
| role | TEXT | NOT NULL | 'user' or 'assistant' |
| content | TEXT | NOT NULL | Message content |
| created_at | TIMESTAMPTZ | NOT NULL | Message timestamp |

**Operations**:
- **Read**: Load messages for a conversation (ordered by created_at ASC)
- **Count**: Count messages per conversation for listing

## 3. conversation_index (EXISTING - Read/Update/Delete Operations)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| session_id | UUID | PK, FK → conversations.id, ON DELETE CASCADE | References conversation |
| project | TEXT | NOT NULL | Project tag (must stay in sync with conversations.project) |
| title | TEXT | NULL | Indexed title (may differ from conversations.title) |
| ... | ... | ... | Other indexed fields (read-only for audit tool) |

**Operations**:
- **Read**: Query by project or session_id
- **Update**: Update `project` field when conversation project is edited
- **Delete**: Handled by CASCADE when conversation is deleted

## State Transitions

### Conversation Listing Flow
```
User runs audit_conversations.py
  ↓
Main menu displayed
  ↓
User selects view mode (by project/id/title)
  ↓
Query database based on selection
  ↓
Display conversation list/details
  ↓
User can type /messages <id> to review
```

### Message Review Flow
```
User types /messages <conversation_id>
  ↓
Query messages from database
  ↓
Display messages in chronological order
  ↓
User can type commands:
  - /edit-title → prompt for new title → update conversations.title
  - /edit-project → prompt for new project → update conversations.project AND conversation_index.project
  - /delete → confirm → delete from conversations (CASCADE handles rest)
```

### Project Edit Flow
```
User types /edit-project
  ↓
Prompt for new project name
  ↓
Validate project name (THN, DAAS, FF, 700B, general)
  ↓
BEGIN TRANSACTION
  ↓
UPDATE conversations SET project = new_project WHERE id = conv_id
  ↓
UPDATE conversation_index SET project = new_project WHERE session_id = conv_id (if exists)
  ↓
COMMIT TRANSACTION
  ↓
Display success message
```

## Validation Rules

### Project Validation
- **Rule**: Project must be one of: 'THN', 'DAAS', 'FF', '700B', 'general'
- **Enforcement**: Application-level validation before database update
- **Error Message**: "Invalid project. Must be one of: THN, DAAS, FF, 700B, general"

### Title Validation
- **Rule**: Title must be non-empty string (after `.strip()`)
- **Enforcement**: Application-level validation before database update
- **Error Message**: "Title cannot be empty"

### UUID Validation
- **Rule**: Conversation ID must be valid UUID format
- **Enforcement**: Try `uuid.UUID(input)` and catch `ValueError`
- **Error Message**: "Invalid conversation ID format"

## Relationships

- `messages.conversation_id` → `conversations.id` (1:many, ON DELETE CASCADE)
- `conversation_index.session_id` → `conversations.id` (1:1, ON DELETE CASCADE)
- When editing project: Both `conversations.project` and `conversation_index.project` must be updated
- When deleting conversation: CASCADE automatically deletes messages and conversation_index entry

## Data Consistency Requirements

1. **Project Sync**: `conversations.project` and `conversation_index.project` must match (when conversation_index entry exists)
2. **Transaction Safety**: Project edits must use transactions to ensure both tables update atomically
3. **Referential Integrity**: Deletions rely on CASCADE constraints to maintain integrity

