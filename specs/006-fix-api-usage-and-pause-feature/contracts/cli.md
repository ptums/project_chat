# CLI Contracts: Fix API Usage Display and Add Pause Feature

## User Story 1: Fix API Usage Display on Exit

### `/exit` Command (Modified)

**Purpose**: Display accurate API usage summary when user exits.

**Request Flow**:
1. User types `/exit`
2. System saves current conversation (if needed)
3. System calls `display_usage_summary()`
4. System queries `SessionUsageTracker.get_summary()`
5. System displays usage summary with accurate data

**Success Output** (stdout):
```
✓ Indexed: Conversation Title [PROJECT]

======================================================================
Session Usage Summary
======================================================================
Total Prompt Tokens:    1,234
Total Completion Tokens: 2,345
Total Tokens:            3,579
Estimated Cost:         $0.0234
API Calls:              5
Model:                  gpt-4

Bye.
```

**Error Handling**:
- If no API calls were made: Display "No API calls made during this session."
- If usage tracking failed: Display usage summary with available data, log warning
- If tracker is None: Initialize tracker and show zero usage

**Bug Fix Requirements**:
- Ensure usage is recorded from streaming responses (final chunk with `done=True`)
- Verify usage tracking happens even if streaming is interrupted
- Add logging to debug usage tracking issues

---

## User Story 2: Pause Streaming Response with @@

### Pause Detection During Streaming

**Purpose**: Allow user to stop streaming response by typing `@@`.

**Request Flow**:
1. User sends message that triggers streaming response
2. System starts streaming and displays response progressively
3. System starts pause detector thread in background
4. User types `@@` while response is streaming
5. Pause detector thread detects `@@` and sets pause flag
6. Streaming loop checks pause flag and breaks
7. System saves partial response (if any content received)
8. System stops pause detector thread
9. System displays pause message
10. System returns to input prompt

**Success Output** (stdout):
```
You (THN) 🟢: How do I deploy my app?
🟢 Thinking for THN...

AI (THN) 🟢: To deploy your app, you'll need to...
@@
Response paused. Partial response saved.

You (THN) 🟢: 
```

**Pause Detection Logic**:
- Pause detector thread runs only when `is_streaming=True`
- Thread monitors stdin for `@@` input
- Uses `threading.Event` to signal pause to main streaming loop
- Main loop checks pause flag before/after each chunk

**Partial Response Handling**:
- Accumulate response content in `reply` variable during streaming
- When pause detected, save `reply` to database using `save_message()`
- Display message indicating response was paused
- Include character count if partial response was received

**Error Handling**:
- If pause detection fails: Continue streaming normally, log warning
- If partial response save fails: Display error, but continue to input prompt
- If pause thread fails to start: Continue streaming without pause capability

**Edge Cases**:
- User types `@@` before streaming starts: Treated as part of message text
- User types `@@` after streaming completes: Treated as part of next message
- User types `@@` multiple times: Only first detection triggers pause
- Streaming completes before `@@` detected: Normal completion, no pause

---

## Modified Functions

### `display_usage_summary()` in `chat_cli.py`

**Changes**:
- Verify `SessionUsageTracker` is properly initialized
- Ensure usage summary reflects all API calls made
- Add debug logging if usage count is zero but calls were made

**Input**: None (uses global session tracker)

**Output**: Formatted usage summary or "No API calls made" message

---

### `chat_turn()` in `brain_core/chat.py` (Streaming Mode)

**Changes**:
- Ensure usage data is extracted from final chunk with `done=True`
- Verify usage tracking happens even if streaming is interrupted
- Add logging for usage tracking

**Input**: `conversation_id`, `user_text`, `project`, `stream=True`

**Output**: Generator yielding response chunks, then returns full response

**Usage Tracking**:
- Extract usage from final chunk: `chunk.done == True` and `chunk.usage`
- Record usage after streaming completes (or is interrupted)
- Handle case where usage data might not be available

---

### Streaming Display Loop in `chat_cli.py` `main()`

**Changes**:
- Add pause detection thread when streaming starts
- Check pause flag in streaming loop
- Handle pause: save partial response, stop streaming, return to input
- Stop pause detector thread when streaming ends

**Pause Detection Implementation**:
```python
# Pseudo-code
pause_event = threading.Event()
pause_thread = threading.Thread(target=detect_pause, args=(pause_event,), daemon=True)
pause_thread.start()

for chunk in stream_gen:
    if pause_event.is_set():
        break  # Pause detected
    # Display chunk...

pause_thread.join(timeout=0.1)
```

---

## Database Operations

### Save Partial Response

```python
# When pause detected
if reply:  # Partial response received
    save_message(conversation_id, "assistant", reply, meta={
        "model": model,
        "paused": True,
        "partial": True,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    })
```

**Note**: Partial responses are saved with `paused=True` and `partial=True` in metadata for tracking.

---

## Error Scenarios

### Usage Tracking Fails

**Scenario**: Usage data not available or tracking fails

**Handling**:
- Log warning: "Failed to track usage for API call"
- Continue with API call (don't fail)
- Display usage summary with available data on exit
- If no usage tracked, show "No API calls made" (current behavior)

### Pause Detection Fails

**Scenario**: Pause detector thread fails or `@@` not detected

**Handling**:
- Continue streaming normally
- Log warning: "Pause detection failed, continuing streaming"
- Don't interrupt user experience

### Partial Response Save Fails

**Scenario**: Database error when saving partial response

**Handling**:
- Display error: "Failed to save partial response"
- Continue to input prompt (don't block user)
- Log error for debugging

