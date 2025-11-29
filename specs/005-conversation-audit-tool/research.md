# Research: Conversation Audit Tool

**Feature**: 005-conversation-audit-tool  
**Date**: 2025-01-27

## Research Tasks

### 1. Database query patterns for listing conversations

**Question**: How should we query conversations by project, ID, or title efficiently?

**Findings**:
- `conversations` table has indexes on `project` and `created_at`
- `conversation_index` table has indexes on `project` and `indexed_at`
- Need to join or query both tables to get complete information
- Message count requires COUNT query on `messages` table grouped by `conversation_id`

**Decision**: Use separate queries for each view mode:
- By project: Query `conversations` table filtered by project, join with COUNT subquery for message count
- By ID: Direct lookup by UUID primary key
- By title: Use ILIKE for case-insensitive partial matching

**Rationale**: Simple, efficient queries that leverage existing indexes. Separate queries keep code clear and maintainable.

**Alternatives considered**:
- Complex JOIN queries: Rejected - unnecessary complexity for single-user tool
- Full table scan: Rejected - inefficient, use indexes instead

---

### 2. Message history display format

**Question**: How should messages be displayed to users for review?

**Findings**:
- Messages stored with `role` (user/assistant) and `content`
- Messages have `created_at` timestamp
- Conversations can have many messages (potentially hundreds)

**Decision**: Display messages in chronological order with clear role indicators:
- Format: `[USER]` or `[ASSISTANT]` prefix
- Show messages in order (oldest first)
- Limit to 50 messages initially with option to load more
- Display message number and timestamp for context

**Rationale**: Clear, readable format. Chronological order helps users understand conversation flow. Limiting initial display prevents overwhelming output.

**Alternatives considered**:
- Reverse chronological: Rejected - harder to follow conversation flow
- No limit: Rejected - could display thousands of messages
- Pagination with page numbers: Considered - may add later if needed

---

### 3. Editing conversation project - data consistency

**Question**: How to ensure `conversations.project` and `conversation_index.project` stay in sync when editing?

**Findings**:
- `conversations` table has `project` field
- `conversation_index` table has `project` field (may not exist for all conversations)
- Foreign key relationship: `conversation_index.session_id` → `conversations.id`
- When project is edited, both tables should be updated

**Decision**: Use a transaction to update both tables atomically:
1. Update `conversations.project`
2. Update `conversation_index.project` WHERE `session_id = conversation_id` (if exists)
3. Commit transaction

**Rationale**: Ensures data consistency. Transaction guarantees both updates succeed or both fail. Handles case where conversation is not indexed.

**Alternatives considered**:
- Update only conversations table: Rejected - conversation_index would be out of sync
- Update only conversation_index: Rejected - conversations table is source of truth
- Separate updates without transaction: Rejected - risk of partial updates

---

### 4. Deleting conversations - cascade behavior

**Question**: What happens when a conversation is deleted? Should we rely on CASCADE or delete explicitly?

**Findings**:
- `messages` table has `ON DELETE CASCADE` foreign key to `conversations`
- `conversation_index` table has `ON DELETE CASCADE` foreign key to `conversations`
- Database handles cascading deletes automatically

**Decision**: Delete from `conversations` table only. Let database CASCADE handle:
- All messages in `messages` table
- Entry in `conversation_index` table (if exists)

**Rationale**: Simpler code, database handles referential integrity. CASCADE is already configured, so we can rely on it.

**Alternatives considered**:
- Explicit deletion from all tables: Rejected - unnecessary, CASCADE handles it
- Soft delete (mark as deleted): Considered - not needed for audit tool, hard delete is appropriate

---

### 5. CLI menu system design

**Question**: How should the interactive menu system work?

**Findings**:
- Need main menu with options
- Need sub-menus for different views
- Need command-based interface for message review mode
- Python `input()` function for user input

**Decision**: Use simple menu system:
- Main menu: Numbered options (1, 2, 3) for different view modes
- After selecting view mode: Display results, then prompt for action
- Message review mode: Command-based (`/messages <id>`, `/edit-title`, `/edit-project`, `/delete`)
- Use `input()` for all user input with clear prompts

**Rationale**: Simple, familiar CLI pattern. No need for complex libraries. Easy to understand and maintain.

**Alternatives considered**:
- Use `click` or `argparse` library: Rejected - overkill for simple interactive tool
- Use `rich` library for formatting: Considered - may add later for better UI, but not required
- Web interface: Rejected - violates "simple CLI tool" requirement

---

### 6. Input validation and error handling

**Question**: How to validate user inputs (UUIDs, project names, titles)?

**Findings**:
- UUIDs can be validated using `uuid.UUID()` constructor
- Project names must be one of: THN, DAAS, FF, 700B, general
- Titles must be non-empty strings
- Database queries can fail (connection errors, invalid IDs)

**Decision**: Validate inputs at CLI level before database queries:
- UUID validation: Try `uuid.UUID(input)` and catch `ValueError`
- Project validation: Check against allowed list
- Title validation: Check non-empty after `.strip()`
- Database errors: Catch `psycopg2` exceptions and display user-friendly messages

**Rationale**: Fail fast with clear error messages. Validate before hitting database to avoid unnecessary queries.

**Alternatives considered**:
- Let database validate: Rejected - database errors are less user-friendly
- No validation: Rejected - poor UX, unclear error messages

---

## Technical Decisions Summary

1. **Query Patterns**: Separate queries for each view mode, leverage existing indexes
2. **Message Display**: Chronological order, role prefixes, limit to 50 initially
3. **Project Editing**: Use transaction to update both `conversations` and `conversation_index` tables
4. **Deletion**: Delete from `conversations` only, rely on CASCADE for related records
5. **Menu System**: Simple numbered menu with command-based message review mode
6. **Input Validation**: Validate UUIDs, project names, and titles at CLI level before database operations

## Implementation Approach

1. Create `audit_conversations.py` script with main menu
2. Implement query functions for listing by project/ID/title
3. Implement message viewing function
4. Implement edit functions (title, project) with transaction support
5. Implement delete function with confirmation
6. Add input validation and error handling throughout

## No Unresolved Clarifications

All technical questions have been resolved. Implementation can proceed to Phase 1 design.

