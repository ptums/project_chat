# Implementation Plan: Seamless Environment Setup

**Branch**: `003-seamless-setup` | **Date**: 2025-01-27 | **Spec**: [/specs/003-seamless-setup/spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-seamless-setup/spec.md`

## Summary

Create unified setup procedures for development and production environments that automate database creation, migration application, and seed data loading. Provide clear separation between dev and prod configurations with validation. Include shared project_knowledge seed data (FF, DAAS, THN, 700B) that is public and consistent across environments. Provide database initialization script that reads database configuration from .env/.env.local files to support flexible database naming. Reorganize feature specifications into sequential numbering (001-dev-environment, 002-large-text-input, 003-ollama-organizer, 004-usage-tracking, 005-daas-semantic-retrieval) for better developer onboarding. Work includes setup scripts, seed data files, migration orchestration, environment validation, database initialization, and documentation consolidation.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: psycopg2, python-dotenv (existing), PostgreSQL, bash (for migration scripts)  
**Storage**: PostgreSQL (existing database), SQL migration files, JSON/CSV seed data files  
**Testing**: Manual verification (as per project standards - no automated test framework)  
**Target Platform**: macOS/Linux development machines, production PostgreSQL servers  
**Project Type**: Single repository with CLI, API server, and shared modules  
**Performance Goals**: Setup completes in under 15 minutes for new developers; migration scripts execute in <30 seconds per migration; seed data loads in <5 seconds  
**Constraints**: Must not break existing setup procedures; must handle existing databases gracefully; must validate environment before destructive operations; seed data must be idempotent (UPSERT semantics); database initialization must read from .env/.env.local files  
**Scale/Scope**: Single developer onboarding workflow; production deployment workflow; 3-5 migration scripts; 3 seed data files (dev conversations, prod conversations, shared project_knowledge); 1 database initialization script; 5 feature specs to reorganize

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Phase 0**: Constitution file currently contains placeholders with no enforced principles, so no blocking gates. Continue to document reasoning and keep changes incremental to stay aligned with implied simplicity/observability expectations.

**Post-Phase 1**:

- ✅ Extends existing infrastructure (migration scripts, database setup) rather than creating new systems
- ✅ Maintains simplicity: single-command setup, clear error messages, idempotent operations
- ✅ Uses existing technologies (Python, PostgreSQL, bash) with no new dependencies
- ✅ No breaking changes to existing database schema or application code
- ✅ Incremental enhancement to existing setup procedures

## Project Structure

### Documentation (this feature)

```text
specs/003-seamless-setup/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── setup-dev.md     # Development setup script contract
│   └── setup-prod.md    # Production setup script contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
setup_dev.py                 # NEW: Unified development setup script
setup_prod.py                # NEW: Unified production setup script
init_db.py                   # NEW: Database initialization script (reads from .env/.env.local)
db/
├── migrations/              # EXISTING: Migration scripts (000, 001, 002)
│   ├── 000_initial_schema.sql
│   ├── 001_create_conversation_index.sql
│   ├── 002_daas_embeddings.sql
│   └── run_all_migrations.sh
├── seeds/                   # NEW: Seed data directory
│   ├── dev_seed.sql         # NEW: Development seed data (3 sample conversations)
│   ├── prod_seed.sql        # NEW: Production seed data (conversations, if needed)
│   └── project_knowledge_seed.sql  # NEW: Shared project knowledge (FF, DAAS, THN, 700B)
setup_dev_db.py              # EXISTING: Legacy dev setup (may be deprecated)
import_chatgpt_from_zip.py   # EXISTING: Data import script
setup_prod_conversation_index.py  # EXISTING: Conversation indexing
backfill_embeddings.py       # EXISTING: Embedding backfill
README.md                    # MODIFIED: Update with new setup procedures
DATABASE_SETUP.md            # MODIFIED: Consolidate with new procedures
specs/                       # MODIFIED: Reorganize feature specs
├── 001-dev-environment/     # RENAMED: From existing 001-dev-environment
├── 002-large-text-input/    # RENAMED: From existing 001-large-text-input
├── 003-ollama-organizer/    # RENAMED: From existing 001-ollama-organizer
├── 004-usage-tracking/      # RENAMED: From existing 001-usage-tracking
└── 005-daas-semantic-retrieval/  # RENAMED: From existing 002-daas-semantic-retrieval
```

**Structure Decision**: Add new setup scripts at repository root for visibility. Create `db/seeds/` directory for seed data files (SQL format for direct execution) with separate files for dev conversations, prod conversations (if needed), and shared project_knowledge. Add `init_db.py` script to initialize databases based on .env/.env.local configuration. Keep existing migration scripts in `db/migrations/`. Reorganize `specs/` directory by renaming/moving feature directories to sequential numbering. Update existing documentation files rather than creating new ones.

## Complexity Tracking

Not required (no constitution violations identified).
