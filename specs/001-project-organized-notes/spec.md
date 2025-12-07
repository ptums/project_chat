# Feature Specification: Project-Organized Meditation Notes Integration

**Feature Branch**: `001-project-organized-notes`  
**Created**: 2025-12-07  
**Status**: Draft  
**Input**: User description: "Okay now that the MCP works. There needs to be some organization because the directories within the obsidian notebook have meaning. I've just reorganized the directory structure of the obsidian notebook. There is now a directory that aligns with each of the projects daas, thn, ff, general, 700b. So now I want to ensure that I can pull notes into a conversation when i am working with in a specific project. Also I'd like to be able to run a command that will save the conversation as a note with in the project directory of the obsidian notebook"

## User Scenarios & Testing

### User Story 1 - Project-Scoped Note Retrieval and Recall (Priority: P1)

When working within a specific project (DAAS, THN, FF, General, 700B), the system should automatically retrieve and include relevant meditation notes from the corresponding project directory in the Obsidian notebook. The system must be able to recall information from these notes when requested and reference them naturally as the conversation progresses.

**Why this priority**: This is the core functionality - enabling project-specific context from meditation notes. The system should not just include notes, but actively use them to answer questions and maintain context throughout the conversation.

**Independent Test**: Can be fully tested by setting project context to "DAAS", asking about information from a note, and verifying the system recalls and references the note content accurately.

**Acceptance Scenarios**:

1. **Given** user is in a DAAS project conversation, **When** system builds context, **Then** only meditation notes from the "daas" directory are included
2. **Given** user is in a THN project conversation, **When** system builds context, **Then** only meditation notes from the "thn" directory are included
3. **Given** user switches from DAAS to THN project, **When** system builds context, **Then** notes switch from "daas" to "thn" directory
4. **Given** no notes exist in a project directory, **When** system builds context, **Then** no meditation notes are included (graceful degradation)
5. **Given** user asks "What did I write about morning routines?", **When** system responds, **Then** it recalls and references relevant content from meditation notes
6. **Given** user references a topic from earlier in conversation, **When** system responds, **Then** it maintains context and can reference related note content from earlier in the conversation

---

### User Story 2 - Save Conversation as Note (Priority: P1)

User can save the current conversation as a markdown note in the appropriate project directory of the Obsidian notebook repository.

**Why this priority**: This enables bidirectional flow - not just reading notes, but also writing conversations back to the notebook. This creates a complete integration loop.

**Independent Test**: Can be fully tested by running a save command in a DAAS conversation and verifying a new markdown file is created in the "daas" directory of the repository.

**Acceptance Scenarios**:

1. **Given** user is in a DAAS project conversation, **When** user runs `/mcp save`, **Then** conversation is saved as a markdown note in the "daas" directory
2. **Given** user is in a THN project conversation, **When** user runs `/mcp save`, **Then** conversation is saved as a markdown note in the "thn" directory
3. **Given** conversation has multiple messages, **When** user runs `/mcp save`, **Then** all messages are formatted as a coherent markdown document
4. **Given** user provides a title, **When** user runs `/mcp save "My Title"`, **Then** note is saved with that title
5. **Given** user doesn't provide a title, **When** user runs `/mcp save`, **Then** system generates a title from conversation content

---

### User Story 3 - Project Directory Mapping (Priority: P2)

System correctly maps project names (DAAS, THN, FF, General, 700B) to their corresponding directory names in the Obsidian notebook (daas, thn, ff, general, 700b).

**Why this priority**: Ensures correct directory mapping between project tags and Obsidian directory structure. Lower priority because it's a configuration/mapping concern.

**Independent Test**: Can be fully tested by verifying the mapping logic correctly translates "DAAS" → "daas", "THN" → "thn", etc.

**Acceptance Scenarios**:

1. **Given** project name is "DAAS", **When** system looks up directory, **Then** it uses "daas" directory
2. **Given** project name is "General", **When** system looks up directory, **Then** it uses "general" directory
3. **Given** project name doesn't have a mapping, **When** system looks up directory, **Then** it uses a default directory or handles gracefully

---

### Edge Cases

- What happens when a project directory doesn't exist in the repository?
- How does system handle notes in subdirectories within project directories?
- What happens if saving a note fails (permissions, disk space, etc.)?
- How are duplicate note titles handled when saving?
- What happens if the repository is out of sync when saving?

## Requirements

### Functional Requirements

- **FR-001**: System MUST filter meditation notes by project directory when building conversation context
- **FR-002**: System MUST map project names (DAAS, THN, FF, General, 700B) to lowercase directory names (daas, thn, ff, general, 700b)
- **FR-003**: System MUST support saving conversations as markdown notes in the appropriate project directory
- **FR-004**: System MUST generate note filenames from conversation title or content
- **FR-005**: System MUST format conversations as valid Obsidian markdown with proper frontmatter
- **FR-006**: System MUST commit and push saved notes to the GitLab repository
- **FR-007**: System MUST handle cases where project directory doesn't exist (create it if needed)
- **FR-008**: System MUST preserve conversation structure (user messages, AI responses, timestamps) in saved notes
- **FR-009**: System MUST recall information from meditation notes when explicitly requested by the user
- **FR-010**: System MUST reference meditation note content naturally throughout the conversation as topics arise
- **FR-011**: System MUST maintain awareness of note content across multiple conversation turns

### Key Entities

- **ProjectNoteFilter**: Filters notes by project directory path
- **ConversationNote**: Represents a conversation saved as a markdown note
- **ProjectDirectoryMapper**: Maps project names to directory names

## Success Criteria

### Measurable Outcomes

- **SC-001**: When in a DAAS project conversation, only notes from "daas" directory are retrieved (100% accuracy)
- **SC-002**: User can save a conversation as a note in under 5 seconds
- **SC-003**: Saved notes are properly formatted and readable in Obsidian
- **SC-004**: Saved notes are successfully committed and pushed to GitLab repository
- **SC-005**: System handles all 5 project types (DAAS, THN, FF, General, 700B) correctly
- **SC-006**: When user asks about note content, system accurately recalls and references the information (90%+ accuracy)
- **SC-007**: System maintains note context across conversation turns and references relevant notes naturally
