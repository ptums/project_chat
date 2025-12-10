-- Migration 004: Simplify project_knowledge table structure
-- 
-- Simplifies project_knowledge table to only overview and rules columns.
-- Migrates existing overview data from summary column where key='overview'.
-- One row per project (not one per key).
--
-- Run this after migration 003_thn_code_index.sql
-- Last updated: 2025-01-27

-- Step 1: Create new table structure
CREATE TABLE IF NOT EXISTS project_knowledge_new (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL UNIQUE,
    overview TEXT NOT NULL,
    rules TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Step 2: Migrate overview data from old structure
-- Extract overview from summary where key='overview', one row per project
INSERT INTO project_knowledge_new (project, overview, rules, created_at)
SELECT 
    project,
    summary AS overview,
    NULL AS rules,  -- Rules will be added later via seed data
    MIN(created_at) AS created_at  -- Use earliest created_at for each project
FROM project_knowledge
WHERE key = 'overview'
GROUP BY project, summary
ON CONFLICT (project) DO NOTHING;

-- Step 3: Create index on project column
CREATE INDEX IF NOT EXISTS idx_project_knowledge_new_project 
ON project_knowledge_new(project);

-- Step 4: Drop old table
DROP TABLE IF EXISTS project_knowledge;

-- Step 5: Rename new table to original name
ALTER TABLE project_knowledge_new RENAME TO project_knowledge;

-- Step 6: Rename index to match new table name
ALTER INDEX idx_project_knowledge_new_project RENAME TO idx_project_knowledge_project;

-- Verification queries (optional - run to confirm migration):
-- Check table structure:
-- \d project_knowledge

-- Check overview data migrated:
-- SELECT project, overview, rules FROM project_knowledge ORDER BY project;

-- Check indexes:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'project_knowledge';
