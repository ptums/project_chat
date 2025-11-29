# API Contracts: DAAS Semantic Dream Retrieval

## Modified Endpoints

### POST /api/chat

**Existing Behavior**: Accepts conversation_id, message, project; returns complete response

**New Behavior**: Supports streaming responses via Server-Sent Events (SSE) or streaming JSON

#### Request (unchanged)
```json
{
  "conversation_id": "uuid",
  "message": "What does 'My Flying Dream' mean?",
  "project": "DAAS"
}
```

#### Response Options

**Option 1: Streaming JSON (default for backward compatibility)**
- Returns complete response as before
- No breaking changes

**Option 2: Server-Sent Events (new, opt-in)**
- Request header: `Accept: text/event-stream`
- Response: SSE stream with chunks
- Format: `data: {"chunk": "text chunk here"}\n\n`

#### DAAS-Specific Retrieval

**Automatic**: When `project = "DAAS"`, system automatically:
1. Detects quoted title in message
2. Routes to single-dream or pattern-based retrieval
3. Uses vector similarity search for pattern queries
4. Returns response with appropriate context

**No API Changes Required**: Retrieval logic is internal, transparent to API consumers

## New Endpoints (Optional - Future)

### POST /api/embeddings/generate

**Purpose**: Generate embedding for text (admin/debug endpoint)

**Request**:
```json
{
  "text": "text to embed"
}
```

**Response**:
```json
{
  "embedding": [0.123, -0.456, ...],
  "dimension": 1536
}
```

**Status**: Not required for initial implementation, can be added later if needed

## Error Responses

### 400 Bad Request
- Missing required fields
- Invalid conversation_id format
- Invalid project value

### 404 Not Found
- Conversation not found (for single-dream mode with quoted title)
- No relevant dreams found (for pattern mode) - returns 200 with empty context message

### 500 Internal Server Error
- Embedding generation failure
- Vector search failure
- Streaming interruption

## Streaming Response Format

### SSE Format
```
event: message
data: {"chunk": "This is a chunk of text"}

event: message
data: {"chunk": " continuing the response"}

event: done
data: {"complete": true}
```

### JSON Streaming Format (alternative)
```json
{"type": "chunk", "content": "This is a chunk"}
{"type": "chunk", "content": " continuing"}
{"type": "complete", "content": ""}
```

