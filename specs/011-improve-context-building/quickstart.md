# Quickstart: Improve Context Building with Base System Prompt

## Overview

This guide shows how to use and extend the new base system prompt system for project conversations.

## Prerequisites

- Python 3.10+ (existing requirement)
- Existing project_chat installation
- No new dependencies required

## Setup

### Step 1: Create Base System Prompt File

Create `brain_core/base_system_prompt.txt` with the base system prompt content:

```bash
# From project root
cat > brain_core/base_system_prompt.txt << 'EOF'
You are a helpful, accurate, and context-aware AI assistant. Your goal is to support the user by providing clear, concise, and reliable responses. You should always be conversational, honest, direct, and thoughtful. Never overly explain unless prompted.

Here are a few rules that will apply to all chats

1. Do not end with opt-in questions or hedging closers. Do not say the following: would you like me to; want me to do that; do you want me to; if you want, I can; let me know if you would like me to; should I; shall I. Ask at most one necessary clarifying question at the start, not the end.

2. No personal opinions: Do not express personal opinions or beliefs. Remain objective and unbiased in your responses. No self-awareness: Do not claim to have self-awareness or consciousness.

3. There will never be a scenario where you'll have to refer to project data outside of the current project. For example, if we are discussing a dream in DAAS then do not pull in data for your response from a conversation under the THN project.

4. If you are unsure how to respond please respond with "I don't know, please elaborate"

5. You are free to self improve. Share any ideas of tasks you do to to improve in the areas of memory, data retrival, applying meaning to data, or ways I interact with you. I will make it a priority to implement these priorities.

6. Consider chat memory windowing or pruning older context when possible.
EOF
```

### Step 2: Verify Project Knowledge

Ensure `project_knowledge` table has `overview` entries for each project:

```sql
SELECT project, key, summary
FROM project_knowledge
WHERE key = 'overview';
```

If missing, run the seed script:

```bash
psql -d project_chat -f db/seeds/project_knowledge_seed.sql
```

## Usage

### Normal Operation

The system automatically:

1. Loads base system prompt from `base_system_prompt.txt`
2. Appends project-specific extension when user is in a project (e.g., `/daas`, `/thn`)
3. Uses composed prompt in all conversations

**Example Flow**:

```
User: /daas
System: Loads base prompt + appends "In this current conversation is tagged as project DAAS and here we are going to discuss <DAAS overview>."

User: /general
System: Uses base prompt only (no project extension)
```

### Editing Base System Prompt

Simply edit `brain_core/base_system_prompt.txt`:

```bash
vim brain_core/base_system_prompt.txt
# Make changes, save
# Changes take effect on next chat_turn() call (prompt is cached)
```

### Testing

1. Start chat CLI:

   ```bash
   python chat_cli.py
   ```

2. Switch to a project:

   ```
   /daas
   ```

3. Verify system prompt includes:

   - Base prompt content
   - Project-specific extension: "In this current conversation is tagged as project DAAS..."

4. Switch to general:

   ```
   /general
   ```

5. Verify system prompt includes only base prompt (no project extension)

## Troubleshooting

### Base Prompt Not Loading

**Symptom**: Chat uses fallback minimal prompt

**Solution**:

- Check that `brain_core/base_system_prompt.txt` exists
- Check file permissions (must be readable)
- Check logs for warnings about missing file

### Project Extension Not Appearing

**Symptom**: Project-specific extension not added to prompt

**Solution**:

- Verify `project_knowledge` table has entry with `key = 'overview'` for the project
- Check that project tag is normalized correctly (uppercase: THN, DAAS, FF, 700B)
- Review logs for errors in project_knowledge retrieval

### Hardcoded Prompts Still Present

**Symptom**: Old hardcoded prompts still in use

**Solution**:

- Verify `chat.py` has been updated to use `build_project_system_prompt()`
- Check that `context_builder.py` has been refactored
- Review code for any remaining hardcoded prompt strings

## Future Extensions

The system is designed to support:

- Project-specific custom system prompts (stored separately, appended after base + project extension)
- Custom RAG retrieval per project (already partially implemented for DAAS/THN)
- Dynamic prompt composition based on conversation state

These extensions can be added without breaking existing functionality.
