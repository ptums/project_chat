# Implementation Plan: Fix Ollama JSON Extraction Bug

**Branch**: `007-fix-ollama-json-extraction` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-fix-ollama-json-extraction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix the bug where Ollama indexing fails when Ollama returns markdown-formatted text instead of JSON. The issue occurs when exiting the program (`/exit`) and potentially when interrupting conversations with Ctrl+C. The solution involves: (1) improving the prompt to be more explicit about JSON format requirements, (2) enhancing the JSON extraction function to handle markdown responses, (3) adding fallback mechanisms to generate JSON from markdown when extraction fails, and (4) improving error handling to ensure conversations are saved even if indexing fails.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: `requests` (for Ollama API), `json` (standard library), existing `brain_core.ollama_client` and `brain_core.conversation_indexer` modules  
**Storage**: PostgreSQL (existing `conversation_index` table), in-memory processing for JSON extraction  
**Testing**: Manual testing with various Ollama responses (JSON, markdown, mixed formats)  
**Target Platform**: macOS/Linux (same as existing project)  
**Project Type**: Single project (CLI application)  
**Performance Goals**: JSON extraction completes in <100ms; fallback generation in <500ms; indexing timeout remains at current OLLAMA_TIMEOUT (60s default)  
**Constraints**: Must not break existing successful indexing flows; must maintain backward compatibility with current JSON responses; must handle partial/interrupted conversations gracefully  
**Scale/Scope**: Single user, local deployment; handles conversations with 10-1000 messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality ✓
- **Readability First**: JSON extraction logic will be well-documented with clear error messages
- **Minimal Dependencies**: Uses existing dependencies (`requests`, `json` standard library)
- **Type Hints**: Will add type hints to enhanced extraction functions
- **Single Responsibility**: Extraction, fallback generation, and error handling will be separate functions

### Accuracy ✓
- **Error Handling**: Will gracefully handle non-JSON responses without crashing
- **Data Validation**: Will validate extracted/generated JSON before use
- **State Consistency**: Conversations will be saved even if indexing fails (graceful degradation)

### Maintainability ✓
- **Clear Error Messages**: Will log full Ollama responses (truncated) for debugging
- **Fallback Mechanisms**: Will provide multiple extraction strategies before failing
- **Logging**: Will log when fallback mechanisms are used for monitoring

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
brain_core/
├── conversation_indexer.py    # Main file to modify (extract_json_from_text, build_index_prompt, index_session)
├── ollama_client.py           # May need to check/add format parameter support
└── db.py                      # Used by index_session (no changes needed)

chat_cli.py                    # Calls save_current_conversation which calls index_session (no changes needed)
```

**Structure Decision**: Single project structure. This is a bug fix in existing modules (`brain_core/conversation_indexer.py` and potentially `brain_core/ollama_client.py`). No new files needed, only modifications to existing extraction and prompt functions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
