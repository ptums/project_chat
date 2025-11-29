# Research: DAAS Semantic Dream Retrieval and Streaming Responses

## Embedding Model/Service Selection

### Decision: Use OpenAI's `text-embedding-3-small` model via OpenAI SDK

**Rationale**:
- Project already uses OpenAI SDK for chat completions, maintaining consistency
- `text-embedding-3-small` provides good quality embeddings at low cost ($0.02 per 1M tokens)
- 1536-dimensional vectors are manageable for PostgreSQL storage
- No additional service dependencies required
- Well-documented and reliable API

**Alternatives Considered**:
- **Ollama embeddings**: Already in use for conversation indexing, but requires local model management and may be slower for batch operations
- **Sentence Transformers (local)**: Would require additional dependencies and model storage, but offers offline capability
- **Other cloud services (Cohere, HuggingFace)**: Adds new dependencies and API keys

**Implementation Notes**:
- Use OpenAI's `embeddings.create()` API endpoint
- Cache embeddings to avoid regenerating for same content
- Handle rate limits gracefully (OpenAI has generous limits for embeddings)

## Vector Storage in PostgreSQL

### Decision: Use PostgreSQL's `vector` extension (pgvector) for native vector similarity search

**Rationale**:
- Native PostgreSQL extension provides efficient vector operations
- Supports cosine similarity, L2 distance, and inner product
- Indexing support (IVFFlat, HNSW) for fast similarity search
- No external vector database required (keeps architecture simple)
- Works seamlessly with existing PostgreSQL infrastructure

**Alternatives Considered**:
- **Store as JSONB array**: Would require application-level similarity calculation (slow for large datasets)
- **External vector DB (Pinecone, Weaviate)**: Adds complexity, network latency, and additional service dependency
- **Embeddings in separate table**: More normalized but requires joins; pgvector allows embedding column in conversation_index

**Implementation Notes**:
- Install `pgvector` extension: `CREATE EXTENSION vector;`
- Add `embedding vector(1536)` column to `conversation_index` table (nullable, DAAS-only)
- Create index: `CREATE INDEX idx_conversation_index_embedding ON conversation_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`
- Use cosine similarity: `ORDER BY embedding <=> query_embedding LIMIT k`

## Backfill Performance

### Decision: Process embeddings in batches of 50 with 1-second delay between batches

**Rationale**:
- OpenAI rate limits: 3000 requests/minute for embeddings API
- Batch of 50 with 1s delay = ~50 requests/second = 3000/minute (within limits)
- Allows progress tracking and graceful interruption
- Reasonable completion time: ~100 dreams = 2 batches = ~2 minutes
- Can be run as background task without blocking user

**Alternatives Considered**:
- **Single-threaded sequential**: Too slow for large backfills
- **Aggressive parallelization**: Risk of hitting rate limits
- **Overnight batch job**: Acceptable but delays feature availability

**Implementation Notes**:
- Backfill script processes DAAS entries in `conversation_index` missing embeddings
- Progress logged to console
- Resumable (can re-run safely, skips entries with existing embeddings)
- Optional dry-run mode to estimate time

## Streaming Response Implementation

### Decision: Use OpenAI streaming API with chunked output for both CLI and API

**Rationale**:
- OpenAI SDK supports streaming via `stream=True` parameter
- CLI: Print chunks as received using `sys.stdout.write()` with flush
- API: Use Flask's `Response` with `stream_with_context()` or Server-Sent Events (SSE)
- Maintains consistency with existing OpenAI integration
- No additional dependencies required

**Alternatives Considered**:
- **WebSocket**: More complex, requires additional infrastructure
- **Polling**: Poor user experience, adds latency
- **Client-side buffering**: Defeats purpose of streaming

**Implementation Notes**:
- CLI: Stream chunks to terminal with proper line handling
- API: Use Flask streaming response or SSE for web clients
- Handle interruptions gracefully (Ctrl+C, connection loss)
- Maintain response quality (streaming doesn't affect content)

## Quoted Title Detection

### Decision: Use regex pattern to detect quoted titles: `"([^"]+)"` with validation

**Rationale**:
- Simple and reliable pattern matching
- Handles common quote styles (double quotes primarily)
- Can be extended for single quotes if needed
- Fast execution (regex is efficient for this use case)
- Clear separation: quoted title = single-dream mode, no quotes = pattern mode

**Alternatives Considered**:
- **NLP-based detection**: Overkill for simple pattern matching
- **Fuzzy matching**: Unnecessary complexity
- **User command syntax**: Would require learning new syntax

**Implementation Notes**:
- Extract quoted text from user message
- Validate that extracted text is reasonable (not empty, not too long)
- Use extracted text for title matching against `conversation_index.title`
- Fallback to pattern mode if no matches found (with user notification)

## Vector Similarity Search Top-K

### Decision: Default top-k = 5, configurable via environment variable (DAAS_VECTOR_TOP_K)

**Rationale**:
- 5 dreams provides sufficient context without overwhelming the prompt
- Balances relevance (top results) with context window limits
- Configurable allows tuning based on user needs
- Matches common RAG (Retrieval-Augmented Generation) practices

**Alternatives Considered**:
- **Fixed at 3**: Too few for pattern recognition across multiple dreams
- **Fixed at 10**: May exceed context window for long dreams
- **Dynamic based on query**: Adds complexity without clear benefit

**Implementation Notes**:
- Use `LIMIT` clause in SQL query
- Return top-k most similar dreams based on cosine similarity
- Include similarity score in debug/logging (not in user-facing output)

## Integration Points

### Context Builder Integration
- Modify `context_builder.py` to use DAAS-specific retrieval when `project == 'DAAS'`
- Route to `daas_retrieval.py` functions based on quoted title detection
- Fall back to existing pattern matching for non-DAAS projects

### Chat Integration
- Modify `chat.py` to support streaming responses
- Pass streaming flag to OpenAI API calls
- Handle streaming chunks in both CLI and API contexts

### Database Schema
- Migration script to add `embedding vector(1536)` column to `conversation_index`
- Migration script to create pgvector index
- Backfill script to generate embeddings for existing DAAS entries

