# Research: Large Text Input Support

**Feature**: Large Text Input Support  
**Date**: 2025-01-27  
**Status**: Complete

## Research Summary

No critical unknowns identified. Solution uses standard library approaches for reading large text input in Python CLI applications.

## Technical Decisions

### Decision 1: Use sys.stdin for Large Text Reading

**Decision**: Replace line-by-line `input()` reading with `sys.stdin.read()` or chunked reading for large text blocks in `/paste` mode.

**Rationale**:

- `sys.stdin.read()` can read unlimited text (until EOF or specified size)
- Standard library solution - no new dependencies
- Handles large pastes efficiently
- Works with terminal paste operations
- Aligns with constitution principle of "Simple Solutions"

**Alternatives Considered**:

- `prompt_toolkit`: More complex, adds dependency, overkill for this use case
- File-based input: Less convenient, requires file management
- Chunked `input()` reading: Still has potential limits, more complex

### Decision 2: Fix Missing Line Append Bug

**Decision**: Fix the bug in `read_multiline_block()` where `lines.append(line)` is missing before the return statement.

**Rationale**:

- Current code doesn't append the last line before EOF token
- Simple bug fix - add missing line
- Critical for correct functionality

**Alternatives Considered**:

- Rewrite entire function: Unnecessary, bug fix is sufficient

### Decision 3: Use sys.stdin.read() with EOF Detection

**Decision**: For `/paste` mode, read from stdin until EOF (Ctrl+D) or end token, using `sys.stdin.read()` for large blocks.

**Rationale**:

- Handles large pastes efficiently
- Standard approach for reading large text in CLI
- Works with terminal paste operations
- Can detect EOF naturally

**Alternatives Considered**:

- Line-by-line with larger buffer: Still has limits, less efficient
- External file reading: Less convenient for users

### Decision 4: Normal Input Mode Enhancement

**Decision**: For normal input mode, detect if pasted content is large and switch to multiline reading mode automatically, or allow continuation.

**Rationale**:

- Improves user experience - no need to use `/paste` for large normal inputs
- Can detect large pastes by checking if input contains newlines or exceeds typical length
- Maintains backward compatibility

**Alternatives Considered**:

- Always require `/paste` for large text: Less user-friendly
- Auto-detect and prompt: More complex, may interrupt workflow

### Decision 5: Flask Request Size Limits

**Decision**: Increase Flask's `MAX_CONTENT_LENGTH` configuration to allow large text payloads in API requests.

**Rationale**:

- Flask defaults to 16MB which should be sufficient, but may need explicit configuration
- Simple configuration change
- No code changes needed for API endpoint (already accepts text strings)

**Alternatives Considered**:

- Streaming uploads: Over-engineered for text input
- Chunked API requests: More complex, not needed

## Implementation Patterns

### Large Text Reading Pattern

```python
# For /paste mode: Read until EOF or end token
# Use sys.stdin.read() for large blocks
# Handle EOF (Ctrl+D) and end token ("EOF") gracefully
```

### Normal Input Enhancement Pattern

```python
# Detect large pastes in normal input
# If input contains newlines or is very long, treat as multiline
# Or allow continuation input
```

### API Request Handling Pattern

```python
# Configure Flask MAX_CONTENT_LENGTH for large payloads
# JSON parsing handles large strings automatically
# No changes needed to endpoint logic
```

## Dependencies

- **sys.stdin**: Standard library, already available
- **Flask**: Already in use, just needs configuration
- **PostgreSQL TEXT field**: Already supports unlimited text (no schema changes needed)

## No Blocking Issues

All technical decisions are straightforward. No research blockers identified. Ready to proceed with implementation.

## Current Bug Identified

**Critical Bug**: In `read_multiline_block()` function (line 124), the code is missing `lines.append(line)` before checking the end token. This causes the last line before "EOF" to be lost.

**Fix**: Add `lines.append(line)` before the end token check, or restructure to append all lines correctly.
