# Quickstart: Fix Ollama JSON Extraction Bug

**Feature**: 007-fix-ollama-json-extraction  
**Date**: 2025-01-27

## Overview

This feature fixes a bug where Ollama indexing fails when Ollama returns markdown instead of JSON. The fix includes enhanced prompt engineering, improved JSON extraction, fallback generation, and graceful error handling.

## Testing Scenarios

### Scenario 1: Normal JSON Response (Regression Test)

**Purpose**: Verify existing successful flows still work.

**Steps**:
1. Start a conversation in any project
2. Have a few message exchanges
3. Exit using `/exit`
4. Verify indexing succeeds and conversation is saved

**Expected Result**:
- Indexing completes successfully
- Conversation appears in `conversation_index` table
- No errors in logs

---

### Scenario 2: Markdown Response (Primary Bug Fix)

**Purpose**: Verify the fix handles markdown responses correctly.

**Steps**:
1. Start a conversation in any project
2. Have a few message exchanges
3. Manually trigger indexing (or wait for `/exit`)
4. If Ollama returns markdown (simulate or wait for natural occurrence):
   - System should extract JSON from markdown
   - Or generate JSON from markdown structure
   - Indexing should succeed

**Expected Result**:
- Indexing completes successfully (even with markdown response)
- Conversation appears in `conversation_index` table
- Logs show extraction method used (primary or fallback)

**How to Simulate**:
- Temporarily modify `build_index_prompt` to request markdown format
- Or wait for natural occurrence (some models return markdown occasionally)

---

### Scenario 3: Interrupted Conversation (Verification)

**Purpose**: Verify interrupted conversations (Ctrl+C) don't cause indexing issues.

**Steps**:
1. Start a conversation
2. Ask a question that triggers a long response
3. Press Ctrl+C to interrupt the response
4. Continue with a few more messages
5. Exit using `/exit`
6. Verify indexing succeeds

**Expected Result**:
- Indexing completes successfully
- Partial response is handled gracefully
- Conversation is fully indexed

---

### Scenario 4: Complete Extraction Failure (Graceful Degradation)

**Purpose**: Verify system handles complete extraction failure gracefully.

**Steps**:
1. Start a conversation
2. Have a few message exchanges
3. Manually modify Ollama response to be completely unparseable (or wait for natural occurrence)
4. Exit using `/exit`
5. Verify conversation is saved even if indexing fails

**Expected Result**:
- Indexing fails (logs show error)
- Conversation is still saved to database
- User sees message: "Indexing failed, but conversation saved"
- No crash or exception propagation

**How to Simulate**:
- Temporarily break `extract_json_from_text` to always fail
- Or modify Ollama response to be completely unparseable

---

### Scenario 5: Fallback Generation (New Feature)

**Purpose**: Verify fallback JSON generation from markdown works.

**Steps**:
1. Start a conversation
2. Have a few message exchanges
3. Manually trigger indexing with markdown response that contains structured info:
   ```
   **Conversation Information**
   
   * Title: Test Conversation
   * Project: THN
   * Tags: [test, bug-fix]
   * Summary: This is a test conversation
   ```
4. Verify fallback generation creates valid JSON

**Expected Result**:
- Fallback generation extracts fields from markdown
- Valid JSON is generated with all required fields
- Indexing succeeds using generated JSON
- Logs show "Using fallback JSON generation"

---

## Manual Testing Checklist

- [ ] Normal JSON response still works (regression test)
- [ ] Markdown response is handled correctly
- [ ] Interrupted conversations don't cause issues
- [ ] Complete extraction failure doesn't crash system
- [ ] Fallback generation creates valid JSON
- [ ] Error messages are clear and actionable
- [ ] Full Ollama responses are logged (truncated) for debugging
- [ ] Conversations are saved even if indexing fails

## Verification Commands

### Check Indexing Success

```bash
# Check if conversation was indexed
psql -d your_database -c "SELECT title, project FROM conversation_index WHERE conversation_id = 'your-conversation-id';"
```

### Check Error Logs

```bash
# Look for indexing errors
grep "Failed to extract JSON" logs/*.log
grep "Using fallback JSON generation" logs/*.log
```

### Check Conversation Saved

```bash
# Verify conversation exists even if indexing failed
psql -d your_database -c "SELECT id, title, project FROM conversations WHERE id = 'your-conversation-id';"
```

## Expected Behavior Summary

| Scenario | Indexing Result | Conversation Saved | User Message |
|----------|----------------|-------------------|--------------|
| Normal JSON | ✅ Success | ✅ Yes | "✓ Indexed: [title] [project]" |
| Markdown Response | ✅ Success (extracted/generated) | ✅ Yes | "✓ Indexed: [title] [project]" |
| Interrupted Conversation | ✅ Success | ✅ Yes | "✓ Indexed: [title] [project]" |
| Complete Failure | ❌ Failed | ✅ Yes | "⚠ Indexing failed, but conversation saved" |

## Debugging Tips

1. **Check Ollama Response**: Look for `Response text:` in logs to see what Ollama actually returned
2. **Check Extraction Method**: Look for "Using fallback JSON generation" in logs
3. **Check Validation**: If indexing fails, check if required fields are missing
4. **Check Conversation Save**: Verify conversation exists in `conversations` table even if indexing failed

