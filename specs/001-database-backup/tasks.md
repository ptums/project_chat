# Tasks: Database Backup Script

**Input**: Design documents from `/specs/001-database-backup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Project Initialization)

**Purpose**: Create directory structure and backup storage location.

- [x] T001 Create `db/backups/` directory at repository root for default backup storage
- [x] T002 Create `db/backups/.gitkeep` file to ensure directory exists in repository
- [x] T003 Add `db/backups/` to `.gitignore` to prevent committing backup files to version control

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks needed by all user stories - environment detection, configuration loading, and backup file naming.

- [x] T004 Create `backup_db.py` script at repository root with command-line argument parsing using `argparse` for `--env`, `--output-dir`, `--verify`, `--list`, `--help` flags
- [x] T005 Implement environment detection logic in `backup_db.py` that reads from `.env.local` (preferred) or `.env` files using `python-dotenv`
- [x] T006 Implement environment type detection in `backup_db.py` that determines dev/prod from `ENV_MODE` or `--env` flag, with `auto` as default
- [x] T007 Implement database configuration loading in `backup_db.py` that supports both `DEV_DB_*` (development) and `DB_*` (production) variables, following pattern from `init_db.py`
- [x] T008 Implement backup directory validation in `backup_db.py` that checks if directory exists, is writable, and creates it if missing
- [x] T009 Implement backup filename generation in `backup_db.py` using format `{database_name}_{environment}_{timestamp}.dump` with ISO 8601 timestamp
- [x] T010 Implement timestamp generation in `backup_db.py` that creates ISO 8601 format timestamps (e.g., `2025-01-27T14-30-00Z`) for backup filenames
- [x] T011 Implement disk space checking in `backup_db.py` that estimates required space (2x database size) and fails early with clear error if insufficient
- [x] T012 Implement `pg_dump` availability check in `backup_db.py` that verifies `pg_dump` is installed and in PATH before attempting backup
- [x] T013 Implement `pg_restore` availability check in `backup_db.py` that verifies `pg_restore` is installed for integrity verification

---

## Phase 3: User Story 1 - Backup Development Database (Priority: P1) 🎯 MVP

**Goal**: Developers can backup their development database with a single command, creating a complete snapshot that can be restored later.
**Independent Test**: A developer can run `python3 backup_db.py --env dev` and successfully create a backup file containing all database tables and data, with timestamp in filename.

- [x] T014 [US1] Implement database connection validation in `backup_db.py` that tests connection to target database before starting backup
- [x] T015 [US1] Implement `pg_dump` execution in `backup_db.py` using subprocess with custom format (`-Fc`), compression level 6 (`-Z 6`), and connection parameters from environment config
- [x] T016 [US1] Implement backup file creation in `backup_db.py` that runs `pg_dump` command and writes output to backup file in specified directory
- [x] T017 [US1] Implement error handling for `pg_dump` failures in `backup_db.py` that captures stderr and provides actionable error messages
- [x] T018 [US1] Implement SHA256 checksum calculation in `backup_db.py` that computes checksum of created backup file using Python `hashlib`
- [x] T019 [US1] Implement database metadata query in `backup_db.py` that queries PostgreSQL for table counts (conversations, messages, project_knowledge, conversation_index) using `psycopg2`
- [x] T020 [US1] Implement PostgreSQL version detection in `backup_db.py` that queries `SELECT version()` to get server version for metadata
- [x] T021 [US1] Implement `pg_dump` version detection in `backup_db.py` that runs `pg_dump --version` to get tool version for metadata
- [x] T022 [US1] Implement metadata file creation in `backup_db.py` that writes JSON file with backup_timestamp, environment, database_name, backup_file, backup_size_bytes, checksum_sha256, table_counts, pg_dump_version, postgresql_version
- [x] T023 [US1] Implement metadata file naming in `backup_db.py` that creates metadata file with same base name as backup file but `.metadata.json` extension
- [x] T024 [US1] Implement success output formatting in `backup_db.py` that displays backup file path, metadata file path, size, environment, database name, table counts, checksum, and verification status
- [x] T025 [US1] Implement partial file cleanup in `backup_db.py` that removes incomplete backup files if backup creation fails mid-process

---

## Phase 4: User Story 2 - Backup Production Database (Priority: P1)

**Goal**: System administrators can backup production database with a single command, ensuring zero-downtime and complete data protection.
**Independent Test**: A system administrator can run `python3 backup_db.py --env prod` and successfully create a production backup without interrupting database operations, with environment identifier in metadata.

- [x] T026 [US2] Implement production environment validation in `backup_db.py` that warns if connecting to localhost/127.0.0.1 for production (may indicate misconfiguration)
- [x] T027 [US2] Ensure `pg_dump` execution uses non-blocking mode (default behavior) that doesn't require database locks or downtime
- [x] T028 [US2] Implement environment identifier in metadata file that stores "prod" for production backups, ensuring clear identification
- [x] T029 [US2] Implement production backup verification that runs integrity check automatically after backup creation (same as US4 but integrated into backup flow)
- [x] T030 [US2] Implement error handling for production backups that provides clear, actionable error messages for connection failures, permission errors, and disk space issues

---

## Phase 5: User Story 4 - Backup Verification and Integrity (Priority: P2)

**Goal**: System administrators can verify backup files are complete and not corrupted before relying on them for restoration.
**Independent Test**: A system administrator can run `python3 backup_db.py --verify <backup_file>` and receive confirmation that the backup file is valid and not corrupted, or clear error if invalid.

- [x] T031 [US4] Implement `--verify` flag handling in `backup_db.py` that accepts backup file path and triggers verification workflow
- [x] T032 [US4] Implement metadata file loading in `backup_db.py` verification that reads corresponding `.metadata.json` file for backup being verified
- [x] T033 [US4] Implement backup file existence check in `backup_db.py` verification that verifies backup file exists at expected path from metadata
- [x] T034 [US4] Implement checksum verification in `backup_db.py` that calculates current SHA256 checksum of backup file and compares with stored checksum from metadata
- [x] T035 [US4] Implement structure verification in `backup_db.py` that runs `pg_restore --list <backup_file>` to validate backup file format and structure
- [x] T036 [US4] Implement verification result reporting in `backup_db.py` that displays checksum match status, structure validation status, and overall verification result (success/failure)
- [x] T037 [US4] Implement error handling for verification failures in `backup_db.py` that provides clear messages for missing files, checksum mismatches, and structure validation failures
- [x] T038 [US4] Integrate automatic verification into backup creation flow in `backup_db.py` that runs `pg_restore --list` after backup file creation to verify integrity before considering backup successful

---

## Phase 6: User Story 3 - Automated Backup Scheduling (Priority: P2)

**Goal**: System administrators can schedule automatic backups without manual intervention, ensuring regular data protection.
**Independent Test**: A system administrator can configure a cron job that runs `python3 backup_db.py --env prod` and verify backup files are created on schedule without manual intervention.

- [x] T039 [US3] Document cron job setup in `quickstart.md` with example crontab entry for daily production backups
- [x] T040 [US3] Document backup retention policy examples in `quickstart.md` showing how to keep last 7 days, last 4 weeks using `find` commands
- [x] T041 [US3] Implement exit code handling in `backup_db.py` that returns appropriate exit codes (0=success, non-zero=error) for cron job monitoring
- [x] T042 [US3] Document error logging for scheduled backups in `quickstart.md` showing how to redirect stdout/stderr to log files for cron jobs
- [x] T043 [US3] Ensure backup script is idempotent and can be run multiple times without side effects (important for scheduling)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling improvements, listing functionality, documentation, and edge case handling.

- [x] T044 Implement `--list` flag handling in `backup_db.py` that scans backup directory for `.dump` files and displays formatted list with timestamp, environment, database name, size, verification status
- [x] T045 Implement backup file scanning in `backup_db.py` listing that finds all `.dump` files in backup directory (default or `--output-dir`)
- [x] T046 Implement metadata loading for listing in `backup_db.py` that loads corresponding metadata files for each backup to display full information
- [x] T047 Implement sorted listing output in `backup_db.py` that displays backups sorted by timestamp (newest first) in formatted table
- [x] T048 Implement `--help` flag handling in `backup_db.py` that displays comprehensive help message with all options, examples, and usage instructions
- [x] T049 Implement comprehensive error handling in `backup_db.py` for database connection failures with clear messages showing connection parameters and troubleshooting steps
- [x] T050 Implement comprehensive error handling in `backup_db.py` for permission errors (database read permissions, filesystem write permissions) with actionable solutions
- [x] T051 Implement comprehensive error handling in `backup_db.py` for disk space errors with clear messages showing required vs available space
- [x] T052 Implement comprehensive error handling in `backup_db.py` for interrupted backups (partial files) with detection and cleanup logic
- [x] T053 Implement concurrent backup detection in `backup_db.py` that checks for existing backup in progress (optional: lock file mechanism) and prevents duplicate backups
- [x] T054 Implement large database handling in `backup_db.py` that uses streaming output from `pg_dump` to avoid memory issues for databases up to 10GB
- [x] T055 Implement custom output directory support in `backup_db.py` that accepts `--output-dir` argument and uses it instead of default `db/backups/`
- [x] T056 Update `README.md` with backup script usage instructions, linking to quickstart guide
- [x] T057 Update `.gitignore` to ensure `db/backups/*.dump` and `db/backups/*.metadata.json` are ignored (backup files should not be committed)
- [x] T058 Add backup script to project documentation index or setup guides if applicable

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **Phase 3 (US1 - MVP)** → **Phase 4 (US2)** → **Phase 5 (US4)** → **Phase 6 (US3)** → **Phase 7 (Polish)**
- **Phase 2** must complete before all user stories (environment detection, configuration loading, filename generation)
- **Phase 3 (US1)** provides MVP functionality - can be deployed independently
- **Phase 4 (US2)** depends on Phase 3 (shares same backup creation logic)
- **Phase 5 (US4)** can proceed in parallel with Phase 4 after Phase 3, but verification is needed for both US1 and US2
- **Phase 6 (US3)** depends on Phase 4 completing (production backups must work before scheduling)
- **Phase 7 (Polish)** depends on all user stories completing

## Parallel Opportunities

### Within Phase 2 (Foundational)
- T005-T007 can be implemented in parallel (different aspects of environment detection)
- T008-T011 can be implemented in parallel (different validation checks)

### Within Phase 3 (US1)
- T018-T021 can be implemented in parallel (checksum, metadata queries, version detection)
- T022-T023 can be implemented together (metadata file creation and naming)

### Within Phase 5 (US4)
- T032-T035 can be implemented in parallel (different verification checks)

### Within Phase 7 (Polish)
- T044-T047 can be implemented together (listing functionality)
- T049-T051 can be implemented in parallel (different error handling scenarios)

## Implementation Strategy

### MVP Scope (Phase 3 - US1 Only)

**Minimum Viable Product**: Development database backup functionality
- Complete Phase 1 (Setup)
- Complete Phase 2 (Foundational)
- Complete Phase 3 (US1 - Backup Development Database)

**Deliverable**: Developers can backup development databases with `python3 backup_db.py --env dev`

**Why this scope**: Provides immediate value for developers, validates core backup functionality, and can be extended to production and verification features incrementally.

### Incremental Delivery

1. **MVP (Phase 1-3)**: Development backup only
2. **Production Support (Phase 4)**: Add production database backup
3. **Verification (Phase 5)**: Add backup integrity verification
4. **Scheduling (Phase 6)**: Document automated scheduling
5. **Polish (Phase 7)**: Listing, error handling improvements, documentation

## Independent Test Criteria

### User Story 1 (MVP)
- Run `python3 backup_db.py --env dev`
- Verify backup file created: `db/backups/{database_name}_dev_{timestamp}.dump`
- Verify metadata file created: `db/backups/{database_name}_dev_{timestamp}.metadata.json`
- Verify backup file contains all tables (can be verified by attempting restore)
- Verify timestamp in filename matches backup creation time

### User Story 2
- Run `python3 backup_db.py --env prod`
- Verify production backup created without database downtime
- Verify metadata contains `"environment": "prod"`
- Verify backup can be restored to test database

### User Story 3
- Configure cron job to run `python3 backup_db.py --env prod`
- Verify backup files created on schedule
- Verify old backups managed according to retention policy

### User Story 4
- Run `python3 backup_db.py --verify <backup_file>`
- Verify checksum validation passes for valid backup
- Verify structure validation passes for valid backup
- Verify verification fails with clear error for corrupted backup

