# Feature Specification: Fix Conversation Saving and Project Switching

**Feature Branch**: `004-fix-conversation-saving`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "There are a bug in project_chat that I'd like to address. The way projects/titles are being saved is confusing and there is a lot of disorganization. For example, I'll start a conversation in general and discuss the hobbit and then switch over to THN and have a lengthy conversation about bitcoin and new project ideas. When I got and hit /save the hobbit conversation in general is grouped together with the bitcoin/project conversation in THN and I want these two conversations to be stored separately."

## User Scenarios & Testing

### User Story 1 - Auto-Save on Project Switch (Priority: P1)

When a user switches between projects during a conversation session, the system should automatically save the current conversation, then prompt for a new title, then switch to the new project context. This ensures conversations are properly separated by project and prevents mixing topics from different projects.

**Why this priority**: This is the core issue causing conversation disorganization. Without this, conversations from different projects get mixed together when saved.

**Independent Test**: Can be fully tested by starting a conversation in "general", adding messages, switching to "THN" using `/thn`, and verifying that: (1) the general conversation was saved, (2) the system prompts for a new title, (3) after entering the title, the project context switches to "THN", and (4) the conversation continues under the new project.

**Acceptance Scenarios**:

1. **Given** a user is in a conversation with project "general" and has exchanged messages, **When** the user types `/thn` to switch to project "THN", **Then** the system: (a) runs `/save` on the current conversation, (b) prompts "Conversation title for THN (required):", (c) after user enters title, switches project context to "THN", (d) continues the conversation under the new project
2. **Given** a user is in a conversation with project "THN" and has exchanged messages, **When** the user types `/daas` to switch to project "DAAS", **Then** the system: (a) runs `/save` on the current conversation, (b) prompts for new title, (c) after user enters title, switches project context to "DAAS", (d) continues the conversation under the new project
3. **Given** a user switches projects using `/project TAG` command, **When** the project changes, **Then** the system: (a) runs `/save` on the current conversation, (b) prompts for new title, (c) after user enters title, switches project context, (d) continues the conversation

---

### User Story 2 - Auto-Save on Exit (Priority: P1)

When a user exits the program using `/exit`, the system should automatically save the current conversation before exiting.

**Why this priority**: Ensures no conversation data is lost when the user exits, and maintains consistency with the auto-save behavior on project switch.

**Independent Test**: Can be fully tested by starting a conversation, exchanging messages, typing `/exit`, and verifying that the conversation was saved before the program exits.

**Acceptance Scenarios**:

1. **Given** a user is in an active conversation with messages, **When** the user types `/exit`, **Then** the system runs `/save` on the current conversation before displaying the usage summary and exiting
2. **Given** a user exits via Ctrl+C, **When** the signal handler is triggered, **Then** the system runs `/save` on the current conversation before displaying the usage summary and exiting

---

### User Story 3 - Mandatory Conversation Titles (Priority: P2)

When starting a new conversation, users must provide a title. The system should not allow skipping the title prompt by pressing Enter without input.

**Why this priority**: Titles are essential for organization. Making them mandatory ensures all conversations are properly labeled and searchable.

**Independent Test**: Can be fully tested by starting the program, pressing Enter when prompted for a title, and verifying that the system prompts again with "A title is required" instead of proceeding.

**Acceptance Scenarios**:

1. **Given** the program starts and prompts for "Conversation title", **When** the user presses Enter without entering text, **Then** the system displays "A title is required" and prompts again
2. **Given** the program prompts for a title, **When** the user enters a non-empty title, **Then** the system proceeds to the project selection prompt
3. **Given** the program prompts for a title, **When** the user enters only whitespace, **Then** the system treats it as empty and prompts again with "A title is required"

---

### User Story 4 - Title Prompt on Project Switch (Priority: P2)

When a user switches projects mid-conversation, the system must follow this exact sequence: (1) run `/save` to save the current conversation, (2) prompt for a new title for the conversation under the new project, (3) switch to the new project context, (4) continue the conversation.

**Why this priority**: When switching projects, the conversation context changes, so a new title helps distinguish this segment from the previous project's conversation. The order ensures the old conversation is saved before creating a new one.

**Independent Test**: Can be fully tested by starting a conversation in "general" with title "Hobbit Discussion", switching to "THN" using `/thn`, and verifying the exact sequence: (1) save completes, (2) title prompt appears, (3) after entering title, project context switches to "THN", (4) conversation continues.

**Acceptance Scenarios**:

1. **Given** a user is in a conversation with project "general" and title "Hobbit Discussion", **When** the user switches to "THN" using `/thn`, **Then** the system: (a) runs `/save` and completes saving, (b) prompts "Conversation title for THN (required):" and waits for input, (c) after user enters title, switches project context to "THN", (d) creates new conversation with new title and project, (e) continues the session
2. **Given** the system prompts for a new title after project switch, **When** the user presses Enter without entering text, **Then** the system displays "A title is required" and prompts again (does not switch project context until valid title provided)
3. **Given** the system prompts for a new title after project switch, **When** the user enters a title, **Then** the system: (a) creates a new conversation with that title and the new project, (b) switches project context, (c) continues the session with the new conversation

---

### Edge Cases

- What happens when `/save` fails during project switch? (System should handle error gracefully, possibly warn user but still allow switch)
- What happens when `/save` fails during exit? (System should handle error gracefully, possibly warn user but still allow exit)
- What happens if user cancels title input (Ctrl+C) during project switch? (System should handle cancellation gracefully)
- What happens when switching to the same project? (System should still run `/save` but may not need new title prompt)
- What happens when there are no messages in the conversation yet? (System should still run `/save` but may skip if no messages exist)

## Requirements

### Functional Requirements

- **FR-001**: System MUST automatically run `/save` command function when user switches projects using `/thn`, `/daas`, `/ff`, `/700b`, `/general`, or `/project TAG` commands
- **FR-002**: System MUST automatically run `/save` command function when user types `/exit` to leave the program
- **FR-003**: System MUST automatically run `/save` command function when user exits via Ctrl+C (SIGINT signal)
- **FR-004**: System MUST require a non-empty title when starting a new conversation (cannot skip with Enter)
- **FR-005**: System MUST display "A title is required" message when user attempts to skip title input with Enter
- **FR-006**: System MUST prompt for a new conversation title after project switch completes and `/save` finishes
- **FR-007**: System MUST require a non-empty title when prompted after project switch (cannot skip with Enter)
- **FR-008**: System MUST create a new conversation record with the new title and project when user switches projects and provides a new title
- **FR-009**: System MUST preserve existing functionality for project selection (default "general" still works)

### Key Entities

- **Conversation**: Represents a chat session with a title, project tag, and associated messages. When switching projects, a new conversation should be created.
- **Message**: Individual user/assistant messages that belong to a conversation. Messages should not be moved between conversations when project switches occur.

## Success Criteria

### Measurable Outcomes

- **SC-001**: When switching projects, conversations are saved 100% of the time before the switch occurs
- **SC-002**: When exiting, conversations are saved 100% of the time before exit
- **SC-003**: All new conversations have non-empty titles (0% of conversations have auto-generated default titles due to empty input)
- **SC-004**: When switching projects, users are prompted for a new title 100% of the time after save completes
- **SC-005**: Conversations from different projects are stored separately (no mixing of "general" and "THN" topics in the same saved conversation)

