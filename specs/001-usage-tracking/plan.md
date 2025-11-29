# Implementation Plan: OpenAI Usage and Cost Tracking

**Branch**: `001-usage-tracking` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-usage-tracking/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable tracking and display of OpenAI API usage and cost information when users exit the CLI session. Extract usage data (prompt_tokens, completion_tokens, total_tokens) from OpenAI API responses, calculate cost estimates based on model pricing, and display a summary report on exit. Provides transparency into token usage and financial impact for cost management.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: OpenAI Python SDK (existing), standard library (no new dependencies)  
**Storage**: In-memory session tracking (no database changes needed)  
**Testing**: Manual testing with real API calls, verify calculations match expected values  
**Target Platform**: Linux/macOS terminal (CLI)  
**Project Type**: Single project (CLI application)  
**Performance Goals**: Usage summary displays in under 2 seconds (SC-003)  
**Constraints**: Must handle mock mode (zero usage), failed calls (no tracking), and missing usage data gracefully  
**Scale/Scope**: Single user, single session tracking (no persistence across sessions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality ✓
- **Readability First**: Simple usage tracking classes, clear cost calculation functions
- **Minimal Dependencies**: No new dependencies - uses existing OpenAI SDK and standard library
- **Type Hints**: Will add type hints to usage tracking classes and functions
- **Single Responsibility**: Separate classes for UsageRecord, SessionUsageTracker, and cost calculation

### Accuracy ✓
- **Error Handling**: Handle missing usage data, failed API calls, unknown models gracefully
- **Data Validation**: Validate usage data from API responses before tracking
- **State Consistency**: Session state tracked in-memory, no database state changes
- **No Silent Failures**: Clear error messages for missing pricing or usage data

### Rapid Development ✓
- **Pragmatic Over Perfect**: Simple in-memory tracking, no complex persistence
- **Local-First**: Optimized for local CLI session tracking
- **Simple Solutions**: Dictionary-based pricing lookup, simple aggregation
- **Fast Iteration**: Minimal changes to existing code (add tracking to chat.py, display to chat_cli.py)

### Personal Use Context ✓
- **No Multi-Tenancy**: Single user session tracking
- **Trusted Environment**: No need for usage data validation beyond API response structure
- **Direct Configuration**: Pricing can be hardcoded or from simple config
- **Manual Deployment**: Single machine deployment

### Single Machine Deployment ✓
- **No Scalability Concerns**: Single process, in-memory tracking
- **Local Resources**: In-memory session state (no database needed)
- **Simple Networking**: No network calls for tracking (uses existing API responses)
- **Resource Efficiency**: Minimal memory overhead for session tracking

**GATE STATUS**: ✅ PASSED - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-usage-tracking/
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
├── chat.py              # Updated: extract usage data from API response and record in tracker
├── usage_tracker.py     # New: UsageRecord class, SessionUsageTracker class, pricing lookup
└── [other modules]      # No changes needed

chat_cli.py              # Updated: display usage summary on /exit and Ctrl+C
```

**Structure Decision**: Minimal changes to existing single-project structure. Updates:
- `brain_core/usage_tracker.py`: New module for usage tracking infrastructure
- `brain_core/chat.py`: Extract usage from API response and record in session tracker
- `chat_cli.py`: Display usage summary on exit
- No database changes needed - session tracking is in-memory only

## Complexity Tracking

> **No violations identified - all changes align with constitution principles**
