# Implementation Plan: Large Text Input Support

**Branch**: `001-large-text-input` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-large-text-input/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable large text input support in CLI and API by removing character limits and implementing proper input handling for text blocks up to 100,000+ characters. Fixes truncation issues in `/paste` mode and normal input, enabling dream journaling and large code block processing.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Flask, sys.stdin (standard library), existing CLI infrastructure  
**Storage**: PostgreSQL (text stored in messages.content TEXT field - no size limit)  
**Testing**: Manual testing with large text blocks, pytest for unit tests  
**Target Platform**: Linux/macOS terminal (CLI), Flask API server  
**Project Type**: Single project (CLI + API server)  
**Performance Goals**: Process 10,000+ character inputs within 5 seconds, handle 100,000+ characters without memory issues  
**Constraints**: Must preserve all text content, handle special characters and line breaks, maintain existing workflow  
**Scale/Scope**: Single user, local development and production use

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality ✓
- **Readability First**: Simple input reading functions, clear error handling
- **Minimal Dependencies**: Use standard library (sys.stdin) - no new dependencies needed
- **Type Hints**: Will add type hints to input functions
- **Single Responsibility**: Separate functions for large text input handling

### Accuracy ✓
- **Error Handling**: Handle input errors, cancellation, encoding issues
- **Data Validation**: Validate text encoding, handle edge cases
- **State Consistency**: Text input doesn't affect database state until processed
- **No Silent Failures**: Clear error messages for input issues

### Rapid Development ✓
- **Pragmatic Over Perfect**: Use standard library solutions, avoid complex libraries
- **Local-First**: Optimized for local terminal use
- **Simple Solutions**: Read from stdin directly, no complex buffering
- **Fast Iteration**: Minimal changes to existing code

### Personal Use Context ✓
- **No Multi-Tenancy**: Single user input handling
- **Trusted Environment**: No need for input sanitization beyond encoding
- **Direct Configuration**: No configuration needed
- **Manual Deployment**: Single machine deployment

### Single Machine Deployment ✓
- **No Scalability Concerns**: Single process, local input
- **Local Resources**: Terminal/stdin input
- **Simple Networking**: API handles JSON payloads (Flask handles size limits)
- **Resource Efficiency**: Efficient memory usage for large inputs

**GATE STATUS**: ✅ PASSED - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-large-text-input/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
chat_cli.py              # Updated: large text input handling in read_multiline_block() and normal input
api_server.py            # Updated: increase Flask request size limits for large text payloads
brain_core/
├── chat.py              # No changes needed (already handles text strings)
├── db.py                # No changes needed (TEXT field supports large content)
└── [other modules]      # No changes needed
```

**Structure Decision**: Minimal changes to existing single-project structure. Updates:
- `chat_cli.py`: Fix `read_multiline_block()` bug and implement large text reading
- `api_server.py`: Configure Flask to accept larger request payloads
- No new files needed - use standard library solutions

## Complexity Tracking

> **No violations identified - all changes align with constitution principles**
