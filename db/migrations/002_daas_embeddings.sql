-- Migration 002: Add pgvector extension and embedding column for DAAS semantic retrieval
-- 
-- This migration adds:
-- 1. pgvector extension (for vector operations)
-- 2. embedding column to conversation_index table
-- 3. Vector similarity index for DAAS entries
--
-- Run these queries in order using psql or your PostgreSQL client

-- Step 1: Install pgvector extension
-- Note: Requires superuser privileges or CREATE EXTENSION permission
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Add embedding column to conversation_index table
-- This column stores 1536-dimensional vectors for DAAS project entries
ALTER TABLE conversation_index 
ADD COLUMN embedding vector(1536);

-- Step 3: Create vector similarity index
-- IVFFlat index with cosine similarity for fast approximate nearest neighbor search
-- Partial index: only indexes DAAS entries with embeddings
CREATE INDEX idx_conversation_index_embedding 
ON conversation_index 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100)
WHERE project = 'DAAS' AND embedding IS NOT NULL;

-- Verification queries (optional - run to confirm migration):
-- Check extension is installed:
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check column exists:
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'conversation_index' AND column_name = 'embedding';

-- Check index exists:
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'conversation_index' 
--   AND indexname = 'idx_conversation_index_embedding';

