# API Contract: Context Building System

## Overview

This contract defines the functions and interfaces for loading and composing system prompts in the context building system.

## Functions

### `load_base_system_prompt() -> str`

Loads the base system prompt from `brain_core/base_system_prompt.txt`.

**Returns**: Base system prompt as string

**Raises**:

- `FileNotFoundError`: If file doesn't exist (handled with fallback)
- `IOError`: If file cannot be read (handled with fallback)

**Side Effects**: Caches prompt in module-level variable to avoid repeated file I/O

**Example**:

```python
from brain_core.context_builder import load_base_system_prompt
base_prompt = load_base_system_prompt()
```

### `build_project_system_prompt(project: str) -> str`

Builds the complete system prompt for a given project by composing base prompt with project-specific extension.

**Parameters**:

- `project`: Project tag (THN, DAAS, FF, 700B, or "general")

**Returns**: Composed system prompt string

**Behavior**:

- Loads base system prompt
- If project is not "general", appends project-specific extension using format: "In this current conversation is tagged as project <project_name> and here we are going to discuss <overview from project_knowledge>."
- Returns composed prompt

**Example**:

```python
from brain_core.context_builder import build_project_system_prompt
system_prompt = build_project_system_prompt("DAAS")
```

### `build_project_context(project: str, user_message: str, ...) -> Dict[str, Any]`

**Modified Function**: Existing function is refactored to use new system prompt composition.

**Changes**:

- No longer includes hardcoded system prompt text
- System prompt is built separately using `build_project_system_prompt()`
- RAG retrieval logic remains unchanged (only used for project-specific conversations)

**Returns**: Dict with 'context' (RAG content) and 'notes' (metadata). System prompt is handled separately in `chat.py`.

## Integration Points

### `chat_turn()` in `brain_core/chat.py`

**Changes**:

- Removes hardcoded `base_system` string (lines 75-89)
- Calls `build_project_system_prompt(project)` to get composed system prompt
- Appends system prompt as system message before other context messages

**Message Order** (unchanged):

1. System message: Composed system prompt (base + project extension)
2. System message: Project context from RAG (if available)
3. System message: Note reads (if any)
4. User/Assistant messages from history

## Error Handling

- If `base_system_prompt.txt` is missing: Log warning and use minimal fallback prompt
- If project_knowledge overview is missing: Project extension is omitted (base prompt only)
- All errors are logged but do not break the chat flow
