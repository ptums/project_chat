# Research: Fix Ollama JSON Extraction Bug

## Decision 1: Prompt Engineering for JSON Format

**Question**: How can we make Ollama models consistently return JSON format?

**Findings**:
- Ollama models sometimes ignore simple instructions like "Return ONLY valid JSON"
- More explicit prompts with examples improve compliance
- Using system messages or role-based prompts can help
- Some Ollama models support `format` parameter for structured output (JSON schema)
- Including example JSON in the prompt significantly improves compliance

**Decision**: Use multi-layered prompt approach:
1. Explicit instruction at the start: "You MUST return ONLY valid JSON. No markdown, no explanatory text."
2. Include example JSON structure in the prompt (already done)
3. Add emphasis: "CRITICAL: Your response must start with '{' and end with '}'"
4. Check if Ollama API supports `format` parameter for JSON schema (if available, use it)
5. Add system message if Ollama API supports it

**Rationale**: Multiple reinforcement techniques increase the likelihood of JSON compliance. Example JSON helps models understand the expected structure.

**Alternatives considered**:
- Using a different model: Rejected - we work with whatever model is configured
- Post-processing only: Rejected - better to prevent the issue at the source
- Switching to a different indexing system: Rejected - out of scope

---

## Decision 2: Enhanced JSON Extraction from Markdown

**Question**: How to extract JSON when Ollama returns markdown-formatted text?

**Findings**:
- Current `extract_json_from_text` only looks for `{` at the start
- Markdown responses may contain JSON in code blocks (```json ... ```)
- JSON might appear after markdown text
- Need to search entire response, not just start
- Need to handle nested code blocks

**Decision**: Enhance `extract_json_from_text` to:
1. Search for JSON code blocks first (```json ... ```)
2. If not found, search entire text for `{` character (not just start)
3. Try multiple extraction strategies before failing:
   - Look for ```json code blocks
   - Look for ``` code blocks (might contain JSON)
   - Look for `{` anywhere in text
   - Look for JSON-like structures in markdown lists

**Rationale**: Multiple extraction strategies increase success rate. Searching entire response handles cases where JSON appears after explanatory text.

**Alternatives considered**:
- Only search for code blocks: Rejected - JSON might not be in code blocks
- Only search from start: Rejected - current approach already fails
- Use regex for JSON: Rejected - too fragile, current brace-counting is better

---

## Decision 3: Fallback JSON Generation from Markdown

**Question**: How to generate valid JSON when extraction completely fails?

**Findings**:
- Markdown responses often contain structured information (titles, lists, key-value pairs)
- Can parse markdown to extract key fields:
  - Title: Often in `**Title:**` or `* Title:` format
  - Project: Often in `**Project:**` or `* Project:` format
  - Tags: Often in `**Tags:**` or list format `[tag1, tag2]`
  - Summary: Often in paragraphs after headers
- Can use regex or simple text parsing to extract these fields
- Need to provide reasonable defaults for missing fields

**Decision**: Implement `generate_json_from_markdown` function that:
1. Parses markdown structure to extract key fields:
   - Title: Look for `**Title:**`, `* Title:`, or `Title:` patterns
   - Project: Look for `**Project:**`, `* Project:`, or `Project:` patterns
   - Tags: Look for `**Tags:**` followed by list or `[tag1, tag2]` format
   - Summary: Extract paragraphs after "Summary" headers
2. Generates valid JSON with extracted fields
3. Uses conversation metadata (title, project from DB) as fallback values
4. Provides empty arrays/objects for missing complex fields (key_entities, key_topics)
5. Logs when fallback generation is used

**Rationale**: Allows indexing to proceed even when Ollama doesn't return JSON. Better than failing completely.

**Alternatives considered**:
- Just fail and skip indexing: Rejected - user wants conversations indexed
- Retry with different prompt: Considered - but adds complexity and delay
- Use AI to convert markdown to JSON: Rejected - adds another API call, defeats purpose

---

## Decision 4: Error Handling and Graceful Degradation

**Question**: How should the system behave when JSON extraction fails?

**Findings**:
- Current code raises exception, causing entire save operation to fail
- User wants conversations saved even if indexing fails
- Need to separate indexing failure from conversation save failure
- Should log errors for debugging but not crash

**Decision**: Implement graceful degradation:
1. Try primary extraction (enhanced `extract_json_from_text`)
2. If that fails, try fallback generation (`generate_json_from_markdown`)
3. If that fails, log error but continue:
   - Save conversation to database (this should already work)
   - Log full Ollama response (truncated if >1000 chars) for debugging
   - Display user-friendly error message: "Indexing failed, but conversation saved"
   - Return None or empty dict from `index_session` to indicate failure
4. Don't raise exceptions that prevent conversation save

**Rationale**: User's primary goal is to save conversations. Indexing is a nice-to-have enhancement. Better to save without indexing than fail entirely.

**Alternatives considered**:
- Fail fast: Rejected - user explicitly wants conversations saved
- Retry indexing: Considered - but adds delay, might fail again
- Queue for later indexing: Rejected - adds complexity, out of scope

---

## Decision 5: Ollama Format Parameter Support

**Question**: Does Ollama API support structured output formats (JSON schema)?

**Findings**:
- Ollama API documentation needs to be checked
- Some LLM APIs support `format` parameter (e.g., OpenAI JSON mode)
- Ollama might support similar features in newer versions
- Need to check actual API capabilities

**Decision**: 
1. Check Ollama API documentation for `format` or `json_mode` parameters
2. If supported, add to API call in `generate_with_ollama`
3. If not supported, rely on prompt engineering (Decision 1)
4. Make format parameter optional (don't break if not supported)

**Rationale**: If Ollama supports structured output, use it. Otherwise, fall back to prompt engineering.

**Alternatives considered**:
- Assume format parameter exists: Rejected - might not be supported
- Don't check: Rejected - might miss a useful feature

---

## Decision 6: Testing Interrupted Conversations

**Question**: Do interrupted conversations (Ctrl+C) cause indexing issues?

**Findings**:
- User mentioned this might be related
- Interrupted conversations have partial responses saved
- Partial responses might confuse Ollama during indexing
- Need to verify if this is actually the root cause

**Decision**: 
1. Test indexing with interrupted conversations (simulate Ctrl+C)
2. Check if partial responses in transcript cause markdown responses
3. If yes, handle partial responses gracefully:
   - Mark partial responses in transcript
   - Adjust prompt to handle incomplete conversations
4. Document findings in research

**Rationale**: User specifically asked to verify this. Need to test to confirm or rule out.

**Alternatives considered**:
- Assume it's not related: Rejected - user asked to verify
- Fix without testing: Rejected - might not address root cause

