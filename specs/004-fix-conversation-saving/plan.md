# Implementation Plan: Fix Conversation Saving and Project Switching

**Branch**: `004-fix-conversation-saving` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-fix-conversation-saving/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix conversation organization by automatically saving conversations when switching projects or exiting, and making conversation titles mandatory. When users switch projects mid-conversation, save the current conversation and prompt for a new title to create a separate conversation under the new project. This prevents mixing topics from different projects in the same saved conversation.

**Technical Approach**: 
- Create `save_current_conversation()` helper function that calls `index_session()` with error handling
- Modify `handle_command()` to detect project switches and trigger save before switching
- Add title validation loop requiring non-empty input at startup and after project switch
- Create new conversation record when switching projects to ensure proper separation
- Integrate auto-save into `/exit` handler and signal handler for Ctrl+C

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: psycopg2 (PostgreSQL), OpenAI SDK, Ollama client, python-dotenv  
**Storage**: PostgreSQL (conversations, messages, conversation_index tables)  
**Testing**: Manual testing via CLI (pytest optional for unit tests)  
**Target Platform**: CLI application (Linux/macOS/Windows)  
**Project Type**: Single CLI application  
**Performance Goals**: Save operations should complete within 5-10 seconds (Ollama indexing may take longer)  
**Constraints**: Must maintain backward compatibility with existing conversations, preserve existing CLI command behavior  
**Scale/Scope**: Single-user application, handles hundreds of conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality
- ✅ **Readability First**: Changes are straightforward - add auto-save calls and title validation
- ✅ **Type Hints**: Existing codebase uses type hints, will maintain consistency
- ✅ **Single Responsibility**: Each change targets a specific behavior (save on switch, save on exit, title validation)

### Accuracy
- ✅ **Error Handling**: Must handle save failures gracefully during project switch and exit
- ✅ **Data Validation**: Title validation ensures non-empty strings
- ✅ **State Consistency**: New conversation creation on project switch maintains DB consistency

### Rapid Development
- ✅ **Pragmatic Over Perfect**: Simple implementation - call existing `/save` function, add title validation
- ✅ **Simple Solutions**: Reuse existing `index_session()` and `create_conversation()` functions

### Personal Use Context
- ✅ **No Multi-Tenancy**: Single user, no additional complexity needed
- ✅ **Direct Configuration**: No new configuration needed

**GATE STATUS**: ✅ PASS - All constitution checks pass. Implementation is straightforward and follows existing patterns.

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
chat_cli.py                    # Main CLI entry point - modifications for auto-save and title validation
brain_core/
├── db.py                      # Database operations - create_conversation() used for new conversations
├── conversation_indexer.py    # index_session() function used for /save command
└── chat.py                    # normalize_project_tag() used for project validation
```

**Structure Decision**: Single CLI application. Main changes in `chat_cli.py`:
- Add auto-save call before project switch in `handle_command()`
- Add auto-save call in `/exit` handler and signal handler
- Modify title input validation in `main()` to require non-empty input
- Add title prompt and new conversation creation logic after project switch

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
