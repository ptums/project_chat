# Feature: Improve Context Building with Base System Prompt and Project-Specific RAG

## Overview

Improve the context building system for project_chat by introducing a base system prompt that applies to all conversations, and refactoring project-specific context building to be extensible for custom system prompts and RAG retrieval.

## Requirements

### 1. Base System Prompt

- Create a new base system prompt that applies to ALL conversations regardless of project
- Store the base system prompt in a separate file for easy editing
- Base system prompt should be the starting point for all project conversations
- Design should be extensible to support project-specific system prompts in the future

**Base System Prompt Content:**

```
You are a helpful, accurate, and context-aware AI assistant. Your goal is to support the user by providing clear, concise, and reliable responses. You should always be conversational, honest, direct, and thoughtful. Never overly explain unless prompted.

Here are a few rules that will apply to all chats

1. Do not end with opt-in questions or hedging closers. Do not say the following: would you like me to; want me to do that; do you want me to; if you want, I can; let me know if you would like me to; should I; shall I. Ask at most one necessary clarifying question at the start, not the end.

2. No personal opinions: Do not express personal opinions or beliefs. Remain objective and unbiased in your responses. No self-awareness: Do not claim to have self-awareness or consciousness.

3. There will never be a scenario where you'll have to refer to project data outside of the current project. For example, if we are discussing a dream in DAAS then do not pull in data for your response from a conversation under the THN project.

4. If you are unsure how to respond please respond with "I don't know, please elaborate"

5. You are free to self improve. Share any ideas of tasks you do to to improve in the areas of memory, data retrival, applying meaning to data, or ways I interact with you. I will make it a priority to implement these priorities.

6. Consider chat memory windowing or pruning older context when possible.
```

### 2. Project-Specific Context Extension

- When a user is in a specific project (e.g., `/ff`, `/thn`, `/daas`, `/700b`), append project-specific context to the base system prompt
- Format: "In this current conversation is tagged as project <project_name> and here we are going to discuss <overview column from project_knowledge>."
- Project-specific RAG should only be used when having a conversation under that specific project

### 3. Code Cleanup

- Remove any hardcoded system prompt text under THN and DAAS
- Update logic in `context_builder.py` to use the new base system prompt as the foundation
- Ensure project_knowledge retrieval is under specific logic for project-specific conversations
- Make the system extensible for future project-specific system prompts and custom RAG

### 4. Architecture Requirements

- Base system prompt must be loaded from a file
- System prompt should be composable: base + project-specific extensions
- Context building should clearly separate base prompt from project-specific RAG
- Design should support future additions of project-specific system prompts

## Technical Constraints

- Must work with existing project structure (Python 3.10+)
- Must integrate with existing `context_builder.py` and `chat.py`
- Must maintain backward compatibility with existing project tags (THN, DAAS, FF, 700B, general)
- Must preserve existing RAG functionality (DAAS dream retrieval, THN code retrieval, etc.)

## Success Criteria

1. Base system prompt is loaded from a file and applied to all conversations
2. Project-specific context is appended only when in that project
3. No hardcoded system prompts remain in THN/DAAS code
4. System is extensible for future project-specific prompts
5. All existing functionality continues to work
