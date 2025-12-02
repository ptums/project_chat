# Refactor Script Organization

## Overview

Reorganize project scripts and tools into proper directory structure and update path references.

## Requirements

### 1. Move Scripts to `scripts/` Directory

Move the following files from project root to `scripts/` directory:
- `backfill_embeddings.py`
- `backup_db.py`
- `fix_invalid_projects.py`
- `import_chatgpt_from_zip.py`
- `reindex_conversations.py`
- `setup_dev.py`
- `setup_prod_conversation_index.py`

### 2. Create `tools/` Directory

Create a new `tools/` directory and move:
- `audit_conversations.py`

### 3. Update Repos Directory References

The `repos/` directory has been moved from `project_chat/repos/` to `../repos/` (one level up from project root, same level as `project_chat/`).

Update all code references to use the new path:
- `scripts/index_thn_code.py` - update help text and any path references
- `brain_core/thn_code_indexer.py` - update `METADATA_DIR` and `clone_repository` default `target_dir`

## Technical Details

- All file moves are straightforward relocations
- Path updates need to change from relative `repos/` to `../repos/`
- Need to ensure all imports and path references still work after moves

