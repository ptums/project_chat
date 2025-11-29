# Feature Specification: Ollama Conversation Organizer

**Feature Branch**: `001-ollama-organizer`  
**Created**: 2025-11-25  
**Status**: Draft  
**Input**: User description: "This app is fully functional and does a decent job and retrieving data from db making sense of it and referencing it in our conversation. However, it isn't 100% accurate and there is room for improvement. I want to add another LLM model to this project to process and organizer the data better. For this I plan to use Ollama with the most optimial model for this project, we'll figure that out later."

## Clarifications

### Session 2025-01-27

- Q: Should the prompt sent to GPT-5.1-mini include summaries from project_knowledge table, and should they be ordered strategically (overview first, then conversation details)? → A: Yes, project_knowledge (stable overview) should appear FIRST in system prompts, followed by conversation_index (specific conversation details) SECOND

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save Conversation to Memory Layer (Priority: P1)

When a conversation ends and the user types `/save`, the backend should run an Ollama-powered "conversation organizer" that stores a structured memory record (summary, title, tags, project classification, key entities/topics, memory blurb) for that session.

**Why this priority**: Without the structured memory record, later sessions cannot benefit from improved context, so this is the foundation for the feature.

**Independent Test**: Complete a conversation, run `/save`, and verify a new index entry exists with all required fields populated.

**Acceptance Scenarios**:

1. **Given** a completed conversation, **When** the user types `/save`, **Then** the system loads the session transcript and sends it to Ollama with the organizer prompt.
2. **Given** Ollama returns structured data, **When** the backend processes the response, **Then** the conversation index table is updated with summary, title, tags, classification, entities, topics, and memory blurb.
3. **Given** the `/save` command is run multiple times for the same session, **When** the backend processes the request, **Then** the most recent structured data replaces the previous record for that session (latest write wins).
4. **Given** Ollama fails or times out, **When** the user types `/save`, **Then** the system reports the failure and does not write partial data.

---

### User Story 2 - Load Project Memory Before New Sessions (Priority: P2)

When the user starts or resumes a session for a project, the system should fetch structured memory from both the `project_knowledge` table (stable overview) and the `conversation_index` table (specific conversation details) so GPT-5.1-mini receives comprehensive, strategically-ordered context before responding.

**Why this priority**: The goal is sharper continuity; sessions must pull the organized memory for the feature to deliver value. Strategic ordering ensures foundational project knowledge appears first, followed by specific conversation context.

**Independent Test**: Create an index entry via `/save`, start a new session for the same project, and confirm both the `project_knowledge` summaries and stored conversation memory are injected into the initial context prompt in the correct order.

**Acceptance Scenarios**:

1. **Given** a project with both `project_knowledge` entries and indexed conversations, **When** a new session starts for that project, **Then** the system loads `project_knowledge` summaries FIRST (as foundational overview), followed by relevant `conversation_index` entries SECOND (as specific conversation details), and injects both into GPT-5.1-mini's system/context prompts in this strategic order.
2. **Given** multiple indexed sessions for a project, **When** a new session starts, **Then** the system selects the most relevant conversation index entries (top 3-5 via relevance scoring) and includes them after the project_knowledge overview.
3. **Given** only `project_knowledge` exists (no indexed conversations), **When** a new session starts, **Then** the system includes the project_knowledge summaries in the context prompt.
4. **Given** only indexed conversations exist (no project_knowledge), **When** a new session starts, **Then** the system includes the conversation_index context in the context prompt.
5. **Given** no indexed data exists for a project, **When** a new session starts, **Then** the system proceeds normally without additional context.
6. **Given** the user switches projects mid-session, **When** the project context changes, **Then** the system fetches the appropriate `project_knowledge` and `conversation_index` entries for the newly selected project, maintaining the strategic ordering.

---

### User Story 3 - Inspect and Manage Conversation Memory (Priority: P3)

The user needs lightweight commands (CLI/API) to list, view, refresh, or delete conversation index entries to keep the memory layer trustworthy.

**Why this priority**: Visibility and control help the user trust and tune the memory layer, especially when the stored context affects future conversations.

**Independent Test**: Run the memory management commands (e.g., `/memory list`, `/memory view <id>`, `/memory refresh <id>`, `/memory delete <id>`) and verify expected results.

**Acceptance Scenarios**:

1. **Given** indexed records exist, **When** the user runs `/memory list`, **Then** the system displays stored summaries with timestamps, projects, and tags.
2. **Given** a specific indexed record, **When** the user runs `/memory view <id>`, **Then** the system shows the structured fields returned by Ollama.
3. **Given** a record is outdated, **When** the user runs `/memory refresh <id>`, **Then** the system reruns the organizer prompt and updates the stored entry.
4. **Given** the user requests deletion of an incorrect entry, **When** the command succeeds, **Then** the record is removed or marked inactive so it no longer primes new sessions.

---

### Edge Cases

- What happens when Ollama is offline or times out during `/save`? (System must retry per policy or inform user without writing partial data.)
- How does the system handle transcripts that exceed Ollama/model token limits? (Need chunking or summary-reduction strategy.)
- What happens if structured fields exceed storage limits (e.g., overly long memory blurb)? (Truncate or refuse with clear message.)
- How are concurrent `/save` requests for the same session handled? (Define locking/last-write behavior.)
- How does the system behave when the conversation index grows large? (Pagination and retention rules for inspection commands.)
- What is the fallback when `/save` is triggered before any conversation content exists? (Warn and cancel.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST capture the configured transcript slice (full session or last N messages) when the user runs `/save`.
- **FR-002**: System MUST send the captured transcript to an Ollama endpoint with a configurable "conversation organizer" prompt.
- **FR-003**: System MUST persist the structured response (summary, title, tags, classification, entities, topics, memory blurb, timestamps, model used) to a conversation index store tied to the session/project.
- **FR-004**: System MUST expose a `/save` command in the CLI that triggers the organizer workflow and reports success/failure to the user.
- **FR-005**: System MUST fetch context from both `project_knowledge` table (stable overview summaries) and `conversation_index` table (specific conversation details) whenever a session starts or project context changes, injecting both into GPT-5.1-mini's context with strategic ordering: `project_knowledge` summaries FIRST (foundational overview), followed by relevant `conversation_index` entries SECOND (specific conversation context).
- **FR-006**: System MUST provide CLI/API commands to list, view, refresh, and delete conversation index entries with clear feedback.
- **FR-007**: System MUST handle Ollama errors gracefully (retry configurable times, log failures, notify user).
- **FR-008**: System MUST enforce configurable transcript length limits before sending to Ollama (e.g., max tokens, fallback summarization).
- **FR-009**: System MUST track metadata (session ID, project, organizer model name, created_at, updated_at, last refreshed_by) for every index entry.
- **FR-010**: System MUST only persist entries when the organizer call succeeds; partial or failed runs must not modify the index.
- **FR-011**: System MUST allow future replacement of the Ollama model or prompt without schema/code changes (model name stored as data/config).
- **FR-012**: System MUST log organizer jobs (inputs, outputs, errors, duration) for auditing while respecting privacy (no raw secrets in logs).

### Key Entities *(include if feature involves data)*

- **ConversationIndex**: Structured memory per session/project with fields such as session_id, project, title, summary, tags, key_entities, topics, memory_blurb, classification, model_name, created_at, updated_at, refreshed_by.
- **OrganizerJob**: Tracks `/save` executions (job_id, session_id, trigger_source, status, retry_count, error_message, started_at, finished_at, duration_ms).
- **ConversationTranscript**: Logical set of ordered messages {role, content, timestamp} extracted for organizer input (may be truncated per policy).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `/save` commands complete (success or clear failure) within 10 seconds for transcripts under 200 messages, excluding external downtime.
- **SC-002**: 95% of new or resumed sessions load their associated memory entry before the first user prompt is answered.
- **SC-003**: Users report at least a 50% reduction in "remind me what we discussed" prompts after one week of using the memory layer (self-reported metric).
- **SC-004**: Memory inspection commands return results in under 2 seconds for up to 500 indexed sessions.
- **SC-005**: Organizer job failure rate remains below 5% per week after automatic retries (excluding deliberate cancellations).

## Assumptions

- Ollama runs locally or on a trusted internal endpoint reachable by the backend.
- GPT-5.1-mini remains the live conversational model; this feature only augments context.
- Conversation transcripts already exist in PostgreSQL and can be reloaded without performance issues.
- Organizer prompt text and model selection will be managed via configuration and can evolve without schema changes.
- Conversation index data lives in the same PostgreSQL instance (new table) and inherits existing backup policies.
- Memory management commands are CLI-only for this iteration; UI dashboards are future work.

## Dependencies

- Existing conversation/message storage and retrieval logic.
- CLI command processor that already handles `/paste`, `/context`, etc.
- Ollama installation with an appropriate model and prompt tuned for organizing conversations.
- Database migrations to add the conversation index table(s).
- Logging/monitoring infrastructure to capture organizer job metrics.

## Out of Scope

- Automatic organizer runs after every message (manual `/save` only).
- Semantic search or vector retrieval across conversation index entries.
- Multi-user tenancy or permission controls for memory management.
- Visual dashboards beyond textual CLI/API responses.
- Automatic conflict resolution between multiple organizers (manual refresh governs updates).
