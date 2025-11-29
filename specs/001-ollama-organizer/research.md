# Research Notes: Ollama Conversation Organizer

## 1. Conversation Index Schema
- **Decision**: Create `conversation_index` table with one row per `chat_sessions.id`, storing structured metadata (title, summaries, tags, entities, topics, memory snippet, model, version, timestamps).
- **Rationale**: Aligns with spec requirement for a "conversation index" while staying backward-compatible (FK to existing sessions, optional JSON/text columns). Single-row-per-session simplifies upsert logic and `/save` idempotency.
- **Alternatives Considered**:
  - Separate table per attribute (e.g., tags table, entities table). Rejected due to unnecessary complexity for single-user workflow.
  - Embedding structured data into `chat_sessions.meta`. Rejected because migration risk is higher and querying context by project would be slower.

## 2. Ollama Integration Strategy
- **Decision**: Wrap Ollama HTTP endpoint via lightweight helper (`generate_with_ollama`) using `requests`, configurable `OLLAMA_BASE_URL`, and JSON contract `{model, prompt, stream:false}`.
- **Rationale**: Keeps dependencies minimal, mirrors Ollama REST API, and centralizes error handling + configuration for CLI, batch script, and context builder.
- **Alternatives Considered**:
  - Calling Ollama via subprocess `ollama run`. Rejected because we need structured error handling and remote host flexibility.
  - Adding a third-party Ollama SDK. Rejected due to extra dependency and limited control.

## 3. Transcript Preparation & Prompting
- **Decision**: Build transcripts as deterministic text blocks (`role: content`) ordered chronologically, then feed into a fixed prompt instructing Ollama to emit strict JSON with required keys.
- **Rationale**: Simplicity, predictable token usage, easy debugging/logging. Chronological listing keeps context intact and matches user mental model when auditing.
- **Alternatives Considered**:
  - Sending raw JSON arrays of messages. Rejected because prompt complexity grows and plaintext is more legible for manual inspection.
  - Limiting to last N messages only. Deferred; we can add truncation logic later if token limits force it.

## 4. Reindex Strategy & Versioning
- **Decision**: Track a `version` integer per index row; batch script (`reindex_conversations.py`) reprocesses sessions missing an index or with older versions.
- **Rationale**: Enables schema/prompt evolution without destructive changes and supports manual reindex runs on dev/prod machines.
- **Alternatives Considered**:
  - Timestamp-only refresh detection. Rejected because it can't differentiate prompt/model upgrades.
  - Auto-reindex on startup. Rejected to avoid startup delays; manual script keeps control with the user.

## 5. Project Context Builder
- **Decision**: Query up to 200 indexed memories per project, apply simple term matching against `tags`, `key_topics`, and `summary_detailed`, select top 3-5, and ask Ollama to condense them into JSON `{context, notes}` for GPT system messages.
- **Rationale**: Lightweight relevance scoring avoids needing embeddings/search infra while satisfying spec for sharper recall. Returning JSON ensures predictable integration with chat engine.
- **Alternatives Considered**:
  - Implementing vector search with pgvector. Deferred to keep scope manageable.
  - Injecting raw memories without reprocessing via Ollama. Rejected because user explicitly wants "organized" context and cross-project connections.
