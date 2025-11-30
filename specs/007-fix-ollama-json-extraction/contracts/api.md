# API Contracts: Fix Ollama JSON Extraction Bug

## Overview

This feature fixes a bug in the conversation indexing system. No new API endpoints are introduced. The contracts describe the internal function interfaces that are modified.

## Modified Functions

### `extract_json_from_text(text: str) -> str`

**Purpose**: Extract JSON object from text that may contain explanatory text or markdown.

**Changes**:
- Enhanced to search for JSON in markdown code blocks (```json ... ```)
- Enhanced to search entire text for `{` character (not just start)
- Multiple extraction strategies before failing

**Input**:
- `text` (str): Text that may contain JSON mixed with other text

**Output**:
- `str`: Extracted JSON string with comments removed

**Errors**:
- `ValueError`: If no valid JSON object is found (after all strategies)

**Behavior**:
1. Remove markdown code blocks if present (```json ... ``` or ``` ... ```)
2. Search for JSON code blocks first
3. If not found, search entire text for `{` character
4. Extract JSON by counting braces
5. Remove JSON comments (// and /* */)
6. Return cleaned JSON string

---

### `build_index_prompt(transcript: str) -> str`

**Purpose**: Build the prompt for Ollama to organize a conversation.

**Changes**:
- Enhanced with more explicit JSON format instructions
- Multiple emphasis points about JSON-only output
- Clearer example structure

**Input**:
- `transcript` (str): Full conversation transcript from `build_transcript()`

**Output**:
- `str`: Prompt string instructing Ollama to return structured JSON

**Behavior**:
1. Include explicit instruction: "You MUST return ONLY valid JSON"
2. Include example JSON structure (existing)
3. Add emphasis: "CRITICAL: Your response must start with '{' and end with '}'"
4. Include warning: "No markdown, no explanatory text, ONLY JSON"

---

### `generate_json_from_markdown(markdown_text: str, conversation_metadata: dict) -> dict`

**Purpose**: Generate valid JSON from markdown-formatted Ollama response when extraction fails.

**New Function**

**Input**:
- `markdown_text` (str): Markdown-formatted response from Ollama
- `conversation_metadata` (dict): Conversation metadata from database with keys:
  - `title` (str): Conversation title
  - `project` (str): Conversation project

**Output**:
- `dict`: Valid JSON object with all required fields

**Errors**:
- None (always returns valid dict with defaults if parsing fails)

**Behavior**:
1. Parse markdown to extract key fields:
   - Title: Look for `**Title:**`, `* Title:`, or `Title:` patterns
   - Project: Look for `**Project:**`, `* Project:`, or `Project:` patterns
   - Tags: Look for `**Tags:**` followed by list or `[tag1, tag2]` format
   - Summary: Extract paragraphs after "Summary" headers
2. Generate valid JSON with extracted fields
3. Use `conversation_metadata` as fallback for missing fields
4. Provide empty arrays/objects for missing complex fields
5. Return complete JSON object with all required fields

---

### `index_session(session_id, model=None, version=None, override_project=None, preserve_project=False) -> Dict[str, Any]`

**Purpose**: Index a conversation session using Ollama.

**Changes**:
- Enhanced error handling with fallback mechanisms
- Graceful degradation when indexing fails
- Better logging of failures

**Input**:
- `session_id` (UUID | str): UUID of the conversation session
- `model` (str, optional): Ollama model to use
- `version` (int, optional): Index version number
- `override_project` (str, optional): Override project classification
- `preserve_project` (bool): If True, don't let Ollama override conversation's project

**Output**:
- `Dict[str, Any]`: Indexed data (title, project, tags, etc.) or None if indexing fails

**Errors**:
- `OllamaError`: If Ollama API call fails (network, timeout, etc.)
- `ValueError`: If conversation not found or no messages

**Behavior**:
1. Load conversation and messages from database
2. Build transcript and prompt
3. Call Ollama API
4. Try primary extraction (`extract_json_from_text`)
5. If extraction fails, try fallback generation (`generate_json_from_markdown`)
6. If all methods fail:
   - Log error with full response (truncated)
   - Return None (don't raise exception)
   - Allow conversation save to proceed
7. If JSON successfully extracted/generated:
   - Validate required fields
   - Upsert into `conversation_index` table
   - Return indexed data

---

### `generate_with_ollama(model: str, prompt: str, base_url: Optional[str] = None, timeout: int = 60) -> str`

**Purpose**: Generate text completion using Ollama API.

**Potential Changes**:
- May add `format` parameter if Ollama API supports JSON schema

**Input**:
- `model` (str): Ollama model name
- `prompt` (str): Input prompt text
- `base_url` (str, optional): Ollama base URL
- `timeout` (int): Request timeout in seconds

**Output**:
- `str`: Generated text response from Ollama

**Errors**:
- `OllamaError`: If API call fails

**Behavior** (if format parameter added):
1. Check if Ollama API supports `format` parameter
2. If supported, add `"format": "json"` to payload
3. Otherwise, use existing behavior (prompt engineering only)

