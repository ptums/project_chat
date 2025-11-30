# Research: Fix API Usage Display and Add Pause Feature

**Feature**: 006-fix-api-usage-and-pause-feature  
**Date**: 2025-01-27

## Research Tasks

### 1. API Usage Tracking Bug Investigation

**Question**: Why does the usage summary show "No API calls made" when API calls were actually made?

**Findings**:
- Usage tracking happens in `brain_core/chat.py` after streaming completes (lines 104-117)
- Usage data is extracted from streaming chunks (lines 95-102)
- Usage is only tracked if `total_tokens > 0` (line 105)
- The issue might be:
  1. Usage data not available in streaming chunks (OpenAI may only send usage in final chunk)
  2. Exception during usage tracking that's silently caught
  3. Tracker not properly initialized or reset
  4. Usage tracking happens but tracker is cleared before exit

**Decision**: Investigate streaming usage data availability. OpenAI streaming API typically sends usage data in the final chunk with `done=True`. Need to ensure we capture this final chunk's usage data.

**Rationale**: The bug suggests usage tracking is failing silently. Need to verify usage data is actually available and being captured correctly.

**Alternatives considered**:
- Assume usage is always available: Rejected - need to verify actual behavior
- Add fallback to estimate usage: Rejected - should use actual API data

---

### 2. Streaming Usage Data Availability

**Question**: When does OpenAI streaming API provide usage data in chunks?

**Findings**:
- OpenAI streaming API sends usage data in the final chunk when `done=True`
- Usage data may not be available in intermediate chunks
- The current code checks `hasattr(chunk, 'usage')` but usage might only be in final chunk
- Need to ensure we're checking the final chunk properly

**Decision**: Modify streaming code to explicitly check for final chunk with `done=True` and extract usage from that chunk. Also add logging to verify usage data is being received.

**Rationale**: If usage is only in the final chunk, we need to ensure we're capturing it. Current code might be missing it if the final chunk isn't properly handled.

**Alternatives considered**:
- Estimate usage from response length: Rejected - should use actual API data
- Track usage separately: Rejected - API provides accurate data

---

### 3. Pause Detection During Streaming

**Question**: How to detect `@@` input while streaming response is being displayed?

**Findings**:
- Streaming is blocking - we're in a loop writing characters
- `input()` is blocking and won't work during streaming
- Need non-blocking input detection
- Options:
  1. Use threading with a separate thread monitoring input
  2. Use `select`/`poll` for non-blocking stdin (Unix only)
  3. Use `msvcrt` for Windows or `termios` for Unix
  4. Use `keyboard` library (cross-platform but requires installation)

**Decision**: Use threading approach:
- Create a background thread that monitors stdin for `@@`
- Use a shared flag/event to signal pause
- Main streaming loop checks the flag periodically
- When `@@` detected, set flag and break from streaming loop

**Rationale**: Threading is simple, cross-platform, and doesn't require additional dependencies. The existing codebase already uses threading for spinners, so this fits the pattern.

**Alternatives considered**:
- `keyboard` library: Rejected - requires new dependency
- Platform-specific solutions (`msvcrt`/`termios`): Rejected - not cross-platform
- Polling stdin with `select`: Considered - but threading is simpler and already used

---

### 4. Partial Response Saving on Pause

**Question**: How to save partial response when streaming is paused?

**Findings**:
- Current code accumulates `reply` variable during streaming (line 1049 in chat_cli.py)
- When pause is detected, we have partial content in `reply`
- Need to save this partial response to database
- Similar to existing KeyboardInterrupt handling (lines 1052-1059)

**Decision**: When pause is detected:
1. Break from streaming loop
2. Save accumulated `reply` content to database using `save_message()`
3. Display message indicating response was paused
4. Return to input prompt

**Rationale**: Reuse existing partial response saving logic. This is already handled for KeyboardInterrupt, so we can follow the same pattern.

**Alternatives considered**:
- Discard partial response: Rejected - user might want to see what was generated
- Wait for full response: Rejected - defeats purpose of pause

---

### 5. Pause Command Detection Logic

**Question**: How to distinguish `@@` as pause command vs regular text in messages?

**Findings**:
- `@@` should only trigger pause during active streaming
- If user types `@@` in a regular message (not during streaming), it should be treated as text
- Need to track streaming state
- Pause detection should only be active when streaming is in progress

**Decision**: 
- Only enable pause detection thread when streaming is active
- When streaming starts, start pause detection thread
- When streaming ends (normally or paused), stop pause detection thread
- If `@@` is typed when not streaming, it's part of the message text

**Rationale**: Clear separation between streaming state and normal input. Prevents false positives where `@@` in a message would trigger pause.

**Alternatives considered**:
- Always monitor for `@@`: Rejected - would interfere with normal messages
- Use different command: Considered - but `@@` is simple and unlikely in normal text

---

### 6. Threading Implementation for Pause Detection

**Question**: How to implement threading for pause detection without blocking streaming?

**Findings**:
- Python `threading` module is available (already used for spinners)
- Need to use `threading.Thread` with daemon=True
- Use `threading.Event` or shared flag for communication
- Main streaming loop checks flag periodically (every chunk or character)

**Decision**: 
- Create `PauseDetector` class or function that runs in background thread
- Thread reads from stdin using `input()` (will block until input received)
- When `@@` detected, set shared event/flag
- Main streaming loop checks flag before/after each chunk
- When flag is set, break from loop and handle pause

**Rationale**: Simple threading pattern, already used in codebase. Event-based communication is clean and thread-safe.

**Alternatives considered**:
- Queue-based communication: Considered - but Event is simpler for boolean flag
- Lock-based communication: Rejected - Event is more appropriate for this use case

---

## Technical Decisions Summary

1. **Usage Tracking Fix**: Ensure final chunk with `done=True` is properly handled to extract usage data
2. **Pause Detection**: Use threading with background thread monitoring stdin for `@@`
3. **Partial Response Saving**: Reuse existing partial response saving logic (similar to KeyboardInterrupt)
4. **Pause Command Scope**: Only active during streaming, treat as text otherwise
5. **Threading Pattern**: Use `threading.Event` for communication between pause detector and streaming loop

## Implementation Approach

1. **Fix Usage Tracking**:
   - Verify usage data is captured from final streaming chunk
   - Add logging to debug usage tracking
   - Ensure usage is recorded even if streaming is interrupted
   - Test with actual API calls to verify tracking works

2. **Implement Pause Feature**:
   - Create pause detection function/class using threading
   - Start pause detection thread when streaming begins
   - Check pause flag in streaming loop
   - Handle pause: save partial response, stop streaming, return to input
   - Stop pause detection thread when streaming ends

## No Unresolved Clarifications

All technical questions have been resolved. Implementation can proceed to Phase 1 design.

