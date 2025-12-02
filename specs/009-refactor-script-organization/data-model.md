# Data Model: Refactor Script Organization

## Overview

This refactoring does not introduce any new data models or modify existing database schemas. It is purely an organizational change to file structure and path references.

## No Data Model Changes

- No new database tables
- No schema modifications
- No new entities or relationships
- File system organization only

## Path Reference Updates

The only "data" aspect is updating path references in code:

- `METADATA_DIR` in `thn_code_indexer.py`: Changed from `repos/.metadata` to `../repos/.metadata`
- Default `target_dir` in `clone_repository()`: Changed from `"repos"` to `"../repos"`

These are string constants, not data model entities.

