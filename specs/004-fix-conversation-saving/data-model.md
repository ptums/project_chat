# Data Model: Fix Conversation Saving and Project Switching

## 1. conversations (EXISTING - No Schema Changes)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | Conversation identifier |
| title | TEXT | NOT NULL | Conversation title (now always required) |
| project | TEXT | NOT NULL, CHECK project IN ('THN','DAAS','FF','700B','general') | Project tag |

**Changes**: No schema changes. Title is already NOT NULL in database. Validation is enforced at application level.

## 2. messages (EXISTING - No Schema Changes)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | Message identifier |
| conversation_id | UUID | FK → conversations.id | Links message to conversation |
| role | TEXT | NOT NULL | 'user' or 'assistant' |
| content | TEXT | NOT NULL | Message content |
| meta_json | JSONB | NULL | Optional metadata |

**Changes**: No schema changes. Messages remain linked to their original conversation.

## 3. conversation_index (EXISTING - No Schema Changes)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| session_id | UUID | PK, FK → conversations.id | References conversation |
| project | TEXT | NOT NULL | Project tag (may differ from conversation.project if overridden) |
| title | TEXT | NULL | Indexed title from Ollama |
| ... | ... | ... | Other indexed fields |

**Changes**: No schema changes. Indexing behavior remains the same.

## State Transitions

### Conversation Lifecycle

1. **New Conversation Created**
   - User starts program → provides title (required) → selects project → `create_conversation(title, project)` called
   - New conversation record created with UUID, title, project

2. **Project Switch (Mid-Conversation)**
   - User types `/thn` (or other project command)
   - System calls `save_current_conversation(conv_id, current_project)` → `index_session(conv_id)`
   - System prompts for new title (required)
   - User provides title → `create_conversation(new_title, new_project)` called
   - New conversation record created, `conv_id` updated to new UUID
   - Messages continue under new conversation_id

3. **Exit**
   - User types `/exit` or Ctrl+C
   - System calls `save_current_conversation(conv_id, current_project)` → `index_session(conv_id)`
   - System displays usage summary and exits

## Validation Rules

### Title Validation
- **Rule**: Title must be non-empty string (after `.strip()`)
- **Enforcement**: Application-level validation in `chat_cli.py`
- **Error Message**: "A title is required"
- **Location**: 
  - Initial conversation creation (startup)
  - After project switch (before creating new conversation)

### Project Validation
- **Rule**: Project must be one of: 'THN', 'DAAS', 'FF', '700B', 'general'
- **Enforcement**: `normalize_project_tag()` function normalizes input
- **Default**: 'general' if invalid input provided

## Relationships

- `messages.conversation_id` → `conversations.id` (1:many)
- `conversation_index.session_id` → `conversations.id` (1:1)
- When project switch occurs, new conversation created, old conversation preserved via indexing

## Data Flow

### Project Switch Flow (EXACT ORDER)
```
User types /thn
  ↓
handle_command() detects project switch
  ↓
STEP 1: Save current conversation
  ↓
save_current_conversation(conv_id, current_project)
  ↓
index_session(conv_id) → saves to conversation_index
  ↓
Wait for save to complete
  ↓
STEP 2: Prompt for new title
  ↓
Prompt "Conversation title for THN (required):"
  ↓
User enters title (loop until non-empty)
  ↓
STEP 3: Switch to new project context
  ↓
create_conversation(new_title, "THN")
  ↓
Update conv_id to new conversation UUID
  ↓
Update current_project to "THN"
  ↓
Display "Switched active project context to THN 🟢"
  ↓
STEP 4: Continue conversation
  ↓
Continue with new conversation_id and new project context
```

### Exit Flow
```
User types /exit or Ctrl+C
  ↓
save_current_conversation(conv_id, current_project)
  ↓
index_session(conv_id) → saves to conversation_index
  ↓
display_usage_summary()
  ↓
Exit program
```

