# Data Model: Large Text Input Support

**Feature**: Large Text Input Support  
**Date**: 2025-01-27

## Overview

This feature does not introduce new database entities. It enhances how text input is captured and processed, but the underlying data model remains unchanged.

## Input Entities

### Text Input

**Purpose**: User-provided text content of variable size.

**Attributes**:

- `content`: String text content (can be very large - 100,000+ characters)
- `size`: Integer character count (for feedback/validation)
- `encoding`: Text encoding (UTF-8 by default)
- `source`: Input method ("paste_mode", "normal_input", "api")

**Behavior**:

- No size limits enforced
- Preserves all characters including newlines, special characters
- Handles UTF-8 encoding
- Can be processed immediately or stored

**State Transitions**:

- Input → Validation → Processing → Storage
- Input → Cancellation → Discard

### Input Mode

**Purpose**: Determines how text is captured from the user.

**Attributes**:

- `mode`: String enum ("paste_mode", "normal_input", "api")
- `end_token`: String token to signal end of input (for paste mode)
- `supports_large_text`: Boolean indicating if mode supports unlimited size

**Behavior**:

- Paste mode: Reads until EOF or end token
- Normal input: Reads single line or detects large paste
- API: Receives JSON payload with text

## Existing Entities (No Changes)

### Messages

- **No schema changes**
- `content` field is TEXT type in PostgreSQL (supports unlimited size)
- Already handles large text correctly once received
- No changes needed to storage layer

### Conversations

- **No schema changes**
- No impact from large text inputs

### Project Knowledge

- **No schema changes**
- No impact from large text inputs

## Data Flow

### CLI Paste Mode

1. User types `/paste` → Enters paste mode
2. System reads from stdin until EOF or "EOF" token
3. Text captured completely (no truncation)
4. Text validated and processed
5. Sent to `chat_turn()` → Stored in database

### CLI Normal Input

1. User types or pastes at normal prompt
2. System detects if input is large (newlines or length)
3. If large, switches to multiline reading or processes as-is
4. Text captured completely
5. Sent to `chat_turn()` → Stored in database

### API Input

1. Client sends POST request with JSON payload
2. Flask receives request (size limit configured)
3. JSON parsed, text extracted from `message` field
4. Text sent to `chat_turn()` → Stored in database

## Validation Rules

### Text Input

- No maximum size limit (practical limit: system memory)
- Must be valid UTF-8 text (no binary data)
- Empty input is rejected (user must provide content)
- Special characters and newlines preserved

### Input Mode

- Paste mode must have clear end signal (EOF or token)
- Normal input should handle both single-line and multiline
- API input must be valid JSON

## Relationships

- **Text Input** → **Messages**: One-to-one (each input becomes one message)
- **Input Mode** → **Text Input**: One-to-many (mode determines how input is captured)

## Performance Considerations

- Large text (100,000+ characters) should be processed efficiently
- Memory usage should be reasonable (streaming not needed for text)
- Database TEXT field handles large content efficiently
- No need for chunking or streaming for text input

## No Schema Changes Required

PostgreSQL TEXT field already supports:

- Unlimited size (up to ~1GB)
- Efficient storage
- No performance degradation for large text
- Proper indexing for search (if needed)

No database migrations or schema changes needed.
