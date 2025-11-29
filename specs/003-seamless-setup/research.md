# Research: Seamless Environment Setup

**Feature**: 003-seamless-setup  
**Date**: 2025-01-27  
**Phase**: 0 - Outline & Research

## Research Questions

### 1. Setup Script Architecture

**Question**: How should setup scripts be structured to support both development and production environments while maintaining clear separation?

**Decision**: Create two separate scripts (`setup_dev.py` and `setup_prod.py`) that share common utilities but have distinct entry points and validation logic. Use environment variable validation to prevent accidental cross-environment operations.

**Rationale**: 
- Clear separation reduces risk of running production migrations on dev database (or vice versa)
- Separate scripts make it obvious which procedure to use
- Shared utilities reduce code duplication
- Environment validation provides safety checks

**Alternatives Considered**:
- Single script with `--env dev|prod` flag: Rejected because flags can be mistyped and are less explicit
- Configuration file approach: Rejected as overkill for this use case; environment variables are sufficient

### 2. Migration Execution Strategy

**Question**: How should migrations be applied to ensure correct order and handle partial migrations?

**Decision**: Use the existing `run_all_migrations.sh` script as the foundation, but enhance it with:
- Migration state tracking (check which migrations have been applied)
- Dependency validation (ensure migrations run in order: 000 → 001 → 002)
- Rollback capability detection (warn if rollback scripts exist but don't auto-rollback)
- Error handling with clear messages

**Rationale**:
- Existing script already handles migration order correctly
- State tracking prevents re-running migrations unnecessarily
- Dependency validation catches out-of-order execution
- Clear error messages help developers troubleshoot

**Alternatives Considered**:
- Python-based migration runner: Rejected because SQL migrations are simpler and more transparent
- Migration version table: Rejected as overkill; checking table existence is sufficient for this project's scale

### 3. Seed Data Format and Loading

**Question**: What format should seed data use, and how should it be loaded to handle existing data gracefully?

**Decision**: Use SQL files with `INSERT ... ON CONFLICT DO UPDATE` (UPSERT) semantics for idempotent loading. Store seed data in `db/seeds/` directory:
- `dev_seed.sql`: Development seed data (3 sample conversations across different projects)
- `prod_seed.sql`: Production seed data (conversations, if needed)
- `project_knowledge_seed.sql`: Shared project knowledge entries for all active projects (THN, DAAS, FF, 700B) - same file used for both dev and prod

**Rationale**:
- SQL format is direct and doesn't require additional parsing
- UPSERT semantics allow safe re-running of setup scripts
- Separate files for dev/prod conversations maintain clear separation
- Shared project_knowledge file ensures consistency across environments and is public-safe
- SQL can be reviewed and edited easily

**Alternatives Considered**:
- JSON/CSV with Python loader: Rejected because SQL is more direct and doesn't require additional dependencies
- YAML format: Rejected as unnecessary complexity; SQL is sufficient
- Separate project_knowledge files for dev/prod: Rejected because project knowledge is public and should be consistent

### 4. Environment Validation

**Question**: How should the setup scripts validate that they're being run in the correct environment?

**Decision**: Validate environment variables before any database operations:
- Development setup: Check `ENV_MODE=development` or `DEV_DB_NAME` is set
- Production setup: Check `ENV_MODE=production` and warn if running on localhost
- Database name validation: Ensure dev setup uses dev database name pattern
- Connection validation: Test database connectivity before proceeding

**Rationale**:
- Early validation prevents accidental data loss
- Clear error messages guide users to fix configuration
- Database name patterns provide additional safety check
- Connection validation catches issues before migration execution

**Alternatives Considered**:
- Interactive confirmation prompts: Rejected as too disruptive; validation errors are sufficient
- Configuration file validation: Rejected because environment variables are the existing pattern

### 5. Seed Data Content Strategy

**Question**: What should development seed data contain, and how should it be structured?

**Decision**: Development seed data should include:
- Minimum 3 sample conversations covering different projects (THN, DAAS, FF, 700B, or general)
- Each conversation should have 2-3 messages (user + assistant) to be realistic
- Use UUIDs that are clearly test data (e.g., `00000000-0000-0000-0000-000000000001`)
- Include project tags to demonstrate project switching

Shared project knowledge seed data (`project_knowledge_seed.sql`) should include:
- Project knowledge entries for all active projects (THN, DAAS, FF, 700B)
- Each entry should have a meaningful `key` and `summary`
- Content is public-safe and will be audited by project maintainer
- Same file used for both dev and prod environments
- Use UPSERT to allow updates without conflicts

**Rationale**:
- 3 conversations is sufficient for testing without being overwhelming
- Multiple projects demonstrate the project switching feature
- Clear test UUIDs make it obvious these are seed data
- Shared project knowledge ensures consistency and reduces maintenance
- Public-safe content allows version control without security concerns

**Alternatives Considered**:
- More seed conversations: Rejected as unnecessary; 3 is sufficient for development
- Auto-generated seed data: Rejected because manually curated data is more realistic
- Separate project knowledge for dev/prod: Rejected because knowledge should be consistent and is public-safe

### 6. Feature Specification Reorganization

**Question**: How should feature specifications be reorganized to sequential numbering?

**Decision**: Rename/move feature directories to sequential order:
- `001-dev-environment` → Keep as-is (already correct)
- `001-large-text-input` → `002-large-text-input`
- `001-ollama-organizer` → `003-ollama-organizer`
- `001-usage-tracking` → `004-usage-tracking`
- `002-daas-semantic-retrieval` → `005-daas-semantic-retrieval`

Update all internal references (specs, plans, tasks) to reflect new numbering. This is a one-time migration task.

**Rationale**:
- Sequential numbering makes dependency relationships clear
- New developers can follow features in order
- Clear progression from basic (dev environment) to advanced (DAAS semantics)

**Alternatives Considered**:
- Keep existing numbering: Rejected because it's confusing (multiple 001s, no 002)
- Semantic naming only: Rejected because numbers provide clear ordering

### 7. Documentation Consolidation

**Question**: How should setup documentation be organized to avoid duplication?

**Decision**: Consolidate setup instructions in `README.md` with a clear "Quick Start" section that points to detailed guides. Update `DATABASE_SETUP.md` to reference the new setup scripts. Keep migration-specific details in `db/migrations/README.md`.

**Rationale**:
- Single source of truth in README for new developers
- Detailed guides remain for specific use cases
- Migration README stays focused on migration details

**Alternatives Considered**:
- Separate setup guide: Rejected because README is the standard entry point
- Remove DATABASE_SETUP.md: Rejected because it contains useful troubleshooting details

### 8. Database Initialization Script

**Question**: How should database initialization be handled when database names are configurable via .env/.env.local files?

**Decision**: Create a standalone `init_db.py` script that:
- Reads database configuration from `.env.local` (if exists) or `.env` files
- Supports both development (`DEV_DB_NAME`, `DEV_DB_HOST`, etc.) and production (`DB_NAME`, `DB_HOST`, etc.) configurations
- Creates the database if it doesn't exist
- Handles existing databases gracefully (informational message, no error)
- Can be run independently or called by setup scripts

**Rationale**:
- Allows flexible database naming via environment files
- Supports both dev and prod configurations
- Can be used standalone for database creation without full setup
- Reusable by both `setup_dev.py` and `setup_prod.py`

**Alternatives Considered**:
- Hardcoded database names: Rejected because user wants to configure via .env files
- Separate scripts for dev/prod initialization: Rejected because logic is similar, only config differs
- Require manual database creation: Rejected because it adds friction to setup process

## Dependencies and Prerequisites

### Existing Infrastructure
- ✅ Migration scripts exist: `000_initial_schema.sql`, `001_create_conversation_index.sql`, `002_daas_embeddings.sql`
- ✅ Migration runner exists: `run_all_migrations.sh`
- ✅ Database connection utilities exist: `brain_core/db.py`
- ✅ Environment configuration exists: `brain_core/config.py`
- ✅ Legacy setup script exists: `setup_dev_db.py` (can be deprecated)

### Required Knowledge
- PostgreSQL database administration (CREATE DATABASE, migrations)
- Python database connectivity (psycopg2)
- SQL UPSERT syntax (`INSERT ... ON CONFLICT`)
- Environment variable management (`.env`, `.env.local`)

### External Dependencies
- PostgreSQL server running and accessible
- Python 3.10+ with psycopg2 installed
- pgvector extension (for production, if DAAS features are used)

## Open Questions Resolved

All research questions have been resolved. No NEEDS CLARIFICATION markers remain.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data model documentation
- Define setup script contracts
- Create quickstart guide

