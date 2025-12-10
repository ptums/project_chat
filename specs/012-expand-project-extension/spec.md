# Feature: Expand Project-Specific Extension with Rules

## Overview

Expand the project-specific system prompt extension to include project-specific rules. Migrate the `project_knowledge` table to a simplified structure with only `overview` and `rules` columns, and update the system prompt composition to include project rules as a bullet list.

## Requirements

### 1. Database Migration

- Create migration script to update `project_knowledge` table structure
- Drop all existing columns except `overview` and `rules`
- Keep `overview` column (currently stored in `summary` column with `key='overview'`)
- Add `rules` column (TEXT) for project-specific rules
- Maintain project identification (project column)
- Preserve existing overview data during migration

### 2. System Prompt Extension Format

Update `build_project_system_prompt()` to include:

```
In this current conversation is tagged as project {PROJECT}.

Here's a general overview of the project {PROJECT}: {overview}

---

### Project {PROJECT} rules:

1. {rule 1 from rules column}
2. {rule 2 from rules column}
3. {rule 3 from rules column}
...
```

### 3. Rules Column Format

- `rules` column stores text with numbered rules
- Rules are separated by newlines or numbered list format
- Each rule should be a complete sentence or instruction
- Rules are displayed as a bullet list in the system prompt

### 4. Seed Data

- Create sample seed data file using current `project_knowledge` overview data
- Include placeholder structure for rules column
- User will fill in actual rules later
- Seed data should reference existing overview content from current seed file

## Technical Constraints

- Must maintain backward compatibility during migration
- Must preserve existing overview data
- Migration must be reversible (rollback script)
- Must work with existing project tags (THN, DAAS, FF, 700B, general)
- Rules column should handle multi-line text

## Success Criteria

1. Migration script successfully updates `project_knowledge` table structure
2. Overview data is preserved from existing `summary` column
3. System prompt includes project rules section
4. Rules are formatted as numbered bullet list
5. Sample seed data created for all projects
6. Migration is reversible
