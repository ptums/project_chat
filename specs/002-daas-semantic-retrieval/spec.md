# Feature Specification: DAAS Semantic Dream Retrieval and Streaming Responses

**Feature Branch**: `002-daas-semantic-retrieval`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "The DAAS project is designed for dream analysis and often times I'll ask to review a dream from a variety of perspectives Christian, Jungian, Pagan, etc. Currently, it is having a hard time providing the optimal response when I want to discuss a dream. So I'd like to update project_chat in three ways: 1. DAAS will have custom retrieval rules. 2. Implement Semantic Vector Embedding in DAAS project entries only. 3. Currently, from a UI perspective the response come out in a single block of text. I prefer to have the text cascaded down and mimic the experience of using ChatGPT"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single Dream Analysis by Title (Priority: P1)

A user wants to analyze a specific dream they've previously recorded. They reference the dream by its title in quotes, expecting the system to retrieve only that specific dream's context and provide analysis from multiple perspectives (Christian, Jungian, Pagan, etc.).

**Why this priority**: This is the most common use case - users want to revisit and analyze specific dreams they've already discussed. It requires precise retrieval to avoid mixing contexts from other dreams.

**Independent Test**: Can be fully tested by asking "Analyze 'Dream Title Here' from a Christian perspective" and verifying that only the matching dream is retrieved, no other dreams are included, and the response focuses solely on that dream.

**Acceptance Scenarios**:

1. **Given** a user has multiple dreams stored in DAAS project, **When** the user asks "What does 'My Flying Dream' mean from a Jungian perspective?", **Then** the system retrieves only the conversation titled "My Flying Dream" (or matching title) and provides analysis using only that dream's context
2. **Given** a user message contains a quoted title like "Dream Title", **When** the system processes the query, **Then** it uses title-based matching (pattern matching or slug/tag matching) and excludes all other dreams from the context, even if keywords overlap
3. **Given** a quoted title matches multiple conversations, **When** the system retrieves matches, **Then** it uses the most recent or most relevant match and does not mix multiple dreams in the response

---

### User Story 2 - Pattern-Based Dream Analysis Across Dreams (Priority: P2)

A user wants to explore themes, symbols, or patterns that appear across multiple dreams. They ask questions without referencing a specific dream title, expecting the system to find relevant dreams using semantic similarity and provide insights about recurring patterns.

**Why this priority**: This enables high-level analysis and pattern recognition across the user's dream history, which is essential for Jungian analysis and long-term meaning discovery. It requires semantic understanding beyond keyword matching.

**Independent Test**: Can be fully tested by asking "What patterns do I have with water in my dreams?" and verifying that the system uses vector similarity search to find relevant dreams, retrieves top-k most semantically similar dreams, and provides analysis across those dreams.

**Acceptance Scenarios**:

1. **Given** a user message does not contain a quoted title, **When** the user asks "What recurring symbols appear in my dreams?", **Then** the system computes an embedding for the user message and performs vector similarity search across all DAAS dreams to find the most relevant entries
2. **Given** multiple dreams contain similar themes but different wording, **When** the user asks about those themes, **Then** the system retrieves dreams based on semantic similarity rather than exact keyword matches, enabling pattern detection across varied language
3. **Given** vector similarity search returns top-k relevant dreams, **When** building context for the response, **Then** the system uses only those top-k dreams and does not include dreams that don't match semantically, even if they share some keywords

---

### User Story 3 - Streaming Response Display (Priority: P3)

A user receives responses that appear progressively word-by-word or chunk-by-chunk, mimicking the ChatGPT experience, rather than waiting for the complete response to appear all at once.

**Why this priority**: This improves perceived responsiveness and user engagement. Users prefer to see responses as they're generated rather than waiting for complete blocks of text, especially for longer analyses.

**Independent Test**: Can be fully tested by sending a query and observing that the response text appears incrementally rather than as a single complete block, with text cascading down the screen as it's generated.

**Acceptance Scenarios**:

1. **Given** the system generates a response for a DAAS dream analysis query, **When** the response is being generated, **Then** the text appears progressively (word-by-word or chunk-by-chunk) rather than as a single complete block
2. **Given** a user is viewing a streaming response, **When** new text arrives, **Then** it appears below the existing text, cascading down the display, creating a natural reading experience
3. **Given** the system supports streaming responses, **When** responses are displayed, **Then** the experience mimics ChatGPT's progressive text display, providing immediate feedback to the user

---

### Edge Cases

- What happens when a quoted title matches no dreams? (System should indicate no match found and ask for clarification)
- What happens when a quoted title matches multiple dreams with similar titles? (System should use the most recent or most relevant match)
- What happens when vector similarity search returns no relevant dreams? (System should indicate no relevant patterns found)
- How does the system handle malformed quotes or partial titles? (System should detect valid quote patterns and handle edge cases gracefully)
- What happens when a user mixes quoted title syntax with pattern query intent? (System should prioritize quoted title detection and use single-dream mode)
- How does the system handle very long dream titles in quotes? (System should truncate or handle appropriately for matching)
- What happens when streaming is interrupted or connection is lost? (System should handle gracefully with appropriate error messaging)
- How does the system handle responses that are too short to benefit from streaming? (System may display immediately or still use streaming for consistency)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect when a user message contains a quoted title (text within quotes like "Title") for DAAS project queries
- **FR-002**: System MUST use title-based matching (pattern matching or slug/tag matching) when a quoted title is detected in DAAS project queries
- **FR-003**: System MUST retrieve only the matching dream conversation when a quoted title is detected, excluding all other dreams from context even if keywords overlap
- **FR-004**: System MUST NOT mix single-dream and pattern-based retrieval modes in the same query processing step
- **FR-005**: System MUST use vector similarity search (semantic embedding-based) when no quoted title is detected in DAAS project queries
- **FR-006**: System MUST compute embeddings for user messages when performing pattern-based queries in DAAS project
- **FR-007**: System MUST store and maintain vector embeddings for all DAAS project conversation entries in conversation_index
- **FR-008**: System MUST perform vector similarity search over stored embeddings for DAAS project entries to find top-k relevant dreams
- **FR-009**: System MUST apply custom retrieval rules only to DAAS project queries, leaving other projects (THN, FF, 700B, general) unchanged
- **FR-010**: System MUST generate responses that appear progressively (streaming) rather than as complete blocks for all queries
- **FR-011**: System MUST display streaming text in a cascading format where new text appears below existing text
- **FR-012**: System MUST support conversational, chunked responses that allow users to prompt for more information incrementally rather than receiving large monolithic responses

### Key Entities

- **Dream Conversation**: A stored conversation in the DAAS project representing a single dream analysis session. Has attributes: title, project tag (DAAS), content, and vector embedding (for semantic search)
- **Conversation Index Entry**: A structured record containing metadata about a dream conversation, including title, summary, tags, and vector embedding for DAAS entries
- **User Query**: A message from the user that may contain either a quoted title (single-dream mode) or pattern-based question (vector search mode)
- **Vector Embedding**: A semantic representation of text content that enables similarity-based retrieval, stored for DAAS project entries only

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a user references a dream by quoted title, the system retrieves the correct dream 95% of the time (measured by user confirmation of correct dream retrieval)
- **SC-002**: When performing pattern-based queries, the system retrieves semantically relevant dreams (top-k) that users confirm as relevant 80% of the time, even when exact keywords don't match
- **SC-003**: Single-dream queries complete without including context from other dreams 100% of the time (zero false positives for dream mixing)
- **SC-004**: Responses begin appearing to users within 2 seconds of query submission (perceived responsiveness for streaming)
- **SC-005**: Users report improved satisfaction with dream analysis quality, specifically noting better pattern recognition and theme detection across dreams (qualitative feedback indicates improvement)
- **SC-006**: Streaming responses provide a ChatGPT-like experience as confirmed by user feedback comparing before/after experience
- **SC-007**: Vector embeddings enable retrieval of relevant dreams even when user query uses different wording than stored dreams (semantic similarity works across varied language)

## Assumptions

- Vector embeddings will be generated using a standard embedding model suitable for semantic text similarity
- Storage for conversation metadata will be extended to include embeddings for DAAS project entries
- Existing DAAS conversations will need their embeddings generated during implementation (backfill process)
- Streaming response capability will work across both CLI and API interfaces
- Users will use consistent quote styles (double quotes) when referencing dream titles, though the system should handle variations
- The top-k value for vector similarity search will be configurable, with a reasonable default (e.g., 5-10 most relevant dreams)
- Other projects (THN, FF, 700B, general) will continue using existing retrieval methods without vector embeddings initially

## Dependencies

- Vector embedding generation capability (embedding model/service)
- Storage infrastructure to support embedding data for conversation metadata
- Streaming response infrastructure (may require updates to both CLI and API interfaces)
- Existing conversation indexing infrastructure from previous features

## Out of Scope

- Applying vector embeddings to other projects (THN, FF, 700B, general) - this is explicitly deferred for future evaluation
- Changing the fundamental conversation storage or message structure
- Modifying retrieval behavior for non-DAAS projects
- Implementing advanced embedding fine-tuning or custom models
- Real-time embedding updates during conversation (embeddings generated during indexing phase)
