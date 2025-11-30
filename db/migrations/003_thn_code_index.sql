-- Migration 003: Create code_index table for THN code RAG pipeline
-- 
-- This migration adds:
-- 1. code_index table for storing code chunks with embeddings
-- 2. Vector similarity index for semantic code search
-- 3. Indexes for repository, language, file path, and production targets
--
-- Note: pgvector extension should already be installed (from migration 002)
-- Run these queries in order using psql or your PostgreSQL client

-- Step 1: Ensure pgvector extension is installed (should already exist from DAAS migration)
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create code_index table
CREATE TABLE IF NOT EXISTS code_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    language TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_metadata JSONB,
    embedding vector(1536),
    production_targets TEXT[],
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_updated TIMESTAMPTZ
);

-- Step 3: Create vector similarity index
-- IVFFlat index with cosine similarity for fast approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_code_index_embedding 
ON code_index 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100)
WHERE embedding IS NOT NULL;

-- Step 4: Create repository and language filter index
CREATE INDEX IF NOT EXISTS idx_code_index_repo_lang 
ON code_index (repository_name, language);

-- Step 5: Create file path lookup index
CREATE INDEX IF NOT EXISTS idx_code_index_file_path 
ON code_index (file_path);

-- Step 6: Create production targets filter index (GIN for array containment)
CREATE INDEX IF NOT EXISTS idx_code_index_production_targets 
ON code_index USING GIN (production_targets);

-- Verification queries (optional - run to confirm migration):
-- Check table exists:
-- SELECT table_name FROM information_schema.tables WHERE table_name = 'code_index';

-- Check columns:
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'code_index'
-- ORDER BY ordinal_position;

-- Check indexes:
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'code_index'
-- ORDER BY indexname;

