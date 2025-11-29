# Feature Specification: Conversation Audit Tool

**Feature Branch**: `005-conversation-audit-tool`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Since we've now streamlined the conversation/project tag system. I'd like to now go back into the conversation history and make manually updates to the organize them properly. I'd a new script, where I run python audit_conversations.py where the user has the capabilities to manage conversation history. The goal is make sure the conversation index database is cleaned and optimized."

## User Scenarios & Testing

### User Story 1 - List Conversations by Project (Priority: P1)

A user wants to review all conversations associated with a specific project to identify misclassified conversations that need cleanup.

**Why this priority**: This is the primary entry point for the audit tool. Users need to see conversations grouped by project to identify issues.

**Independent Test**: Can be fully tested by running `python audit_conversations.py`, selecting "conversations by project", choosing a project, and verifying that all conversations for that project are listed with id, title, project, and message count.

**Acceptance Scenarios**:

1. **Given** the user runs `python audit_conversations.py`, **When** they select "conversations by project", **Then** the system prompts for a project name and lists all conversations for that project with: id, title, project, number of messages
2. **Given** the user selects a project that has no conversations, **When** the system queries the database, **Then** it displays "No conversations found for project [PROJECT]"
3. **Given** the user selects a project with many conversations, **When** the list is displayed, **Then** conversations are sorted by creation date (newest first) or indexed date (newest first)

---

### User Story 2 - List Conversation by ID (Priority: P1)

A user wants to view details of a specific conversation when they know its ID.

**Why this priority**: Users may have conversation IDs from logs or other sources and need to quickly access them.

**Independent Test**: Can be fully tested by running `python audit_conversations.py`, selecting "conversation by id", entering a valid conversation ID, and verifying the conversation details are displayed.

**Acceptance Scenarios**:

1. **Given** the user runs `python audit_conversations.py`, **When** they select "conversation by id" and enter a valid conversation ID, **Then** the system displays the conversation details: id, title, project, number of messages, created_at
2. **Given** the user enters an invalid conversation ID, **When** the system queries the database, **Then** it displays "Conversation not found: [ID]"

---

### User Story 3 - List Conversation by Title (Priority: P1)

A user wants to find a conversation by searching for its title.

**Why this priority**: Users often remember conversations by title rather than ID, so title search is essential.

**Independent Test**: Can be fully tested by running `python audit_conversations.py`, selecting "conversation by title", entering a title (or partial title), and verifying matching conversations are displayed.

**Acceptance Scenarios**:

1. **Given** the user runs `python audit_conversations.py`, **When** they select "conversation by title" and enter a title (exact or partial match), **Then** the system displays all matching conversations with: id, title, project, number of messages
2. **Given** the user enters a title that matches multiple conversations, **When** the system queries the database, **Then** it displays all matches and allows the user to select which one to review
3. **Given** the user enters a title with no matches, **When** the system queries the database, **Then** it displays "No conversations found matching '[TITLE]'"

---

### User Story 4 - Review Message History (Priority: P2)

A user wants to review the message history of a conversation to determine if it's properly classified or needs cleanup.

**Why this priority**: Reviewing messages is essential for determining if a conversation is misclassified or contains mixed project content.

**Independent Test**: Can be fully tested by running `python audit_conversations.py`, selecting any list option, then typing `/messages <conversation_id>`, and verifying the message history is displayed in a readable format.

**Acceptance Scenarios**:

1. **Given** the user is viewing a conversation list or details, **When** they type `/messages <conversation_id>`, **Then** the system displays all messages for that conversation in chronological order with role (user/assistant) and content
2. **Given** the user types `/messages` with an invalid conversation ID, **When** the system queries the database, **Then** it displays "Conversation not found: [ID]"
3. **Given** a conversation has many messages, **When** the messages are displayed, **Then** they are paginated or limited to a reasonable number (e.g., 50) with option to see more

---

### User Story 5 - Edit Conversation Title (Priority: P2)

A user wants to update a conversation's title when reviewing its message history to better reflect its content.

**Why this priority**: Titles are important for organization. Users need to fix incorrect or unclear titles during audit.

**Independent Test**: Can be fully tested by running `/messages <conversation_id>`, then typing a command to edit the title, entering a new title, and verifying the title is updated in the database.

**Acceptance Scenarios**:

1. **Given** the user is viewing message history with `/messages <conversation_id>`, **When** they type a command to edit title (e.g., `/edit-title` or `/title`), **Then** the system prompts for a new title
2. **Given** the user enters a new title, **When** the system updates the database, **Then** it displays "Title updated successfully" and shows the updated title
3. **Given** the user enters an empty title, **When** the system validates input, **Then** it displays "Title cannot be empty" and prompts again

---

### User Story 6 - Edit Conversation Project (Priority: P2)

A user wants to change a conversation's project tag when reviewing its message history to correct misclassification.

**Why this priority**: This is the core cleanup functionality - fixing conversations that are tagged with the wrong project.

**Independent Test**: Can be fully tested by running `/messages <conversation_id>`, then typing a command to edit the project, entering a new project name, and verifying the project is updated in both `conversations` and `conversation_index` tables.

**Acceptance Scenarios**:

1. **Given** the user is viewing message history with `/messages <conversation_id>`, **When** they type a command to edit project (e.g., `/edit-project` or `/project`), **Then** the system prompts for a new project name
2. **Given** the user enters a valid project name (THN, DAAS, FF, 700B, general), **When** the system updates the database, **Then** it updates both `conversations.project` and `conversation_index.project` (if indexed), and displays "Project updated successfully"
3. **Given** the user enters an invalid project name, **When** the system validates input, **Then** it displays "Invalid project. Must be one of: THN, DAAS, FF, 700B, general" and prompts again

---

### User Story 7 - Delete Conversation (Priority: P3)

A user wants to delete a conversation entirely when it's too jumbled with different projects and not worth fixing.

**Why this priority**: Some conversations may be too mixed to clean up. Deletion is a last resort but should be available.

**Independent Test**: Can be fully tested by running `/messages <conversation_id>`, then typing a delete command, confirming deletion, and verifying the conversation and its messages are removed from the database.

**Acceptance Scenarios**:

1. **Given** the user is viewing message history with `/messages <conversation_id>`, **When** they type a command to delete (e.g., `/delete` or `/remove`), **Then** the system prompts "Are you sure you want to delete this conversation? (yes/no)"
2. **Given** the user confirms with "yes", **When** the system deletes the conversation, **Then** it removes the conversation from `conversations` table, all messages from `messages` table, and the entry from `conversation_index` table (if exists), and displays "Conversation deleted successfully"
3. **Given** the user confirms with "no" or anything else, **When** the system processes the response, **Then** it cancels the deletion and returns to message view
4. **Given** the user types "yes" but the deletion fails, **When** the system encounters an error, **Then** it displays an error message and does not delete the conversation

---

### Edge Cases

- What happens if a conversation has no messages? (Display message count as 0, allow editing/deletion)
- What happens if a conversation is not indexed? (Allow editing title/project, deletion still works)
- What happens if user tries to edit a conversation that doesn't exist? (Display error, return to main menu)
- What happens if database connection fails? (Display error, exit gracefully)
- What happens if user cancels input with Ctrl+C? (Handle gracefully, return to previous menu)

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a main menu with options: "conversations by project", "conversation by id", "conversation by title"
- **FR-002**: System MUST list conversations by project showing: id, title, project, number of messages
- **FR-003**: System MUST display conversation details when queried by ID showing: id, title, project, number of messages, created_at
- **FR-004**: System MUST search conversations by title (exact or partial match) and display matching results
- **FR-005**: System MUST support `/messages <conversation_id>` command to view message history
- **FR-006**: System MUST display messages in chronological order with role (user/assistant) and content
- **FR-007**: System MUST support editing conversation title while viewing message history
- **FR-008**: System MUST support editing conversation project while viewing message history
- **FR-009**: System MUST update both `conversations.project` and `conversation_index.project` when project is edited
- **FR-010**: System MUST support deleting conversations with confirmation prompt
- **FR-011**: System MUST delete conversation from `conversations`, all messages from `messages`, and entry from `conversation_index` when deleted
- **FR-012**: System MUST validate project names (THN, DAAS, FF, 700B, general)
- **FR-013**: System MUST validate that title is not empty when editing

### Key Entities

- **Conversation**: Represents a chat session with id, title, project, created_at. Can be queried, edited, or deleted.
- **Message**: Individual user/assistant messages linked to a conversation. Displayed when reviewing conversation history.
- **Conversation Index**: Indexed metadata for conversations. Project field must be kept in sync with conversations table.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can list all conversations for a project in under 2 seconds
- **SC-002**: Users can find a conversation by ID or title in under 1 second
- **SC-003**: Users can review message history for any conversation
- **SC-004**: Users can successfully edit conversation titles and projects
- **SC-005**: Project edits update both `conversations` and `conversation_index` tables correctly
- **SC-006**: Deleted conversations are completely removed from all related tables
- **SC-007**: All database operations use parameterized queries (no SQL injection vulnerabilities)

