# Project Chat

A local-first, privacy-focused command-line chat interface for managing and searching project conversations—complete with project tagging, color-coded UI, and local database storage.
Designed for home-lab and productivity workflows (e.g. THN, DAAS, FF, 700B, etc.).

---

## Features

- **CLI chat interface** with project tagging and color-coded context
- **Local conversation storage** (PostgreSQL) for privacy and fast search
- **Context-aware AI assistant** (OpenAI API or local LLM via Ollama)
- **Customizable labeling, emoji, and color schemes**
- **/history and project switching** on-the-fly
- **Streaming responses** - ChatGPT-like progressive text display
- **Automatic conversation saving** - Conversations are automatically saved:
  - When switching between projects (saves current conversation before switch)
  - When exiting the program (saves before exit)
- **Mandatory conversation titles** - All conversations require a title for better organization
- **Project-aware conversation separation** - Switching projects creates a new conversation to keep topics separate
- **DAAS Semantic Dream Retrieval** - Advanced dream analysis with:
  - Single-dream queries by quoted title (e.g., `"My Flying Dream"`)
  - Pattern-based semantic search across dreams using vector embeddings
  - Automatic embedding generation for dream entries
- **Conversation indexing** - Automatic organization and summarization of conversations
- **Conversation audit tool** - CLI tool for managing and cleaning up conversation history (edit titles/projects, delete conversations)
- **Shell alias support** for quick startup

---

## Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourname/project_chat.git
   cd project_chat
   ```

2. **Install dependencies**

   Assuming Python 3.10+ is used:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install PostgreSQL pgvector extension** (required for DAAS semantic search)

   The DAAS project uses vector embeddings for semantic dream retrieval. You need to install the pgvector extension:

   **macOS (Homebrew)**:

   ```bash
   brew install pgvector
   # Then build and install for your PostgreSQL version:
   cd /tmp
   git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
   cd pgvector
   export PG_CONFIG=/opt/homebrew/opt/postgresql@15/bin/pg_config  # Adjust version as needed
   make
   sudo make install
   ```

   **Ubuntu/Debian**:

   ```bash
   sudo apt-get install postgresql-XX-pgvector  # Replace XX with your PostgreSQL version
   ```

   **From Source** (see [pgvector installation guide](https://github.com/pgvector/pgvector#installation)):

   ```bash
   git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   sudo make install
   ```

   After installation, create the extension in your database:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

4. **Run the CLI**

   ```bash
   python3 chat_cli.py
   ```

   Or, if you have an alias set up:

   ```bash
   project_chat
   ```

5. **Configure your database and environment**

   - Copy `.env.example` to `.env` or `.env.local` and fill in your values
   - Set up PostgreSQL database (see `setup_dev.py` for development)
   - Ensure `OPENAI_API_KEY` is set for embedding generation (DAAS feature)
   - See `config.py` for all available settings

6. **Run database migrations** (for DAAS semantic retrieval feature)
   - Install pgvector extension (see step 3 above)
   - Create the extension in your database:
     ```sql
     psql -d your_database -c "CREATE EXTENSION IF NOT EXISTS vector;"
     ```
   - Run migration SQL: `psql -d your_database -f db/migrations/002_daas_embeddings.sql`
   - Generate embeddings for existing DAAS entries:
     ```bash
     python3 backfill_embeddings.py
     ```

---

## Usage

### Database Backups

Backup your development or production database:

```bash
# Backup development database
python3 backup_db.py --env dev

# Backup production database
python3 backup_db.py --env prod

# Verify a backup file
python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump

# List all backups
python3 backup_db.py --list
```

See [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) or [specs/001-database-backup/quickstart.md](specs/001-database-backup/quickstart.md) for detailed backup documentation.

### Basic Commands

- Switch project context with `/project [THN|DAAS|FF|700B]` or `/thn`, `/daas`, `/ff`, `/700b`, `/general`
  - **Auto-save on switch**: Current conversation is automatically saved before switching
  - **New conversation**: You'll be prompted for a new title, and a new conversation is created for the new project
- View project history: `/history [project]`
- Index a conversation: `/save` (manually organizes and summarizes the conversation)
- View indexed memories: `/memory list` or `/memory view <session_id>`
- Search conversations: `/search <query>`
- Exit: `/exit` (automatically saves current conversation before exiting)

### Conversation Audit Tool

The conversation audit tool (`audit_conversations.py`) helps you manage and clean up your conversation history. Use it to review conversations, fix misclassified projects, update titles, and delete conversations.

**Running the audit tool:**

```bash
python3 audit_conversations.py
```

**Main Menu Options:**

1. **List conversations by project** - View all conversations for a specific project (THN, DAAS, FF, 700B, or general)
2. **View conversation by ID** - Display details for a specific conversation when you know its UUID
3. **Search conversation by title** - Find conversations by searching for their title (exact or partial match)
4. **Exit** - Return to command line

**Message Review Mode:**

After viewing a conversation list or details, you can enter message review mode by typing `/messages <conversation_id>` (or `/message <id>`). In message review mode, you can:

- **`/edit-title`** - Update the conversation's title
- **`/edit-project`** - Change the conversation's project tag (updates both `conversations` and `conversation_index` tables)
- **`/delete`** - Delete the conversation entirely (with confirmation prompt)
- **`/back`** - Return to the previous view (main menu or conversation list)

**Example Workflow:**

```bash
$ python3 audit_conversations.py

Conversation Audit Tool
==================================================
1. List conversations by project
2. View conversation by ID
3. Search conversation by title
4. Exit

Select an option (1-4): 1

Enter project name (THN/DAAS/FF/700B/general): DAAS

Conversations for project: DAAS
============================================================
ID: abc-123-def-456
Title: Flying Dream Analysis
Project: DAAS
Messages: 12

Enter /messages <id> to review, or press Enter to return to main menu
/messages abc-123-def-456

Message History for: Flying Dream Analysis (DAAS)
============================================================

[1] [USER] I had a dream about flying...
[2] [ASSISTANT] Flying dreams often represent...

Commands: /edit-title, /edit-project, /delete, /back
Enter command: /edit-project

Enter new project (THN/DAAS/FF/700B/general): general
Project updated successfully.

Returning to main menu...
```

**Use Cases:**

- **Clean up misclassified conversations**: Find conversations tagged with the wrong project and fix them
- **Update unclear titles**: Review message history and update titles to better reflect conversation content
- **Delete jumbled conversations**: Remove conversations that contain mixed topics and aren't worth fixing
- **Organize conversation history**: Ensure all conversations are properly categorized by project

### Conversation Management

**Starting a New Conversation:**
- When you start the program, you **must** provide a conversation title (cannot skip)
- Select a project tag (default: `general`)

**Switching Projects Mid-Conversation:**
1. Type a project switch command (e.g., `/thn`, `/daas`, `/general`)
2. The current conversation is automatically saved
3. You'll be prompted for a new title for the conversation under the new project
4. A new conversation is created, and you continue with the new project context
5. This keeps conversations properly separated by project

**Exiting:**
- Type `/exit` or press Ctrl+C
- Current conversation is automatically saved before exit
- Usage summary is displayed

### DAAS Dream Analysis

The DAAS project includes advanced semantic dream retrieval:

**Single Dream Analysis** - Reference a specific dream by title:

```
You (DAAS) 🟣: What does "My Flying Dream" mean from a Jungian perspective?
```

**Pattern-Based Analysis** - Find themes across multiple dreams:

```
You (DAAS) 🟣: What patterns do I have with water in my dreams?
```

The system automatically:

- Detects quoted titles for single-dream queries
- Uses vector similarity search for pattern queries
- Generates embeddings for new DAAS entries
- Falls back to keyword search if embeddings unavailable

---

## Example

```bash
$ python3 chat_cli.py
Conversation title (required): Web App Deployment
Project tag [general/THN/DAAS/FF/700B] (default: general): THN

Started conversation abc-123 [project=THN] 🟢

You (THN) 🟢: How do I deploy my web app locally?
🟢 Thinking for THN...
AI (THN) 🟢: [Streaming response appears progressively...]

You (THN) 🟢: /general
✓ Indexed: Web App Deployment [THN]
Conversation title for GENERAL (required): The Hobbit Discussion
Switched active project context to GENERAL 🔵

You (GENERAL) 🔵: What scenes in the hobbit book were not in the movie?
🔵 Thinking for GENERAL...
AI (GENERAL) 🔵: [Streaming response...]

You (GENERAL) 🔵: /exit
✓ Indexed: The Hobbit Discussion [general]
[Usage summary]
Bye.
```

### Streaming Responses

Responses appear progressively, word-by-word, mimicking ChatGPT's experience. The text cascades down the screen as it's generated, providing immediate feedback.

---

## Integrations

- **Web API/PWA**: Tiny Flask/FastAPI endpoint can be enabled for web journal apps
- **Shell**: Add an alias to your `.zshrc`/`.bash_profile` for easier launch

---

## Configuration

### Environment Variables

Create a `.env` or `.env.local` file (see `.env.example` for template):

- **Database**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **OpenAI**: `OPENAI_API_KEY`, `OPENAI_MODEL` (default: `gpt-4.1`)
- **Ollama**: `OLLAMA_BASE_URL`, `OLLAMA_MODEL` (for conversation indexing)
- **DAAS**: `DAAS_VECTOR_TOP_K` (default: `5`) - Number of dreams to retrieve for pattern queries

### Customization

- Edit `brain_core/config.py` to change default project tags and UI colors/emojis
- Adjust streaming speed by modifying the `min_delay` in `chat_cli.py` (default: 30ms per character)
- Customize project styles in `chat_cli.py` `PROJECT_STYLE` dictionary

---

## License

MIT or similar (edit as appropriate).

---

## Credits

Inspired by productivity workflows, home-lab privacy, and local knowledge management.

---

**Feel free to edit and expand—let me know if you want this tuned for a specific stack or workflow!**
