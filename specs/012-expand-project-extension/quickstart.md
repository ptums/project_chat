# Quickstart: Expand Project-Specific Extension with Rules

## Overview

This guide shows how to migrate the `project_knowledge` table to include project-specific rules and update the system prompt to display them.

## Prerequisites

- Python 3.10+ (existing requirement)
- PostgreSQL database with existing `project_knowledge` table
- Existing project_chat installation

## Setup

### Step 1: Backup Database

Before migration, backup the `project_knowledge` table:

```bash
# Backup project_knowledge table
psql -d project_chat -c "\copy project_knowledge TO '/tmp/project_knowledge_backup.csv' CSV HEADER"
```

Or use the backup script:

```bash
python scripts/backup_db.py
```

### Step 2: Run Migration

Run the migration script to update table structure:

```bash
cd /path/to/project_chat
psql -d project_chat -f db/migrations/004_project_knowledge_simplify.sql
```

**What this does**:

- Creates new `project_knowledge` table with `overview` and `rules` columns
- Migrates existing overview data from `summary` where `key='overview'`
- Drops old table structure
- Recreates indexes

### Step 3: Load Seed Data (Optional)

If you want to use the sample seed data with placeholder rules:

```bash
psql -d project_chat -f db/seeds/project_knowledge_seed_v2.sql
```

**Note**: This seed data includes placeholder rules. You should update the `rules` column with actual project-specific rules.

## Usage

### Adding Project Rules

Update rules for a project:

```sql
UPDATE project_knowledge
SET rules = '1. Always provide responses strictly related to THN. Do not incorporate or reference information from other projects.
2. Maintain a privacy-first mindset; emphasize local control and avoid recommending cloud-based solutions.
3. You have access to software projects indexed in the database table `code_index` which contains project source code and documentation. Use all retrieval capabilities possible to provide accurate analysis.'
WHERE project = 'THN';
```

### Formatting Rules

Rules can be formatted as:

- Numbered list: `1. Rule text\n2. Rule text\n3. Rule text`
- Newline-separated: `Rule one\nRule two\nRule three`
- The system will parse and format them as numbered bullets

### Viewing System Prompt

The system prompt will automatically include:

1. Base system prompt (from `base_system_prompt.txt`)
2. Project overview (from `project_knowledge.overview`)
3. Project rules (from `project_knowledge.rules`, formatted as bullet list)

**Example for THN**:

```
[Base system prompt]

In this current conversation is tagged as project THN.

Here's a general overview of the project THN: THN (Tumulty Home Network) is...

---

### Project THN rules:

1. Always provide responses strictly related to THN...
2. Maintain a privacy-first mindset...
3. You have access to software projects indexed...
```

## Testing

### Verify Migration

```sql
-- Check table structure
\d project_knowledge

-- Verify overview data migrated
SELECT project, overview FROM project_knowledge;

-- Check rules column exists
SELECT project, rules FROM project_knowledge;
```

### Test System Prompt

1. Start chat CLI:

   ```bash
   python chat_cli.py
   ```

2. Switch to a project:

   ```
   /thn
   ```

3. Ask about the system prompt or test rule behavior

4. Verify rules are included in the prompt

## Troubleshooting

### Migration Failed

**Symptom**: Migration script errors

**Solution**:

- Check database connection
- Verify backup was created
- Review migration script for syntax errors
- Use rollback script if needed: `psql -d project_chat -f db/migrations/004_project_knowledge_simplify_rollback.sql`

### Overview Data Missing

**Symptom**: No overview in system prompt

**Solution**:

- Verify overview data exists: `SELECT project, overview FROM project_knowledge WHERE project = 'THN';`
- Check migration extracted overview correctly
- Re-run seed data if needed

### Rules Not Appearing

**Symptom**: Rules section missing from prompt

**Solution**:

- Verify rules exist: `SELECT project, rules FROM project_knowledge WHERE project = 'THN';`
- Check rules column is not NULL or empty
- Review rules parsing logic in `_parse_rules_text()`
- Check logs for parsing errors

### Rollback

If you need to revert the migration:

```bash
psql -d project_chat -f db/migrations/004_project_knowledge_simplify_rollback.sql
```

Then restore from backup if needed.

## Next Steps

1. Update rules for each project with actual project-specific rules
2. Test system prompts in all project contexts
3. Verify rules are being followed in conversations
4. Adjust rules format as needed
