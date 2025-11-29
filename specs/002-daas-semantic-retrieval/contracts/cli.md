# CLI Contracts: DAAS Semantic Dream Retrieval

## No New Commands

This feature does not introduce new CLI commands. Existing chat interface automatically uses DAAS-specific retrieval when:
- Project is set to DAAS (`/project DAAS` or initial project selection)
- User sends a message (quoted title or pattern query)

## Modified Behavior

### Chat Query Processing

**Input**: User message in DAAS project context

**Processing**:
1. Detect quoted title pattern: `"Dream Title"`
2. If found → Single-dream mode (title matching)
3. If not found → Pattern-based mode (vector similarity search)
4. Retrieve relevant context
5. Generate response with streaming

**Output**: Streaming response text (progressive display)

## Streaming Response Display

**Format**: Text appears progressively word-by-word or chunk-by-chunk

**Implementation**:
- Use OpenAI streaming API (`stream=True`)
- Print chunks as received via `sys.stdout.write()`
- Flush after each chunk: `sys.stdout.flush()`
- Handle line breaks appropriately
- Support Ctrl+C interruption gracefully

**User Experience**:
- Response begins appearing within 2 seconds
- Text cascades down the screen
- Mimics ChatGPT progressive display

## Error Handling

**No Match Found (Single-Dream Mode)**:
- Display: "No dream found matching '[Title]'. Did you mean one of these?" (list similar titles)
- Allow user to retry with corrected title

**No Relevant Dreams (Pattern Mode)**:
- Display: "No relevant dreams found for your query. Try rephrasing or asking about a specific dream using quotes."
- Continue with general context (project knowledge only)

**Embedding Generation Failure**:
- Log error
- Fall back to keyword-based search (existing behavior)
- Notify user: "Using keyword search (semantic search unavailable)"

