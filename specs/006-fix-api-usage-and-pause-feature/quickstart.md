# Quickstart: Fix API Usage Display and Add Pause Feature

## Overview

This feature fixes a bug where API usage summary shows incorrect information on exit, and adds the ability to pause streaming responses by typing `@@`.

## Testing Scenarios

### Test Scenario 1: Verify API Usage Display Fix

**Goal**: Ensure usage summary shows correct data when exiting after making API calls.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Ask a question that generates a response (makes API call)
4. Ask another question (makes another API call)
5. Type `/exit`
6. Verify usage summary shows:
   - Correct API call count (should be 2)
   - Correct token counts (prompt + completion = total)
   - Estimated cost
   - Model used

**Expected Output**:
```
You (THN) 🟢: /exit
✓ Indexed: Conversation Title [THN]

======================================================================
Session Usage Summary
======================================================================
Total Prompt Tokens:    1,234
Total Completion Tokens: 2,345
Total Tokens:            3,579
Estimated Cost:         $0.0234
API Calls:              2
Model:                  gpt-4

Bye.
```

**Verification**:
- ✅ API call count matches number of questions asked
- ✅ Token counts are non-zero
- ✅ Estimated cost is calculated correctly
- ✅ Model name is displayed

---

### Test Scenario 2: Verify No API Calls Message

**Goal**: Ensure "No API calls made" message appears when no calls were made.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Type `/exit` immediately (without asking any questions)
4. Verify message shows "No API calls made during this session."

**Expected Output**:
```
You (GENERAL) 🔵: /exit
✓ Indexed: Conversation Title [general]

No API calls made during this session.

Bye.
```

**Verification**:
- ✅ Message appears when no API calls were made
- ✅ No usage summary table is displayed

---

### Test Scenario 3: Pause Streaming Response

**Goal**: Verify user can pause streaming response by typing `@@`.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Ask a question that will generate a long response (e.g., "Explain quantum computing in detail")
4. While response is streaming, type `@@`
5. Verify:
   - Streaming stops immediately
   - Partial response is saved
   - User is returned to input prompt
   - Can immediately type a new question

**Expected Output**:
```
You (THN) 🟢: Explain quantum computing in detail
🟢 Thinking for THN...

AI (THN) 🟢: Quantum computing is a revolutionary computing paradigm that leverages...
@@
Response paused. Partial response saved.

You (THN) 🟢: 
```

**Verification**:
- ✅ Streaming stops within 1 second of typing `@@`
- ✅ Partial response message is displayed
- ✅ User can immediately type new prompt
- ✅ Partial response is saved to database (check with `/messages <id>`)

---

### Test Scenario 4: @@ in Regular Message (Not During Streaming)

**Goal**: Verify `@@` is treated as regular text when not streaming.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Type a message that includes `@@` (e.g., "My email is user@@example.com")
4. Verify message is sent normally (not treated as pause command)

**Expected Output**:
```
You (THN) 🟢: My email is user@@example.com
🟢 Thinking for THN...

AI (THN) 🟢: [Response about email addresses...]
```

**Verification**:
- ✅ Message with `@@` is sent normally
- ✅ No pause is triggered
- ✅ Response is generated normally

---

### Test Scenario 5: Multiple API Calls and Usage Summary

**Goal**: Verify usage summary aggregates multiple API calls correctly.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Ask 5 different questions (making 5 API calls)
4. Type `/exit`
5. Verify usage summary shows:
   - API Calls: 5
   - Total tokens = sum of all calls
   - Total cost = sum of all call costs

**Expected Output**:
```
======================================================================
Session Usage Summary
======================================================================
Total Prompt Tokens:    5,678
Total Completion Tokens: 12,345
Total Tokens:            18,023
Estimated Cost:         $0.1234
API Calls:              5
Model:                  gpt-4
```

**Verification**:
- ✅ API call count is 5
- ✅ Token totals are sum of all calls
- ✅ Cost is sum of all call costs

---

### Test Scenario 6: Pause at Start of Streaming

**Goal**: Verify pause works even if triggered at the very beginning of streaming.

**Steps**:
1. Start the CLI: `python3 chat_cli.py`
2. Enter a conversation title and select a project
3. Ask a question
4. Immediately type `@@` as soon as response starts streaming
5. Verify:
   - Streaming stops immediately
   - No partial response saved (or minimal content)
   - User can type new prompt

**Expected Output**:
```
You (THN) 🟢: What is Python?
🟢 Thinking for THN...

AI (THN) 🟢: P
@@
Response paused.

You (THN) 🟢: 
```

**Verification**:
- ✅ Pause works even at start of streaming
- ✅ Handles case where minimal/no content received

---

## Implementation Checklist

- [ ] Fix usage tracking in streaming mode to capture usage from final chunk
- [ ] Add logging to debug usage tracking issues
- [ ] Verify usage is recorded even if streaming is interrupted
- [ ] Create pause detector function using threading
- [ ] Implement pause detection thread that monitors stdin for `@@`
- [ ] Add pause flag checking in streaming loop
- [ ] Handle pause: save partial response, stop streaming, return to input
- [ ] Ensure pause detection only active during streaming
- [ ] Test all scenarios above
- [ ] Verify edge cases (pause at start, pause after completion, `@@` in messages)

## Key Functions to Implement

### `chat_cli.py`

1. **`detect_pause(pause_event: threading.Event)`** - Background thread function that monitors stdin for `@@`
2. **Modify streaming loop** - Add pause flag checking and handling
3. **`display_usage_summary()`** - Verify usage tracking works correctly (may need debugging)

### `brain_core/chat.py`

1. **Modify streaming mode** - Ensure usage is captured from final chunk with `done=True`
2. **Add logging** - Log when usage tracking happens and if it fails

## Database Verification

After pausing, verify partial response was saved:

```sql
-- Check partial response was saved
SELECT content, meta_json->>'paused', meta_json->>'partial'
FROM messages
WHERE conversation_id = 'abc-123-def-456'
ORDER BY created_at DESC
LIMIT 1;
```

Expected: `paused=True` and `partial=True` in metadata if response was paused.

