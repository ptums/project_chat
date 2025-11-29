# Implementation Plan: Database Backup Script

**Branch**: `001-database-backup` | **Date**: 2025-01-27 | **Spec**: [/specs/001-database-backup/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-database-backup/spec.md`

## Summary

Create a Python script that backs up PostgreSQL databases for both development and production environments. The script will use `pg_dump` to create complete database backups with timestamps, environment identifiers, and integrity verification. Support automatic environment detection from .env files, custom backup locations, and backup metadata generation. Ensure zero-downtime backups and proper error handling for production use.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: psycopg2-binary (existing), python-dotenv (existing), PostgreSQL client tools (pg_dump, pg_restore)  
**Storage**: PostgreSQL database backups (SQL dump format), backup metadata files (JSON), local filesystem or network storage  
**Testing**: Manual verification (as per project standards - no automated test framework)  
**Target Platform**: macOS/Linux development machines, production PostgreSQL servers  
**Project Type**: Single repository with CLI scripts and shared modules  
**Performance Goals**: Complete backup in under 5 minutes for databases up to 10GB; integrity verification completes in <30 seconds  
**Constraints**: Must not require database downtime; must handle large databases (up to 10GB); must preserve vector embeddings and binary data; must work with existing .env/.env.local configuration pattern; backup files must be restorable with standard PostgreSQL tools  
**Scale/Scope**: Single backup script; supports dev and prod environments; backup file storage management; metadata generation; integrity verification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Phase 0**: Constitution file currently contains placeholders with no enforced principles, so no blocking gates. Continue to document reasoning and keep changes incremental to stay aligned with implied simplicity/observability expectations.

**Post-Phase 1**:

- ✅ Extends existing infrastructure (database scripts, environment configuration) rather than creating new systems
- ✅ Maintains simplicity: single-command backup, clear error messages, standard PostgreSQL tools
- ✅ Uses existing technologies (Python, PostgreSQL, pg_dump) with no new dependencies
- ✅ No breaking changes to existing database schema or application code
- ✅ Incremental enhancement to existing database management scripts

## Project Structure

### Documentation (this feature)

```text
specs/001-database-backup/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── backup-script.md # CLI contract for backup script
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backup_db.py             # NEW: Database backup script (main entry point)
brain_core/
├── config.py            # EXISTING: Environment configuration (used for DB connection)
└── db.py                # EXISTING: Database connection utilities (may extend)
db/
└── backups/             # NEW: Default backup storage directory (gitignored)
    └── .gitkeep         # NEW: Ensure directory exists in repo
```

**Structure Decision**: Add `backup_db.py` script at repository root for visibility and consistency with other database management scripts (`init_db.py`, `setup_dev.py`, `import_chatgpt_from_zip.py`). Create `db/backups/` directory for default backup storage location (gitignored to prevent committing backup files). Script will use existing `brain_core/config.py` and `brain_core/db.py` for database connection configuration, following the same pattern as other database scripts in the project.

## Complexity Tracking

Not required (no constitution violations identified).
