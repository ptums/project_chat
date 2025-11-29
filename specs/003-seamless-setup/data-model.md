# Data Model: Seamless Environment Setup

**Feature**: 003-seamless-setup  
**Date**: 2025-01-27  
**Phase**: 1 - Design & Contracts

## Overview

This feature does not introduce new database tables or modify existing schemas. Instead, it provides setup procedures, seed data, and migration orchestration for existing tables. The data model documentation focuses on seed data structures and setup state management.

## Seed Data Entities

### Development Seed Data (`db/seeds/dev_seed.sql`)

**Purpose**: Provide sample conversations for local development and testing.

**Structure**: SQL INSERT statements for `conversations` and `messages` tables.

**Content Requirements**:
- Minimum 3 sample conversations
- Cover different projects: THN, DAAS, FF, 700B, or general
- Each conversation should have 2-3 messages (user + assistant)
- Use clearly identifiable test UUIDs (e.g., `00000000-0000-0000-0000-000000000001`)

**Example Structure**:
```sql
-- Sample conversation 1: DAAS project
INSERT INTO conversations (id, title, project, created_at)
VALUES ('00000000-0000-0000-0000-000000000001', 'Sample Dream Analysis', 'DAAS', NOW())
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title;

INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES 
  ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'user', 'I had a dream about flying...', NOW()),
  ('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'assistant', 'Flying dreams often represent...', NOW())
ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;
```

**Validation Rules**:
- UUIDs must be unique across all seed conversations
- `conversation_id` in messages must reference existing conversation
- Project values must be valid: 'THN', 'DAAS', 'FF', '700B', or 'general'

### Shared Project Knowledge Seed Data (`db/seeds/project_knowledge_seed.sql`)

**Purpose**: Load stable project knowledge entries for all environments (dev and prod). This is public-safe data that is consistent across environments.

**Structure**: SQL INSERT statements for `project_knowledge` table.

**Content Requirements**:
- Project knowledge entries for all active projects: THN, DAAS, FF, 700B
- Each entry must have a unique `(project, key)` combination
- `summary` field should contain meaningful project context
- Content is public-safe and will be audited by project maintainer
- Same file used for both development and production environments

**Example Structure**:
```sql
-- THN project knowledge
INSERT INTO project_knowledge (project, key, summary, created_at)
VALUES 
  ('THN', 'overview', 'THN is a project focused on...', NOW()),
  ('THN', 'goals', 'Primary goals include...', NOW())
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- DAAS project knowledge
INSERT INTO project_knowledge (project, key, summary, created_at)
VALUES 
  ('DAAS', 'overview', 'DAAS is a dream analysis and...', NOW()),
  ('DAAS', 'analysis_approaches', 'Supports multiple analytical frameworks...', NOW())
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- FF project knowledge
INSERT INTO project_knowledge (project, key, summary, created_at)
VALUES 
  ('FF', 'overview', 'FF is a project focused on...', NOW())
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- 700B project knowledge
INSERT INTO project_knowledge (project, key, summary, created_at)
VALUES 
  ('700B', 'overview', '700B is a project focused on...', NOW())
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;
```

**Validation Rules**:
- `(project, key)` combination must be unique (enforced by table constraint)
- Project values must be valid: 'THN', 'DAAS', 'FF', '700B'
- Summary text should be non-empty and meaningful
- Content must be public-safe (no sensitive information)

### Production Seed Data (`db/seeds/prod_seed.sql`)

**Purpose**: Load production-specific seed data (if needed). Currently, production seed data primarily consists of the shared project knowledge (loaded via `project_knowledge_seed.sql`).

**Structure**: SQL INSERT statements (currently minimal or empty).

**Note**: Production-specific conversation seed data is typically loaded via `import_chatgpt_from_zip.py` rather than static seed files.

## Setup State Management

### Migration State

**No explicit migration state table is required.** Instead, setup scripts determine migration state by checking table existence:

- **Migration 000 applied**: `conversations` table exists
- **Migration 001 applied**: `conversation_index` table exists
- **Migration 002 applied**: `conversation_index.embedding` column exists

**Rationale**: Table existence checks are sufficient for this project's scale. A migration version table would add unnecessary complexity.

### Environment State

Setup scripts validate environment state through:

1. **Environment Variables**:
   - `ENV_MODE`: Must be 'development' or 'production'
   - `DEV_DB_NAME` or `DB_NAME`: Database name
   - Database connection variables: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`

2. **Database Connectivity**:
   - Test connection before proceeding
   - Validate database exists (or can be created)

3. **Database Schema State**:
   - Check which migrations have been applied
   - Detect existing seed data (optional, for idempotency)

## Existing Tables (Referenced, Not Modified)

### conversations
- **Purpose**: Store conversation metadata
- **Key Fields**: `id` (UUID), `title`, `project`, `created_at`
- **Used By**: Development seed data

### messages
- **Purpose**: Store individual messages within conversations
- **Key Fields**: `id` (UUID), `conversation_id` (FK), `role`, `content`, `created_at`
- **Used By**: Development seed data

### project_knowledge
- **Purpose**: Store stable project knowledge entries
- **Key Fields**: `id` (SERIAL), `project`, `key`, `summary`, `created_at`
- **Constraints**: `UNIQUE(project, key)`
- **Used By**: Production seed data

### conversation_index
- **Purpose**: Store conversation metadata and embeddings (from previous features)
- **Key Fields**: `session_id` (FK to conversations), `project`, `embedding` (vector)
- **Used By**: Not directly used by this feature, but migrations must be applied before seed data

## Data Flow

### Development Setup Flow

1. **Database Initialization**: Run `init_db.py` to create development database (reads from `.env.local` or `.env`)
2. **Migration Application**: Run migrations 000 → 001 → 002 in order
3. **Seed Data Loading**: 
   - Execute `db/seeds/project_knowledge_seed.sql` (shared project knowledge) - **loaded first as foundational data for RAG**
   - Execute `db/seeds/dev_seed.sql` (sample conversations) - **loaded after project knowledge**
4. **Verification**: Check that tables exist and seed data is present

### Production Setup Flow

1. **Environment Validation**: Verify `ENV_MODE=production` and database configuration
2. **Database Initialization**: Run `init_db.py` to ensure production database exists (reads from `.env`)
3. **Migration Application**: Run migrations 000 → 001 → 002 in order (skip if already applied)
4. **Seed Data Loading**: 
   - Execute `db/seeds/project_knowledge_seed.sql` (shared project knowledge) - **loaded first as foundational data for RAG**
   - Execute `db/seeds/prod_seed.sql` (if any production-specific data) - **loaded after project knowledge**
5. **Verification**: Check that tables exist and project knowledge is loaded

## Constraints and Validation

### Seed Data Constraints

- **Idempotency**: All seed data uses `ON CONFLICT DO UPDATE` to allow safe re-running
- **Referential Integrity**: Messages must reference existing conversations
- **Project Validation**: Project values must match allowed values
- **UUID Format**: Seed UUIDs should follow standard UUID format

### Setup Script Constraints

- **Migration Order**: Migrations must run in order (000 → 001 → 002)
- **Environment Separation**: Development setup must not run on production database
- **Database Existence**: Database must exist or be creatable before migrations
- **Connection Validation**: Database connection must be testable before proceeding

## Error Handling

### Common Error Scenarios

1. **Database doesn't exist**: Create it (dev) or error with instructions (prod)
2. **Migration already applied**: Skip with informational message
3. **Seed data conflict**: Use UPSERT to update existing data
4. **Invalid environment**: Error with clear message about required configuration
5. **Connection failure**: Error with troubleshooting guidance

### Error Messages

Setup scripts should provide:
- Clear error descriptions
- Actionable guidance (what to check/fix)
- Relevant environment variable names
- Links to documentation if applicable

