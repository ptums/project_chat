# Quickstart: Refactor Script Organization

## Overview

This refactoring reorganizes scripts and tools into proper directories and updates path references for the moved `repos/` directory.

## Steps

### 1. Move Scripts to `scripts/` Directory

Move the following files from project root to `scripts/`:

```bash
cd /Users/petertumulty/Documents/Sites/project_chat/project_chat
git mv backfill_embeddings.py scripts/
git mv backup_db.py scripts/
git mv fix_invalid_projects.py scripts/
git mv import_chatgpt_from_zip.py scripts/
git mv reindex_conversations.py scripts/
git mv setup_dev.py scripts/
git mv setup_prod_conversation_index.py scripts/
```

### 2. Create `tools/` Directory and Move Audit Tool

```bash
mkdir -p tools
git mv audit_conversations.py tools/
```

### 3. Update Path References

#### Update `scripts/index_thn_code.py`

Change line 44 help text:
- From: `help="Index all repositories in repos/ directory"`
- To: `help="Index all repositories in ../repos/ directory"`

#### Update `brain_core/thn_code_indexer.py`

Change line 33:
- From: `METADATA_DIR = Path("repos/.metadata")`
- To: `METADATA_DIR = Path("../repos/.metadata")`

Change line 36:
- From: `target_dir: str = "repos"`
- To: `target_dir: str = "../repos"`

### 4. Verify Changes

```bash
# Verify files are in correct locations
ls scripts/ | grep -E "(backfill_embeddings|backup_db|fix_invalid|import_chatgpt|reindex|setup_dev|setup_prod)"
ls tools/ | grep audit_conversations

# Verify path references updated
grep -n "repos/" scripts/index_thn_code.py brain_core/thn_code_indexer.py

# Test that scripts still work (if applicable)
python3 scripts/backup_db.py --help
python3 tools/audit_conversations.py --help
```

## Expected Result

- All utility scripts in `scripts/` directory
- Audit tool in `tools/` directory
- Path references updated to `../repos/`
- All functionality preserved

