-- Rollback Migration 000: Drop initial schema tables
-- 
-- WARNING: This will delete ALL data in conversations, messages, and project_knowledge!
-- Only run this if you need to completely remove the base schema.
-- This will also cascade delete conversation_index if it exists (due to FK).

-- Drop indexes first
DROP INDEX IF EXISTS idx_messages_conversation_id;
DROP INDEX IF EXISTS idx_messages_created_at;
DROP INDEX IF EXISTS idx_conversations_project;
DROP INDEX IF EXISTS idx_conversations_created_at;
DROP INDEX IF EXISTS idx_project_knowledge_project;

-- Drop tables in order (respecting foreign key dependencies)
-- conversation_index will be dropped automatically if it exists (CASCADE)
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS project_knowledge;
DROP TABLE IF EXISTS conversations;

