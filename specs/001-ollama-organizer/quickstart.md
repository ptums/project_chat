# Quickstart: Ollama Conversation Organizer

1. **Configure Environment**

   - Add `OLLAMA_BASE_URL=http://localhost:11434` (or remote host) to `.env.local` / `.env`.
   - Ensure PostgreSQL dev DB has `chat_sessions`, `messages`, and run the new `conversation_index` migration.

2. **Install Dependencies**

   - `pip install -r requirements.txt` (includes `requests`).
   - Verify Ollama is running and `curl $OLLAMA_BASE_URL/api/tags` responds.

3. **Index a Session Manually**

   - Run `python chat_cli.py` and converse.
   - Type `/save` to trigger indexing; verify confirmation message.
   - Check DB: `SELECT * FROM conversation_index WHERE session_id = '...'`.

4. **Reindex Historical Sessions**

   - Execute `python reindex_conversations.py`.
   - Script logs each session status and skips entries already at `CURRENT_VERSION`.

5. **Validate Context Injection**

   - Start a new conversation for the same project.
   - Confirm logs/system message show injected context from `conversation_index`.
   - Verify GPT responses reference prior conversation context appropriately.

6. **Test Memory Management Commands**

   - Run `/memory list` to see indexed entries for current project.
   - Run `/memory view <session_id>` to inspect a specific memory.
   - Run `/memory refresh <session_id>` to reindex a session.
   - Run `/memory delete <session_id>` to remove a memory entry.

7. **End-to-End Validation Checklist**

   - [ ] Ollama is running and accessible at configured URL
   - [ ] `/save` command successfully indexes a conversation
   - [ ] Indexed data appears in `conversation_index` table
   - [ ] New conversations for same project show context injection
   - [ ] `/memory list` displays indexed entries
   - [ ] `/memory view` shows detailed memory information
   - [ ] `/memory refresh` successfully reindexes a session
   - [ ] `reindex_conversations.py` processes multiple sessions
   - [ ] Context builder gracefully handles Ollama failures (fallback works)

8. **Troubleshooting**
   - If `/save` fails, inspect logs for Ollama HTTP errors (timeout, 500, invalid JSON).
   - Re-run with `OLLAMA_BASE_URL` pointing to reachable host.
   - Use `/memory list` and `/memory view` to audit stored entries.
   - Check that Ollama model is pulled: `ollama pull llama3:8b`
   - Verify database connection and `conversation_index` table exists.
