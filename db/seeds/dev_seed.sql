-- Development Seed Data
-- 
-- This file contains sample conversations for local development and testing.
-- It includes 3 sample conversations covering different projects (THN, DAAS, FF, 700B, or general).
-- Each conversation has 2-3 messages (user + assistant) for realistic sample data.
--
-- Uses UPSERT semantics (ON CONFLICT DO UPDATE) for idempotent loading.
-- Test UUIDs are clearly identifiable (00000000-0000-0000-0000-000000000001, etc.)
--
-- Validation Requirements:
-- - All project values must be one of: 'THN', 'DAAS', 'FF', '700B', 'general'
-- - All conversations must have at least one message
-- - All message conversation_id values must reference existing conversations

-- Sample conversation 1: DAAS - Dream Analysis
INSERT INTO conversations (id, title, project, created_at)
VALUES ('00000000-0000-0000-0000-000000000001', 'Flying Dream Analysis', 'DAAS', NOW())
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, project = EXCLUDED.project;

INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES 
  ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'user', 'I had a dream about flying over mountains. What does this mean?', NOW()),
  ('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'assistant', 'Flying dreams often represent freedom, liberation, or a desire to escape constraints. Mountains can symbolize challenges or goals. Together, this might suggest you are overcoming obstacles or achieving personal growth. Would you like to explore this from a specific analytical framework?', NOW())
ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;

-- Sample conversation 2: THN - Project Planning
INSERT INTO conversations (id, title, project, created_at)
VALUES ('00000000-0000-0000-0000-000000000002', 'Q1 Planning Discussion', 'THN', NOW())
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, project = EXCLUDED.project;

INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES 
  ('00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000002', 'user', 'Let''s discuss the Q1 roadmap for the THN project. What are our key priorities?', NOW()),
  ('00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000002', 'assistant', 'Based on our previous discussions, the Q1 priorities for THN should focus on: 1) Core feature implementation, 2) User testing and feedback, 3) Performance optimization. Should we break these down into specific tasks?', NOW()),
  ('00000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000002', 'user', 'Yes, let''s create a task breakdown for each priority.', NOW())
ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;

-- Sample conversation 3: General - Technical Question
INSERT INTO conversations (id, title, project, created_at)
VALUES ('00000000-0000-0000-0000-000000000003', 'Python Best Practices', 'general', NOW())
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, project = EXCLUDED.project;

INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES 
  ('00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000003', 'user', 'What are some best practices for error handling in Python?', NOW()),
  ('00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000003', 'assistant', 'Key best practices for error handling in Python include: 1) Use specific exception types rather than bare except clauses, 2) Provide meaningful error messages, 3) Use try-except-finally for resource cleanup, 4) Consider using context managers for file operations, 5) Log errors appropriately. Would you like examples for any of these?', NOW())
ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;
