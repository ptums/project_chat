# CLI Input Contract

**Feature**: Large Text Input Support  
**Date**: 2025-01-27

## Overview

This contract defines how the CLI captures and processes large text input from users.

## Input Modes

### Paste Mode (`/paste`)

**Trigger**: User types `/paste`, `/block`, or `/ml` command

**Behavior**:

1. System enters paste mode
2. Displays prompt: "(paste mode) Paste your block now. End with a line containing only EOF"
3. Reads text from stdin until:
   - EOF signal (Ctrl+D on Unix, Ctrl+Z on Windows)
   - Line containing only "EOF" token
   - User cancellation (Ctrl+C)
4. Returns complete text block without truncation

**Input Reading**:

- Uses `sys.stdin.read()` for large text blocks
- No character limit
- Preserves all newlines, special characters, formatting
- Handles UTF-8 encoding

**End Token**:

- Default: "EOF"
- Must be on a line by itself (after stripping whitespace)
- Case-sensitive matching

### Normal Input Mode

**Trigger**: User types or pastes at normal prompt

**Behavior**:

1. System reads input from prompt
2. If input contains newlines or exceeds typical length, treats as multiline
3. Captures complete text without truncation
4. Processes immediately

**Large Text Detection**:

- Input contains newline characters (`\n`)
- Input length exceeds threshold (e.g., 1000 characters)
- Automatic multiline handling

**Input Reading**:

- Uses `input()` for single-line input
- Switches to `sys.stdin.read()` if large paste detected
- No character limit

## Input Validation

### Size Limits

- **No hard limits**: System accepts text of any size
- **Practical limit**: System memory (typically 100MB+ for text)
- **Target support**: 100,000+ characters reliably

### Encoding

- **Required**: UTF-8 text encoding
- **Rejected**: Binary data, invalid UTF-8 sequences
- **Handled**: Special characters, emoji, unicode

### Content Validation

- Empty input rejected (user must provide content)
- Whitespace-only input accepted (may be intentional)
- All text content preserved exactly

## Error Handling

### Input Errors

- **EOF without content**: Returns empty string, shows cancellation message
- **Invalid encoding**: Shows error, allows retry
- **Cancellation (Ctrl+C)**: Gracefully exits input mode, returns to prompt
- **Memory errors**: Shows error message, suggests breaking into smaller chunks

### User Feedback

- **Large input received**: Shows character count or size indicator
- **Processing status**: Shows spinner during processing
- **Success**: Confirms text received and processing started

## Examples

### Example 1: Large Dream Journal Entry

```
User: /paste
System: (paste mode) Paste your block now. End with a line containing only EOF
User: [pastes 5000+ character dream journal entry]
User: EOF
System: Received 5,234 characters. Processing...
```

### Example 2: Large Code Block

```
User: /paste
System: (paste mode) Paste your block now. End with a line containing only EOF
User: [pastes 10,000+ character code block]
User: EOF
System: Received 10,456 characters. Processing...
```

### Example 3: Normal Input with Large Paste

```
User: [pastes large text directly at prompt]
System: Detected large input (2,345 characters). Processing...
```

## Implementation Notes

- Use `sys.stdin` for reading large blocks
- Handle EOF signals properly (Ctrl+D)
- Preserve all text content exactly
- Provide clear user feedback
- Handle cancellation gracefully
