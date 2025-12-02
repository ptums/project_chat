# Implementation Plan: Refactor Script Organization

**Branch**: `009-refactor-script-organization` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-refactor-script-organization/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Reorganize project scripts and tools into proper directory structure: move utility scripts to `scripts/` directory, create `tools/` directory for audit tools, and update path references for the `repos/` directory that has been moved one level up from the project root.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: Existing project dependencies (no new dependencies required)  
**Storage**: N/A (file system reorganization only)  
**Testing**: Manual verification of file moves and path updates  
**Target Platform**: macOS/Linux (same as existing project)  
**Project Type**: Single project (refactoring existing structure)  
**Performance Goals**: N/A (organizational change only)  
**Constraints**: Must preserve all functionality; ensure imports and path references work after moves; maintain backward compatibility where possible  
**Scale/Scope**: 8 files to move, 2 files to update path references

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Phase 0**: Constitution file contains placeholders, so no blocking gates. This is a simple organizational refactoring with no functional changes.

**Post-Phase 1**:

- ✅ Simple file reorganization with no new dependencies
- ✅ Maintains existing functionality (no breaking changes)
- ✅ Improves project structure (scripts in scripts/, tools in tools/)
- ✅ Updates path references to match new directory layout

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
scripts/                          # MODIFIED - consolidates utility scripts
├── backfill_embeddings.py        # MOVED from root
├── backup_db.py                  # MOVED from root
├── fix_invalid_projects.py       # MOVED from root
├── import_chatgpt_from_zip.py   # MOVED from root
├── reindex_conversations.py      # MOVED from root
├── setup_dev.py                  # MOVED from root
├── setup_prod_conversation_index.py  # MOVED from root
├── index_thn_code.py             # EXISTING - path references updated
└── backfill_thn_embeddings.py    # EXISTING

tools/                            # NEW - directory for audit/maintenance tools
└── audit_conversations.py        # MOVED from root

brain_core/
├── thn_code_indexer.py          # MODIFIED - update repos path references
└── [other existing files]

../repos/                         # EXTERNAL - moved one level up from project root
├── .metadata/
└── [repository directories]
```

**Structure Decision**: Single project structure maintained. Scripts consolidated into `scripts/` directory for better organization. New `tools/` directory separates audit/maintenance tools from utility scripts. Path references updated to reflect new `repos/` location at `../repos/` (one level up from project root).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                      |
