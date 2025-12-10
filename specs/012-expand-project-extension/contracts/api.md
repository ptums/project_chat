# API Contract: Project Rules Extension

## Overview

This contract defines the functions and database schema for including project-specific rules in system prompts.

## Database Schema

### project_knowledge Table (Modified)

**New Structure**:

```sql
CREATE TABLE project_knowledge (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL UNIQUE,
    overview TEXT NOT NULL,
    rules TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Migration**: See `db/migrations/004_project_knowledge_simplify.sql`

## Functions

### `_get_project_overview(project: str) -> Optional[str]`

**Modified Function**: Updated to query new table structure.

**Changes**:

- Queries `overview` column directly (no `key='overview'` filter needed)
- Returns overview text or None

**Example**:

```python
from brain_core.context_builder import _get_project_overview
overview = _get_project_overview("DAAS")
```

### `_get_project_rules(project: str) -> Optional[str]`

**New Function**: Retrieves project rules from `project_knowledge` table.

**Parameters**:

- `project`: Project tag (THN, DAAS, FF, 700B)

**Returns**: Rules text as string, or None if not found or empty

**Example**:

```python
from brain_core.context_builder import _get_project_rules
rules = _get_project_rules("THN")
```

### `_parse_rules_text(rules_text: str) -> List[str]`

**New Function**: Parses rules text into list of individual rules.

**Parameters**:

- `rules_text`: Raw rules text from database

**Returns**: List of rule strings (cleaned and filtered)

**Behavior**:

- Splits on numbered patterns (1., 2., etc.) or newlines
- Strips whitespace from each rule
- Filters empty rules
- Returns list of clean rule strings

**Example**:

```python
from brain_core.context_builder import _parse_rules_text
rules_list = _parse_rules_text("1. Rule one\n2. Rule two\n3. Rule three")
# Returns: ["Rule one", "Rule two", "Rule three"]
```

### `build_project_system_prompt(project: str) -> str`

**Modified Function**: Updated to include project rules section.

**Changes**:

- Retrieves both overview and rules from `project_knowledge` table
- Formats rules as numbered bullet list
- Includes rules section in composed prompt

**Format**:

```
{base_prompt}

In this current conversation is tagged as project {PROJECT}.

Here's a general overview of the project {PROJECT}: {overview}

---

### Project {PROJECT} rules:

1. {rule 1}
2. {rule 2}
3. {rule 3}
...
```

**Behavior**:

- If rules are missing or empty, omits rules section
- If overview is missing, uses base prompt only
- Rules are formatted as markdown numbered list

## Integration Points

### Migration Script

**Location**: `db/migrations/004_project_knowledge_simplify.sql`

**Responsibilities**:

- Create new table structure
- Migrate overview data from old structure
- Drop old table
- Recreate indexes

### Seed Data

**Location**: `db/seeds/project_knowledge_seed_v2.sql`

**Format**:

```sql
INSERT INTO project_knowledge (project, overview, rules)
VALUES (
  'THN',
  'THN (Tumulty Home Network) is...',
  '1. Rule one\n2. Rule two\n3. Rule three'
)
ON CONFLICT (project) DO UPDATE SET
  overview = EXCLUDED.overview,
  rules = EXCLUDED.rules;
```

## Error Handling

- If `overview` is missing: Use base prompt only (log warning)
- If `rules` is missing or empty: Omit rules section (no error)
- If rules parsing fails: Use raw rules text as single rule (log warning)
- All errors are logged but do not break the chat flow
