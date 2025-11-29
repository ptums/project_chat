# Data Model: Ollama Conversation Organizer

## 1. conversation_index (NEW)
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| session_id | UUID | PK, FK → chat_sessions.id, ON DELETE CASCADE | One row per session |
| project | TEXT | NOT NULL, CHECK project IN ('THN','DAAS','FF','700B','general') | Mirrors session project |
| title | TEXT | NULL allowed | Short headline returned by Ollama |
| tags | JSONB | NULL allowed | Array of strings or key/value pairs |
| summary_short | TEXT | NULL allowed | 1-2 sentence recap |
| summary_detailed | TEXT | NULL allowed | Multi-paragraph story |
| key_entities | JSONB | NULL allowed | Shape `{"people":[],"domains":[],"assets":[]}` |
| key_topics | JSONB | NULL allowed | Array of topical strings |
| memory_snippet | TEXT | NULL allowed | Ready-to-inject blurb |
| ollama_model | TEXT | NOT NULL DEFAULT 'llama3:8b' | Audit of model used |
| version | INTEGER | NOT NULL DEFAULT 1 | Prompt/schema version |
| indexed_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Last index timestamp |

## 2. organizer_job (LOGICAL)
*No physical table planned yet.* Represented as log entries/structured data in code (job_id, status, retries, durations) for observability. If persisted later, follow spec entity definition.

## 3. Derived Structures
- **Transcript blob**: In-memory list of `{role, content, created_at}` loaded from `messages` joined to `chat_sessions`.
- **Project context payload**: Dict of `{"context": string, "notes": [string]}` returned by Ollama for chat priming.

## Relationships
- `conversation_index.session_id` references `chat_sessions.id` (1:1).
- Context builder filters `conversation_index` by `project`; ranking uses in-memory term matching against `tags`, `key_topics`, `summary_detailed`.
- CLI `/save` ensures `conversation_index` row exists/updates before reusing in future chats.
