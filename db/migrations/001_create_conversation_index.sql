-- Migration 001: Create conversation_index table
-- 
-- This migration creates the conversation_index table for the Ollama Conversation Organizer feature.
-- This table stores organized summaries, tags, and metadata about conversations.
--
-- Run this migration BEFORE running 002_daas_embeddings.sql if conversation_index doesn't exist yet.

-- Create conversation_index table
CREATE TABLE IF NOT EXISTS conversation_index (
    session_id UUID PRIMARY KEY,
    project TEXT NOT NULL CHECK (project IN ('THN', 'DAAS', 'FF', '700B', 'general')),
    title TEXT,
    tags JSONB,
    summary_short TEXT,
    summary_detailed TEXT,
    key_entities JSONB,
    key_topics JSONB,
    memory_snippet TEXT,
    ollama_model TEXT NOT NULL DEFAULT 'llama3:8b',
    version INTEGER NOT NULL DEFAULT 1,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create foreign key to conversations table (if it exists)
-- Note: This assumes your conversations table is named 'conversations' with 'id' as primary key
-- Adjust the table/column names if your schema differs
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'conversations') THEN
        -- Add foreign key constraint if conversations table exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'conversation_index_session_id_fkey'
        ) THEN
            ALTER TABLE conversation_index
            ADD CONSTRAINT conversation_index_session_id_fkey
            FOREIGN KEY (session_id) REFERENCES conversations(id) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_conversation_index_project 
ON conversation_index(project);

CREATE INDEX IF NOT EXISTS idx_conversation_index_indexed_at 
ON conversation_index(indexed_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_index_project_indexed_at 
ON conversation_index(project, indexed_at DESC);

-- Verification queries (optional - run to confirm migration):
-- Check table exists:
-- SELECT table_name FROM information_schema.tables WHERE table_name = 'conversation_index';

-- Check columns:
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'conversation_index' 
-- ORDER BY ordinal_position;

-- Check indexes:
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'conversation_index';

