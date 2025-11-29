# CLI Contracts: Ollama Conversation Organizer

## /save [SESSION_ID]
- **Purpose**: Run Ollama organizer for the active session (default) or explicit `SESSION_ID`.
- **Request Flow**:
  1. Resolve session_id (active conversation or user override).
  2. Invoke `index_session(session_id, model=CONFIG_OLLAMA_MODEL)`.
- **Success Output** (stdout):
  ```
  Indexed session {session_id}
  Title: {title}
  Project: {project}
  ```
- **Failure Output** (stderr):
  - Validation errors: `Cannot index session: {reason}`
  - Ollama error: `Ollama indexing failed: {exception}`
- **Side Effects**: Upserts `conversation_index` row (version constant) and updates `indexed_at`.

## /memory list
- **Purpose**: Inspect available conversation index entries for current project.
- **Output**: Tabular rows `session_id | title | indexed_at | version`.

## /memory view <SESSION_ID>
- **Purpose**: Show stored structured fields.
- **Output**: Pretty-printed JSON or labeled lines for summary/tags/entities/memory.

## /memory refresh <SESSION_ID>
- **Purpose**: Force re-run of organizer with current prompt/version.
- **Behavior**: Calls `index_session` regardless of existing version.

## /memory delete <SESSION_ID>
- **Purpose**: Remove stale/incorrect memory entries.
- **Behavior**: Deletes row from `conversation_index`; chat context builder will skip.
