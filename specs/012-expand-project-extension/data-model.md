# Data Model: Expand Project-Specific Extension with Rules

## Overview

This feature modifies the `project_knowledge` table structure to simplify it to only `overview` and `rules` columns, and updates the system prompt composition to include project rules.

## Database Schema Changes

### project_knowledge Table (Modified)

**Current Structure**:

```sql
CREATE TABLE project_knowledge (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    key TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(project, key)
);
```

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

**Changes**:

- Removed `key` column (no longer needed - one row per project)
- Renamed `summary` → `overview` (semantic clarity)
- Added `rules` column (TEXT, nullable - projects may not have rules initially)
- Changed UNIQUE constraint from `(project, key)` to `project` (one row per project)
- Removed `id` SERIAL (optional - can keep for compatibility or remove)

**Migration Notes**:

- Extract `summary` where `key='overview'` → `overview` column
- One row per project (not one per key)
- `rules` column starts as NULL or empty string

## Data Format

### overview Column

**Type**: TEXT NOT NULL

**Content**: Project overview description (migrated from existing `summary` where `key='overview'`)

**Example**:

```
THN (Tumulty Home Network) is the umbrella project for the entire home-lab and network ecosystem...
```

### rules Column

**Type**: TEXT (nullable)

**Content**: Project-specific rules as numbered list text

**Format Examples**:

```
1. Always provide responses strictly related to THN. Do not incorporate or reference information from other projects.
2. Maintain a privacy-first mindset; emphasize local control and avoid recommending cloud-based solutions.
3. You have access to software projects indexed in the database table `code_index` which contains project source code and documentation. Use all retrieval capabilities possible to provide accurate analysis.
```

Or:

```
1. Rule one text
2. Rule two text
3. Rule three text
```

**Parsing**: Rules are parsed by splitting on numbered patterns (1., 2., etc.) or newlines, then formatted as markdown bullet list in system prompt.

## In-Memory Entities

### System Prompt Composition

**Purpose**: Composed system prompt with project rules

**Structure**:

```python
{
    "base_prompt": str,           # From base_system_prompt.txt
    "project_overview": str,       # From project_knowledge.overview
    "project_rules": List[str],    # Parsed from project_knowledge.rules
    "composed_prompt": str         # Final: base + overview + rules
}
```

**Lifecycle**: Composed on-demand during `build_project_system_prompt()` calls.

## Migration Path

1. **Pre-migration**: Backup existing `project_knowledge` table
2. **Migration**: Create new table structure, migrate overview data
3. **Post-migration**: Update application code to use new structure
4. **Rollback**: Restore old structure if needed

## No Other Schema Changes

- No new tables
- No changes to other tables
- Only `project_knowledge` table modified
