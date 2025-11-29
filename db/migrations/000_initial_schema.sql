-- Migration 000: Initial Schema (001-dev-environment)
-- 
-- Creates the base tables: conversations, messages, project_knowledge
-- This is the foundation for all other features.
--
-- Run this FIRST before any other migrations.

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    project TEXT NOT NULL DEFAULT 'general',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create messages table with foreign key to conversations
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    meta_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create project_knowledge table
CREATE TABLE IF NOT EXISTS project_knowledge (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    key TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(project, key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at 
ON messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_project 
ON conversations(project);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_project_knowledge_project 
ON project_knowledge(project);

-- Verification queries (optional - run to confirm migration):
-- Check tables exist:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_name IN ('conversations', 'messages', 'project_knowledge')
-- ORDER BY table_name;

-- Check foreign key exists:
-- SELECT 
--     tc.constraint_name, 
--     tc.table_name, 
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY' 
--   AND tc.table_name = 'messages';

