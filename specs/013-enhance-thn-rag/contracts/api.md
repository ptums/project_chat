# API Contracts: Enhance THN RAG System

## Function Contracts

### 1. `build_thn_rag_context(user_message: str) -> Dict[str, Any]`

**Location**: `brain_core/context_builder.py`

**Purpose**: Build new RAG context for THN project with History & Context and Relevant Code Snippets sections.

**Parameters**:

- `user_message` (str): Current user message for code similarity search

**Returns**:

```python
{
    "context": str,  # Formatted RAG string with both sections (no wrapper text)
    "notes": List[str]  # List of source notes for debugging/tracking
}
```

**Behavior**:

1. Query `conversation_index` for last 5 THN conversations (ordered by `indexed_at DESC`)
2. Query `code_index` for top 5 relevant code chunks (vector similarity search)
3. Format conversations into "History & Context: Last 5 Conversations" section
4. Format code chunks into "Relevant Code Snippets" section
5. Combine sections into single context string (no wrapper/intro text)
6. Return context dict with notes

**Note**: The function returns only the RAG content (History & Context + Relevant Code Snippets sections). The wrapper text is added in `chat.py` when building system messages.

**Error Handling**:

- If database error: Log error, return `{"context": "", "notes": []}`
- If no conversations: Include empty History section or omit
- If no code: Include empty Code Snippets section or omit
- If embedding generation fails: Skip code retrieval, return conversation-only RAG

**Example Return**:

```python
{
    "context": "### History & Context: Last 5 Conversations\n\n- **Title:** THN Network Setup\n...\n\n### Relevant Code Snippets\n\n**File:** brain_core/context_builder.py\n...",
    "notes": [
        "Retrieved 5 conversations from conversation_index",
        "Retrieved 5 code chunks via vector similarity search"
    ]
}
```

---

### 2. `_format_conversation_entry(row: Tuple) -> str`

**Location**: `brain_core/context_builder.py` (private helper)

**Purpose**: Format a single conversation_index row into RAG format.

**Parameters**:

- `row` (Tuple): Database row from conversation_index query

**Returns**:

- `str`: Formatted conversation entry string

**Behavior**:

1. Extract fields: title, tags, key_entities, summary_detailed, memory_snippet
2. Format tags/key_entities as comma-separated strings (handle JSONB)
3. Truncate summary_detailed to 500 chars if longer
4. Truncate memory_snippet to 300 chars if longer
5. Format as markdown list item with all available fields

**Error Handling**:

- Handle NULL fields gracefully (omit field if NULL)
- Handle JSONB parsing errors (fallback to empty string)

**Example Output**:

```
- **Title:** THN Network Setup
- **Tags:** networking, vlan, firewall
- **Key Entities:** Firewalla, Mac Mini
- **Summary:** Long summary text... (truncated)
- **Memory Snippet:** Memory text... (truncated)
```

---

### 3. `_format_code_snippet(chunk: Dict[str, Any]) -> str`

**Location**: `brain_core/context_builder.py` (private helper)

**Purpose**: Format a single code_index chunk into RAG format.

**Parameters**:

- `chunk` (Dict[str, Any]): Code chunk dict from retrieval

**Returns**:

- `str`: Formatted code snippet string

**Behavior**:

1. Extract file_path, language, chunk_text, chunk_metadata
2. Generate brief_description from metadata (function_name/class_name) or file path
3. Truncate chunk_text to 1000 chars if longer
4. Format as markdown with file, language, description, and code block

**Error Handling**:

- Handle missing metadata gracefully (use file path for description)
- Handle NULL fields (use defaults)

**Example Output**:

````
**File:** brain_core/context_builder.py
**Language:** python
**Description:** build_project_context
```python
def build_project_context(...):
    ...
````

````

---

### 4. `_retrieve_thn_conversations(limit: int = 5) -> List[Tuple]`

**Location**: `brain_core/context_builder.py` (private helper)

**Purpose**: Query conversation_index for last N THN conversations.

**Parameters**:
- `limit` (int): Number of conversations to retrieve (default: 5)

**Returns**:
- `List[Tuple]`: List of database rows

**Behavior**:
1. Query `conversation_index` WHERE `project = 'THN'`
2. ORDER BY `indexed_at DESC`
3. LIMIT to `limit`
4. Return rows

**Error Handling**:
- If database error: Log error, return empty list
- If no rows: Return empty list

---

### 5. `_retrieve_thn_code(user_message: str, top_k: int = 5) -> List[Dict[str, Any]]`

**Location**: `brain_core/context_builder.py` (private helper)

**Purpose**: Query code_index for top K relevant code chunks using vector similarity.

**Parameters**:
- `user_message` (str): User query for similarity search
- `top_k` (int): Number of code chunks to retrieve (default: 5)

**Returns**:
- `List[Dict[str, Any]]`: List of code chunk dicts

**Behavior**:
1. Generate embedding for user_message
2. Query `code_index` WHERE `embedding IS NOT NULL`
3. ORDER BY `embedding <=> query_embedding::vector`
4. LIMIT to `top_k`
5. Return list of chunk dicts

**Error Handling**:
- If embedding generation fails: Log error, return empty list
- If database error: Log error, return empty list
- If no rows: Return empty list

**Note**: May reuse existing `retrieve_thn_code()` from `thn_code_retrieval.py` or implement inline.

---

## Integration Points

### Modified Function: `build_project_context()`

**Location**: `brain_core/context_builder.py`

**Changes**:
- Replace THN-specific block (lines 489-562) with call to `build_thn_rag_context()`
- Maintain function signature: `build_project_context(project: str, user_message: str, ...) -> Dict[str, Any]`
- For THN project: Call `build_thn_rag_context(user_message)` and return result
- For other projects: Keep existing logic unchanged

**Example**:
```python
# THN-specific retrieval: new RAG format
if project == 'THN':
    try:
        return build_thn_rag_context(user_message)
    except Exception as e:
        logger.error(f"THN RAG generation failed: {e}")
        # Fall through to default behavior
```

### Message Ordering in `chat.py`

**Location**: `brain_core/chat.py`

**Current Message Order** (lines 54-100):
1. System prompt (base + project extension with overview/rules) - `build_project_system_prompt()`
2. Project context from RAG - `build_project_context()` output (this is where THN RAG appears)
3. Existing project context (from memory.py)
4. Note reads
5. Conversation messages

**Requirement**: THN RAG must appear **after** the project_knowledge section (overview and rules) which is in the first system message. The RAG is included in the second system message, maintaining this order.

**Wrapper Text Update**: The wrapper text in `chat.py` (lines 67-72) should be updated to be more concise. Current text:
```python
f"We're working on project {project} together. "
f"Here's relevant context from prior conversations and notes:\n\n"
```

**Recommended replacement**: Remove wrapper text entirely and let RAG sections speak for themselves, or use a concise one-liner like:
```python
f"Context from THN project history and codebase:\n\n"
```

The RAG content itself (History & Context + Relevant Code Snippets sections) is self-explanatory and doesn't need verbose introduction.`

---

## Testing Contracts

### Unit Tests

1. **`test_build_thn_rag_context()`**:

   - Test with 5 conversations and 5 code chunks
   - Test with empty results (no conversations, no code)
   - Test with partial results (some conversations, no code)
   - Test truncation of long fields
   - Test NULL field handling

2. **`test_format_conversation_entry()`**:

   - Test with all fields present
   - Test with NULL fields
   - Test JSONB array formatting
   - Test truncation

3. **`test_format_code_snippet()`**:

   - Test with metadata (function_name)
   - Test without metadata (use file path)
   - Test truncation of chunk_text

4. **`test_retrieve_thn_conversations()`**:

   - Test query execution
   - Test limit parameter
   - Test empty result handling

5. **`test_retrieve_thn_code()`**:
   - Test vector similarity search
   - Test embedding generation
   - Test empty result handling

### Integration Tests

1. **End-to-end RAG generation**:

   - Test full flow from `build_project_context()` → RAG generation → formatted output
   - Verify RAG appears in chat system messages
   - Verify performance (<500ms)

2. **Database integration**:
   - Test with real database queries
   - Test with various data states (NULL fields, empty tables, etc.)
````
