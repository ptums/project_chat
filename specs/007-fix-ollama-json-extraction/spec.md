# Fix Ollama JSON Extraction Bug

## Problem Statement

When exiting the program using `/exit` (or potentially when interrupting with Ctrl+C), the Ollama indexing function fails because Ollama returns markdown-formatted text instead of JSON. The `extract_json_from_text` function cannot find a JSON object (no `{` character) and raises a `ValueError`, causing the indexing to fail.

### Error Details

```
Failed to extract JSON from Ollama response: No JSON object found in response (no opening brace)

Response text: Here is the structured information extracted from the conversation:

**Conversation Information**

* Title: Building Custom Mattermost Plugin for Canvas Creation
* Project: THN (The Home Network)
* Tags: [mattermost, plugin, canvas]
...
```

The response is pure markdown with no JSON object, causing indexing to fail.

### Root Cause

1. Ollama models sometimes ignore the prompt instruction to "Return ONLY valid JSON, no additional text or markdown formatting"
2. The `extract_json_from_text` function only looks for JSON objects starting with `{` and fails when none is found
3. No fallback mechanism exists to handle non-JSON responses
4. The prompt may not be explicit enough about the required format

## User Stories

### US1: Robust JSON Extraction (P1)

**As a** user  
**I want** conversations to be indexed successfully even when Ollama returns markdown instead of JSON  
**So that** my conversation history is properly organized and searchable

**Acceptance Criteria:**
- When Ollama returns markdown-formatted text, the system extracts or generates valid JSON
- Indexing completes successfully even with non-JSON responses
- Error messages are clear and actionable
- The conversation is saved to the database even if indexing fails (graceful degradation)

### US2: Improved Prompt Engineering (P1)

**As a** system  
**I want** Ollama to consistently return JSON format  
**So that** extraction is reliable and predictable

**Acceptance Criteria:**
- Prompt explicitly requires JSON format using multiple techniques (instruction, example, format parameter if available)
- Prompt includes example JSON structure
- Prompt emphasizes "ONLY JSON" multiple times
- System logs the actual prompt sent for debugging

### US3: Enhanced Error Handling (P2)

**As a** developer  
**I want** better error messages and logging when JSON extraction fails  
**So that** I can diagnose and fix issues quickly

**Acceptance Criteria:**
- Full Ollama response is logged (truncated if very long)
- Error messages indicate what was received vs. what was expected
- System attempts fallback extraction methods before failing
- Clear indication of whether conversation was saved despite indexing failure

### US4: Fallback JSON Generation (P2)

**As a** system  
**I want** to generate valid JSON from markdown responses when extraction fails  
**So that** indexing can still proceed with partial data

**Acceptance Criteria:**
- System parses markdown structure to extract key fields (title, project, tags, etc.)
- Generated JSON includes all required fields with reasonable defaults
- System logs when fallback generation is used
- Generated JSON is validated before use

### US5: Verify Ctrl+C Interruption Impact (P3)

**As a** developer  
**I want** to verify if interrupted conversations (Ctrl+C) cause indexing issues  
**So that** we can handle partial responses appropriately

**Acceptance Criteria:**
- System tests indexing with interrupted conversations
- Partial responses are handled gracefully during indexing
- System identifies if interruption is the root cause of JSON extraction failures

## Technical Requirements

1. **Prompt Enhancement:**
   - Use more explicit JSON format instructions
   - Include example JSON in the prompt
   - Use Ollama's `format` parameter if available (JSON schema)
   - Add system message emphasizing JSON-only output

2. **Extraction Improvements:**
   - Search for JSON in markdown code blocks (```json ... ```)
   - Search for JSON anywhere in the response, not just at the start
   - Handle cases where JSON appears after markdown text
   - Add retry logic with modified prompt if first attempt fails

3. **Fallback Mechanisms:**
   - Parse markdown structure to extract structured data
   - Generate JSON from extracted markdown fields
   - Use conversation metadata (title, project) as fallback values
   - Log fallback usage for monitoring

4. **Error Handling:**
   - Don't fail entire save operation if indexing fails
   - Save conversation to database even if indexing fails
   - Log full response for debugging (with truncation for very long responses)
   - Provide clear error messages to user

5. **Testing:**
   - Test with various Ollama model responses (JSON, markdown, mixed)
   - Test with interrupted conversations
   - Test with very long conversations
   - Test with malformed responses

## Out of Scope

- Changing the Ollama model (we work with whatever model is configured)
- Implementing a different indexing system (we fix the current Ollama-based system)
- Real-time streaming of indexing progress (keep current spinner approach)

