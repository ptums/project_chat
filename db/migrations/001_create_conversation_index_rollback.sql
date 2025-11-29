-- Rollback Migration 001: Drop conversation_index table
-- 
-- WARNING: This will delete all conversation index data!
-- Only run this if you need to completely remove the conversation_index feature.

-- Drop indexes first
DROP INDEX IF EXISTS idx_conversation_index_project;
DROP INDEX IF EXISTS idx_conversation_index_indexed_at;
DROP INDEX IF EXISTS idx_conversation_index_project_indexed_at;

-- Drop foreign key constraint (if it exists)
ALTER TABLE conversation_index 
DROP CONSTRAINT IF EXISTS conversation_index_session_id_fkey;

-- Drop the table
DROP TABLE IF EXISTS conversation_index;

