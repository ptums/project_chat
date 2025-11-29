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
- **DAAS Semantic Dream Retrieval** - Advanced dream analysis with:
  - Single-dream queries by quoted title (e.g., `"My Flying Dream"`)
  - Pattern-based semantic search across dreams using vector embeddings
  - Automatic embedding generation for dream entries
- **Conversation indexing** - Automatic organization and summarization of conversations
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

- Switch project context with `/project [THN|DAAS|FF|700B]`
- View project history: `/history [project]`
- Index a conversation: `/save` (organizes and summarizes the conversation)
- View indexed memories: `/memory list` or `/memory view <session_id>`
- Search conversations: `/search <query>`

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
Welcome! Current project: 🟩 THN

You (THN) 🟩: How do I deploy my web app locally?
🟩 Thinking for THN...
AI (THN) 🟩: [Streaming response appears progressively...]

> /project DAAS
You (DAAS) 🟣: What does "My Flying Dream" mean?
🟣 Thinking for DAAS...
AI (DAAS) 🟣: [Streaming response with dream analysis...]
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
