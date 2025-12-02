# File Move Contract

## Overview

This contract defines the file moves required for script organization refactoring.

## Files to Move to `scripts/` Directory

1. `backfill_embeddings.py` → `scripts/backfill_embeddings.py`
2. `backup_db.py` → `scripts/backup_db.py`
3. `fix_invalid_projects.py` → `scripts/fix_invalid_projects.py`
4. `import_chatgpt_from_zip.py` → `scripts/import_chatgpt_from_zip.py`
5. `reindex_conversations.py` → `scripts/reindex_conversations.py`
6. `setup_dev.py` → `scripts/setup_dev.py`
7. `setup_prod_conversation_index.py` → `scripts/setup_prod_conversation_index.py`

## Files to Move to `tools/` Directory

1. `audit_conversations.py` → `tools/audit_conversations.py`

## Path Reference Updates

### `scripts/index_thn_code.py`

- Update help text on line 44: Change `repos/` to `../repos/` in documentation

### `brain_core/thn_code_indexer.py`

- Line 33: `METADATA_DIR = Path("repos/.metadata")` → `METADATA_DIR = Path("../repos/.metadata")`
- Line 36: `target_dir: str = "repos"` → `target_dir: str = "../repos"`

## Verification

After moves:
- All files exist in new locations
- Path references updated correctly
- Scripts execute without errors
- No broken imports

