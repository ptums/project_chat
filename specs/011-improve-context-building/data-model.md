# Data Model: Improve Context Building

## Overview

This feature does not introduce new database tables. It adds a file-based storage for the base system prompt and refactors existing context building logic.

## File-Based Storage

### Base System Prompt File

**Location**: `brain_core/base_system_prompt.txt`

**Structure**: Plain text file containing the base system prompt content.

**Fields**: N/A (single text block)

**Validation Rules**:

- File must exist (with fallback to default if missing)
- Content should be valid UTF-8 text
- No specific length limits (but should be reasonable for LLM context)

## Existing Database Entities (Unchanged)

### project_knowledge Table

**Purpose**: Stores project-specific knowledge summaries (unchanged by this feature)

**Key Fields Used**:

- `project`: Project tag (THN, DAAS, FF, 700B)
- `key`: Knowledge entry key (e.g., 'overview')
- `summary`: Text content used for project-specific context extension

**Usage**: The `overview` key's summary is used to append project context to base system prompt.

## In-Memory Entities

### System Prompt Composition

**Purpose**: Composed system prompt used in chat conversations

**Structure**:

```python
{
    "base_prompt": str,           # Loaded from base_system_prompt.txt
    "project_extension": str,    # Optional: "In this current conversation is tagged as project <name> and here we are going to discuss <overview>."
    "composed_prompt": str        # Final composed prompt: base + project_extension
}
```

**Lifecycle**: Composed on-demand during `chat_turn()` or `build_project_context()` calls.

## No Schema Changes

- No new database tables
- No new columns in existing tables
- No migration required
