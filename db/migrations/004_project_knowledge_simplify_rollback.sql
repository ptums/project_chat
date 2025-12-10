-- Rollback Migration 004: Restore project_knowledge table to original structure
-- 
-- WARNING: This will delete the simplified table structure and recreate the old structure.
-- Overview data will be preserved, but you may need to manually restore other key entries.
--
-- Last updated: 2025-01-27

-- Step 1: Create backup of current data
CREATE TABLE IF NOT EXISTS project_knowledge_backup_004 AS
SELECT * FROM project_knowledge;

-- Step 2: Drop simplified table
DROP TABLE IF EXISTS project_knowledge;

-- Step 3: Recreate original table structure
CREATE TABLE IF NOT EXISTS project_knowledge (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    key TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(project, key)
);

-- Step 4: Restore overview data from backup
-- Convert overview back to summary with key='overview'
INSERT INTO project_knowledge (project, key, summary, created_at)
SELECT 
    project,
    'overview' AS key,
    overview AS summary,
    created_at
FROM project_knowledge_backup_004
WHERE overview IS NOT NULL;

-- Step 5: Recreate index
CREATE INDEX IF NOT EXISTS idx_project_knowledge_project 
ON project_knowledge(project);

-- Step 6: Drop backup table (optional - keep for safety)
-- DROP TABLE IF EXISTS project_knowledge_backup_004;

-- Note: Other key entries (machine_roles, design_principles, etc.) are not restored.
-- You may need to re-run original seed data or restore from full database backup.
