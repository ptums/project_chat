# Tasks: Seamless Environment Setup

**Input**: Design documents from `/specs/003-seamless-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Project Initialization)

**Purpose**: Create directory structure and seed data files for the setup system.

- [x] T001 Create `db/seeds/` directory at repository root
- [x] T002 Create `db/seeds/dev_seed.sql` file with placeholder comment structure for development seed data
- [x] T003 Create `db/seeds/prod_seed.sql` file with placeholder comment structure for production seed data
- [x] T004 Create `db/seeds/project_knowledge_seed.sql` file with placeholder comment structure for shared project knowledge seed data

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks needed by all user stories - database initialization script and shared utilities.

- [x] T005 Implement `init_db.py` script at repository root with environment detection logic (reads from `.env.local` or `.env`)
- [x] T006 Implement database configuration loading in `init_db.py` that supports both `DEV_DB_*` (development) and `DB_*` (production) variables
- [x] T007 Implement database connection testing in `init_db.py` that connects to PostgreSQL server before attempting database creation
- [x] T008 Implement database existence check in `init_db.py` that queries `pg_database` to determine if database already exists
- [x] T009 Implement database creation logic in `init_db.py` that creates database if it doesn't exist, handles existing databases gracefully
- [x] T010 Implement `--force` flag handling in `init_db.py` that drops and recreates database with user confirmation
- [x] T011 Implement `--env dev|prod` flag handling in `init_db.py` that explicitly sets environment when provided
- [x] T012 Implement verbose output mode in `init_db.py` that shows detailed progress for each step
- [x] T013 Implement error handling in `init_db.py` with clear messages for missing configuration, connection failures, permission errors
- [x] T014 Add command-line argument parsing to `init_db.py` using `argparse` for `--env`, `--force`, `--verbose` flags

---

## Phase 3: User Story 1 - New Developer Onboarding (Priority: P1) 🎯 MVP

**Goal**: New developers can clone the repo and get the application running locally with a single command.
**Independent Test**: A developer with no prior knowledge can clone the repo, run `python3 setup_dev.py`, and successfully start the application within 15 minutes without asking for help.

- [x] T015 [US1] Create `setup_dev.py` script at repository root with command-line argument parsing for `--skip-seed`, `--force-recreate`, `--verbose` flags
- [x] T016 [US1] Implement environment validation in `setup_dev.py` that checks `ENV_MODE=development` or `dev` and errors with clear message if not set
- [x] T017 [US1] Implement database initialization call in `setup_dev.py` that invokes `init_db.py` with appropriate flags (or imports and calls directly)
- [x] T018 [US1] Implement migration application logic in `setup_dev.py` that calls `db/migrations/run_all_migrations.sh` or equivalent Python logic
- [x] T019 [US1] Implement migration state checking in `setup_dev.py` that verifies which migrations have been applied (checks table existence: conversations, conversation_index, embedding column)
- [x] T020 [US1] Implement seed data loading in `setup_dev.py` that executes `db/seeds/dev_seed.sql` using `psql` or `psycopg2`
- [x] T021 [US1] Implement shared project knowledge loading in `setup_dev.py` that executes `db/seeds/project_knowledge_seed.sql` using `psql` or `psycopg2`
- [x] T022 [US1] Implement `--skip-seed` flag handling in `setup_dev.py` that skips both dev_seed.sql and project_knowledge_seed.sql execution
- [x] T023 [US1] Implement `--force-recreate` flag handling in `setup_dev.py` that passes `--force` to `init_db.py` with user confirmation
- [x] T024 [US1] Implement verification logic in `setup_dev.py` that checks tables exist and seed data is present (conversation count, project knowledge entries)
- [x] T025 [US1] Implement success output formatting in `setup_dev.py` that displays clear summary of completed steps
- [x] T026 [US1] Implement error handling in `setup_dev.py` with actionable error messages for each failure scenario (environment, database, migration, seed data)
- [x] T027 [US1] Create `db/seeds/dev_seed.sql` with 3 sample conversations covering different projects (THN, DAAS, FF, 700B, or general) using test UUIDs (00000000-0000-0000-0000-000000000001, etc.)
- [x] T028 [US1] Ensure `db/seeds/dev_seed.sql` uses UPSERT semantics (`ON CONFLICT DO UPDATE`) for idempotent loading
- [x] T029 [US1] Ensure `db/seeds/dev_seed.sql` includes 2-3 messages per conversation (user + assistant) for realistic sample data

---

## Phase 4: User Story 2 - Production Environment Deployment (Priority: P1)

**Goal**: System administrators can deploy the application to production with a single command that applies migrations and loads seed data.
**Independent Test**: A system administrator can deploy to a new production server by running `python3 setup_prod.py`, and the application is fully functional with all features available.

- [ ] T030 [US2] Create `setup_prod.py` script at repository root with command-line argument parsing for `--skip-seed`, `--verify-only`, `--verbose` flags
- [ ] T031 [US2] Implement environment validation in `setup_prod.py` that checks `ENV_MODE=production` or `prod` and errors with clear message if not set
- [ ] T032 [US2] Implement localhost warning in `setup_prod.py` that warns if connecting to `localhost` or `127.0.0.1` (may indicate misconfiguration)
- [ ] T033 [US2] Implement database initialization call in `setup_prod.py` that invokes `init_db.py` with `--env prod` flag
- [ ] T034 [US2] Implement database verification in `setup_prod.py` that checks database exists and is accessible before proceeding
- [ ] T035 [US2] Implement `--verify-only` flag handling in `setup_prod.py` that displays migration and seed data status without making changes
- [ ] T036 [US2] Implement migration application logic in `setup_prod.py` that calls `db/migrations/run_all_migrations.sh` or equivalent Python logic
- [ ] T037 [US2] Implement migration state checking in `setup_prod.py` that verifies which migrations have been applied and skips already-applied migrations
- [ ] T038 [US2] Implement existing data detection in `setup_prod.py` that warns if database contains existing data before applying migrations
- [ ] T039 [US2] Implement shared project knowledge loading in `setup_prod.py` that executes `db/seeds/project_knowledge_seed.sql` using `psql` or `psycopg2`
- [ ] T040 [US2] Implement production seed data loading in `setup_prod.py` that executes `db/seeds/prod_seed.sql` if it exists and contains data
- [ ] T041 [US2] Implement `--skip-seed` flag handling in `setup_prod.py` that skips both project_knowledge_seed.sql and prod_seed.sql execution
- [ ] T042 [US2] Implement verification logic in `setup_prod.py` that checks tables exist and project knowledge is loaded for all active projects (THN, DAAS, FF, 700B)
- [ ] T043 [US2] Implement success output formatting in `setup_prod.py` that displays clear summary of completed steps and next actions
- [ ] T044 [US2] Implement error handling in `setup_prod.py` with actionable error messages for each failure scenario (environment, database, migration, seed data)
- [ ] T045 [US2] Create `db/seeds/prod_seed.sql` file (can be empty or contain minimal placeholder comments for future production-specific data)

---

## Phase 5: User Story 3 - Environment Configuration Clarity (Priority: P2)

**Goal**: Developers and administrators can clearly identify which setup procedure to use, and procedures validate environment configuration.
**Independent Test**: A developer can clearly identify which setup procedure to use for their environment, and the procedure validates that they're using the correct environment configuration.

- [ ] T046 [US3] Enhance environment validation error messages in `setup_dev.py` to clearly direct users to development setup when wrong environment detected
- [ ] T047 [US3] Enhance environment validation error messages in `setup_prod.py` to clearly direct users to production setup when wrong environment detected
- [ ] T048 [US3] Add database name pattern validation in `setup_dev.py` that warns if database name doesn't match dev pattern (optional, informational)
- [ ] T049 [US3] Add database name pattern validation in `setup_prod.py` that warns if database name matches dev pattern (may indicate confusion)
- [ ] T050 [US3] Update `README.md` with clear "Quick Start" section that distinguishes between development and production setup procedures
- [ ] T051 [US3] Add environment configuration examples to `README.md` showing `.env.local` for development and `.env` for production
- [ ] T052 [US3] Update `DATABASE_SETUP.md` to reference new setup scripts (`setup_dev.py`, `setup_prod.py`, `init_db.py`) and consolidate setup instructions
- [ ] T053 [US3] Add troubleshooting section to `README.md` or `DATABASE_SETUP.md` covering common environment configuration errors and solutions

---

## Phase 6: Shared Project Knowledge Seed Data

**Purpose**: Create shared project knowledge seed file that is used by both development and production environments.

- [x] T054 [P] Create `db/seeds/project_knowledge_seed.sql` with project knowledge entries for THN project (overview, goals, or other relevant keys)
- [x] T055 [P] Add DAAS project knowledge entries to `db/seeds/project_knowledge_seed.sql` (overview, analysis_approaches, or other relevant keys)
- [x] T056 [P] Add FF project knowledge entries to `db/seeds/project_knowledge_seed.sql` (overview and other relevant keys)
- [x] T057 [P] Add 700B project knowledge entries to `db/seeds/project_knowledge_seed.sql` (overview and other relevant keys)
- [x] T058 [P] Ensure all entries in `db/seeds/project_knowledge_seed.sql` use UPSERT semantics (`ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary`)
- [x] T059 [P] Verify `db/seeds/project_knowledge_seed.sql` contains public-safe content (no sensitive information) suitable for version control

---

## Phase 7: Feature Specification Reorganization

**Purpose**: Reorganize feature specifications into sequential numbering for better developer onboarding.

- [ ] T060 [P] Rename `specs/001-large-text-input/` directory to `specs/002-large-text-input/`
- [ ] T061 [P] Rename `specs/001-ollama-organizer/` directory to `specs/003-ollama-organizer/`
- [ ] T062 [P] Rename `specs/001-usage-tracking/` directory to `specs/004-usage-tracking/`
- [ ] T063 [P] Rename `specs/002-daas-semantic-retrieval/` directory to `specs/005-daas-semantic-retrieval/`
- [ ] T064 [P] Update all internal references in renamed spec directories (plan.md, spec.md, tasks.md) to reflect new numbering
- [ ] T065 [P] Update `README.md` or main documentation to reference new sequential numbering for feature specifications
- [ ] T066 [P] Verify `specs/001-dev-environment/` directory name is correct (should remain as-is)

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T067 [P] Add comprehensive error handling for database connection failures in both `setup_dev.py` and `setup_prod.py` with troubleshooting guidance
- [ ] T068 [P] Add comprehensive error handling for migration failures in both `setup_dev.py` and `setup_prod.py` with clear error messages and next steps
- [ ] T069 [P] Add comprehensive error handling for seed data loading failures in both `setup_dev.py` and `setup_prod.py` with file path validation
- [ ] T070 [P] Add logging throughout `init_db.py`, `setup_dev.py`, and `setup_prod.py` for debugging setup issues
- [ ] T071 [P] Update `README.md` with complete setup instructions referencing new setup scripts and seed data files
- [ ] T072 [P] Update `DATABASE_SETUP.md` to consolidate all setup procedures and reference new scripts
- [ ] T073 [P] Add exit codes documentation to `setup_dev.py`, `setup_prod.py`, and `init_db.py` (0=success, 1+=error types)
- [ ] T074 [P] Run manual end-to-end test: Fresh development setup, verify database created, migrations applied, seed data loaded
- [ ] T075 [P] Run manual end-to-end test: Production setup verification, verify migrations applied, project knowledge loaded
- [ ] T076 [P] Document edge cases handling in code comments: missing .env files, partial migrations, seed data conflicts, connection failures

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **User Story phases (3–5)** → **Phase 6 (Shared Seed)** → **Phase 7 (Reorganization)** → **Phase 8 (Polish)**
- **Phase 2** must complete before User Stories 1 and 2 (database initialization script required)
- **User Story 1 (P1)** can start after Phase 2, provides MVP functionality for new developers
- **User Story 2 (P1)** can proceed in parallel with User Story 1 after Phase 2, provides production deployment
- **User Story 3 (P2)** depends on User Stories 1 and 2 completing (needs setup scripts to enhance)
- **Phase 6 (Shared Seed)** can proceed in parallel with User Stories 1 and 2, but must complete before final testing
- **Phase 7 (Reorganization)** can proceed independently, but should complete before Phase 8
- **Phase 8** depends on all previous phases completing

## Parallel Opportunities

### Within Phase 2 (Foundational)
- T005-T014 can be implemented in parallel (different functions within `init_db.py`)

### Within Phase 3 (User Story 1)
- T015-T026 (setup_dev.py implementation) can be implemented incrementally
- T027-T029 (dev_seed.sql creation) can proceed in parallel with setup_dev.py implementation

### Within Phase 4 (User Story 2)
- T030-T044 (setup_prod.py implementation) can be implemented incrementally
- T045 (prod_seed.sql creation) can proceed in parallel

### Within Phase 5 (User Story 3)
- T046-T049 (validation enhancements) can be implemented in parallel
- T050-T053 (documentation updates) can proceed in parallel

### Within Phase 6 (Shared Seed)
- T054-T057 (project knowledge entries) can be created in parallel for different projects

### Within Phase 7 (Reorganization)
- T060-T063 (directory renames) can be done in parallel
- T064-T065 (reference updates) can proceed after renames

### Within Phase 8 (Polish)
- T067-T070 (error handling and logging) can be implemented in parallel
- T071-T073 (documentation updates) can proceed in parallel

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
Focus on **User Story 1 (New Developer Onboarding)** to provide immediate value:
- Complete Phase 1 (Setup)
- Complete Phase 2 (Foundational) - `init_db.py`
- Complete Phase 3 (User Story 1) - `setup_dev.py` and `dev_seed.sql`
- Complete Phase 6 (Shared Seed) - `project_knowledge_seed.sql` (needed by setup_dev.py)

This provides a working development setup procedure that new developers can use immediately.

### Incremental Delivery
1. **Week 1**: MVP (Phases 1, 2, 3, 6) - Development setup working
2. **Week 2**: Production setup (Phase 4) - Production deployment working
3. **Week 3**: Environment clarity (Phase 5) - Documentation and validation
4. **Week 4**: Reorganization and polish (Phases 7, 8) - Codebase organization and final touches

## Task Summary

- **Total Tasks**: 76
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 10 tasks
- **Phase 3 (User Story 1)**: 15 tasks
- **Phase 4 (User Story 2)**: 16 tasks
- **Phase 5 (User Story 3)**: 8 tasks
- **Phase 6 (Shared Seed)**: 6 tasks
- **Phase 7 (Reorganization)**: 7 tasks
- **Phase 8 (Polish)**: 10 tasks

## Independent Test Criteria

### User Story 1
A developer with no prior knowledge can clone the repo, run `python3 setup_dev.py`, and successfully start the application within 15 minutes without asking for help.

### User Story 2
A system administrator can deploy to a new production server by running `python3 setup_prod.py`, and the application is fully functional with all features available.

### User Story 3
A developer can clearly identify which setup procedure to use for their environment, and the procedure validates that they're using the correct environment configuration.

