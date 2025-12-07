# Implementation Plan: Project-Organized Meditation Notes Integration

**Branch**: `001-project-organized-notes` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-project-organized-notes/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable project-scoped meditation note retrieval and conversation saving. The Obsidian notebook repository is organized by project directories (daas, thn, ff, general, 700b). When working in a specific project context, the system should filter notes from the corresponding directory and allow saving conversations back to that directory. Implementation extends the existing MCP server with project filtering logic, directory mapping, and Git-based note saving functionality.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: GitPython (for committing/pushing notes), python-frontmatter (for markdown frontmatter), existing MCP server infrastructure  
**Storage**: Local filesystem (GitLab repository clone), in-memory index (NoteIndex)  
**Testing**: pytest  
**Target Platform**: macOS/Linux (same as existing project_chat)  
**Project Type**: single (extends existing project_chat codebase)  
**Performance Goals**: Filter notes by project directory in <50ms, save conversation as note in <5s  
**Constraints**: Must work with existing project context system, must handle Git operations safely, must preserve Obsidian markdown format  
**Scale/Scope**: 5 project types (DAAS, THN, FF, General, 700B), handle 1000+ notes per project directory, support saving conversations up to 10MB

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Note**: Constitution file contains template placeholders. No specific gates defined yet. Will re-evaluate after Phase 1 design.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-organized-notes/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── note.py           # Note entity (existing - may need project_path field)
│   ├── repository.py     # Repository entity (existing)
│   └── index.py          # NoteIndex entity (existing - may need project filtering)
├── services/
│   ├── git_sync.py       # Git sync service (existing)
│   ├── note_parser.py    # Note parser (existing)
│   ├── index_builder.py  # Index builder (existing)
│   ├── project_filter.py # NEW: Project-based note filtering
│   └── note_saver.py     # NEW: Save conversations as notes
├── mcp/
│   ├── api.py            # MCP API (existing - needs project filtering)
│   ├── resources.py      # Resource handlers (existing - needs project filtering)
│   └── tools.py          # Tool handlers (existing - needs save tool)
└── cli/
    └── main.py           # CLI entry point (optional)

brain_core/
├── context_builder.py    # Existing - needs MCP integration with project filtering
└── chat.py              # Existing - may need conversation saving integration

chat_cli.py               # Existing - needs /mcp save command
```

**Structure Decision**: Single project structure chosen as this extends the existing project_chat codebase. New services (project_filter.py, note_saver.py) added to src/services/, existing MCP components extended with project-aware functionality. Integration points in brain_core/context_builder.py and chat_cli.py.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation             | Why Needed | Simpler Alternative Rejected Because |
| --------------------- | ---------- | ------------------------------------ |
| [None identified yet] |            |                                      |
