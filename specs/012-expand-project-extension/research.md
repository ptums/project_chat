# Research Notes: Expand Project-Specific Extension with Rules

## 1. Database Migration Strategy

- **Decision**: Create new migration script `004_project_knowledge_simplify.sql` that:
  1. Creates new table structure with only `project`, `overview`, `rules` columns
  2. Migrates existing overview data from `summary` column where `key='overview'`
  3. Drops old table and renames new table
  4. Recreates indexes
- **Rationale**: Clean migration approach that preserves data and allows rollback. Using table recreation ensures clean schema.
- **Alternatives Considered**:
  - ALTER TABLE to drop columns. Rejected because dropping multiple columns and changing structure is complex and error-prone.
  - Keep old structure and add rules column. Rejected because user explicitly wants simplified structure with only overview and rules.

## 2. Rules Column Format

- **Decision**: Store rules as plain text with numbered list format (e.g., "1. Rule text\n2. Rule text\n3. Rule text"). Parse and format as bullet list in system prompt.
- **Rationale**: Simple text storage, easy to edit, flexible formatting. Can handle multi-line rules.
- **Alternatives Considered**:
  - JSON array storage. Rejected due to unnecessary complexity for simple list.
  - Separate rules table. Rejected because rules are project-specific and should be with overview.

## 3. Rules Parsing and Formatting

- **Decision**: Parse rules text by splitting on numbered patterns (1., 2., etc.) or newlines, then format as markdown bullet list in system prompt.
- **Rationale**: Flexible parsing handles various input formats, markdown bullets are clean and readable.
- **Alternatives Considered**:
  - Require strict format. Rejected because it makes data entry harder.
  - Store pre-formatted markdown. Rejected because it's less flexible for editing.

## 4. Migration Data Preservation

- **Decision**: Extract overview data from existing `summary` column where `key='overview'` and insert into new `overview` column. One row per project (not one per key).
- **Rationale**: Simplifies structure - one row per project with overview and rules. Matches new usage pattern.
- **Alternatives Considered**:
  - Keep key column and migrate all keys. Rejected because user wants only overview and rules.
  - Migrate all summary data. Rejected because only overview is needed.

## 5. System Prompt Format

- **Decision**: Format project extension as:

  ```
  In this current conversation is tagged as project {PROJECT}.

  Here's a general overview of the project {PROJECT}: {overview}

  ---

  ### Project {PROJECT} rules:

  1. {rule 1}
  2. {rule 2}
  ...
  ```

- **Rationale**: Clear structure, markdown formatting, separates overview from rules visually.
- **Alternatives Considered**:
  - Single paragraph format. Rejected because rules need clear separation.
  - Different heading style. Rejected because markdown heading is standard and readable.

## 6. Seed Data Structure

- **Decision**: Create new seed file `project_knowledge_seed_v2.sql` with:
  - One INSERT per project (THN, DAAS, FF, 700B)
  - `overview` column populated from current seed data
  - `rules` column with placeholder structure for user to fill
- **Rationale**: Clean seed data that user can easily edit. References existing overview content.
- **Alternatives Considered**:
  - Update existing seed file. Rejected because we want to preserve old structure during migration.
  - Separate seed files per project. Rejected because single file is easier to manage.

## 7. Rollback Strategy

- **Decision**: Create rollback script that recreates old table structure and attempts to restore data from backup or new structure.
- **Rationale**: Safety net for migration. Allows reverting if issues occur.
- **Alternatives Considered**:
  - No rollback. Rejected because migrations should be reversible.
  - Backup before migration. Accepted as additional safety measure (user can run backup script first).

## 8. Rules Parsing Implementation

- **Decision**: Use simple text parsing:
  1. Split rules text by numbered list patterns (1., 2., etc.) or newlines
  2. Clean each rule (strip whitespace)
  3. Filter empty rules
  4. Format as numbered markdown list
- **Rationale**: Handles various input formats, robust to formatting variations.
- **Alternatives Considered**:
  - Strict format validation. Rejected because it makes data entry harder.
  - Regex-based parsing. Accepted as implementation approach for flexibility.
