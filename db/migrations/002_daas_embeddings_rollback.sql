-- Rollback Migration 002: Remove embedding column and index for DAAS
--
-- WARNING: This will permanently delete all embedding data!
-- Only run this if you need to completely rollback the migration.
--
-- Run these queries in order using psql or your PostgreSQL client

-- Step 1: Drop vector similarity index
DROP INDEX IF EXISTS idx_conversation_index_embedding;

-- Step 2: Remove embedding column
ALTER TABLE conversation_index 
DROP COLUMN IF EXISTS embedding;

-- Step 3: Optionally remove pgvector extension
-- UNCOMMENT ONLY if you want to completely remove pgvector
-- (Note: pgvector may be used by other features, so this is usually not recommended)
-- DROP EXTENSION IF EXISTS vector CASCADE;

-- Verification queries (optional - run to confirm rollback):
-- Check column is removed:
-- SELECT column_name 
-- FROM information_schema.columns 
-- WHERE table_name = 'conversation_index' AND column_name = 'embedding';
-- (Should return 0 rows)

-- Check index is removed:
-- SELECT indexname 
-- FROM pg_indexes 
-- WHERE tablename = 'conversation_index' 
--   AND indexname = 'idx_conversation_index_embedding';
-- (Should return 0 rows)

