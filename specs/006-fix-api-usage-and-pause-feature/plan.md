# Implementation Plan: Fix API Usage Display and Add Pause Feature

**Branch**: `006-fix-api-usage-and-pause-feature` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-fix-api-usage-and-pause-feature/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix bug where API usage summary shows "No API calls made" when calls were actually made, and add pause functionality (`@@`) to stop streaming responses mid-generation. The bug likely occurs because usage tracking happens in streaming mode but may not be properly recorded. The pause feature requires detecting `@@` input during streaming and immediately stopping the response generation.

**Technical Approach**: 
- Investigate why usage tracking fails on exit (likely issue with streaming usage recording)
- Fix usage tracking to ensure all API calls are properly recorded
- Implement pause detection during streaming using non-blocking input or threading
- Save partial responses when paused
- Return user to input prompt immediately after pause

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: openai (OpenAI API), existing `brain_core.usage_tracker` and `brain_core.chat` modules  
**Storage**: N/A (in-memory session tracking)  
**Testing**: Manual testing via CLI  
**Target Platform**: CLI application (Linux/macOS/Windows)  
**Project Type**: Single CLI application  
**Performance Goals**: Pause detection should respond within 100ms, streaming should stop immediately  
**Constraints**: Must work with existing streaming implementation, cannot break current functionality  
**Scale/Scope**: Single-user application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality
- ✅ **Readability First**: Clear pause detection logic, maintainable usage tracking fixes
- ✅ **Type Hints**: Use type hints for new functions
- ✅ **Single Responsibility**: Separate pause detection from streaming display logic

### Accuracy
- ✅ **Error Handling**: Handle edge cases (pause at start, pause after completion, etc.)
- ✅ **State Consistency**: Ensure usage tracking accurately reflects all API calls
- ✅ **No Silent Failures**: Log usage tracking failures, display clear pause feedback

### Rapid Development
- ✅ **Pragmatic Over Perfect**: Simple pause detection using threading or non-blocking input
- ✅ **Simple Solutions**: Reuse existing usage tracker, minimal changes to streaming logic

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
chat_cli.py                  # Main CLI - fix usage display, add pause detection
brain_core/
├── chat.py                 # Streaming logic - ensure usage tracking works
└── usage_tracker.py        # Usage tracking - verify recording works correctly
```

**Structure Decision**: Single CLI application. Changes to existing files:
- `chat_cli.py`: Fix usage display on exit, add pause detection during streaming
- `brain_core/chat.py`: Ensure usage tracking works correctly in streaming mode
- `brain_core/usage_tracker.py`: Verify usage recording logic (likely no changes needed)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
