# API Contracts: THN Code RAG Pipeline

**Feature**: 008-thn-code-rag-pipeline  
**Date**: 2025-01-27

## Overview

This document defines the API contracts for functions related to THN code indexing and retrieval. The focus is on internal function interfaces since this is primarily a CLI application.

---

## Code Indexing Functions

### `index_repository(repository_path: str, repository_name: str, production_targets: List[str] = None) -> Dict[str, Any]`

**Purpose**: Index all code files in a repository, generating embeddings and storing in database.

**Input**:
- `repository_path` (str): Local filesystem path to repository root
- `repository_name` (str): Name identifier for the repository
- `production_targets` (List[str], optional): List of production machine names where this code runs

**Output**:
- `Dict[str, Any]`: Statistics about indexing:
  ```python
  {
      "files_processed": 42,
      "chunks_created": 156,
      "embeddings_generated": 156,
      "errors": []
  }
  ```

**Behavior**:
1. Scan repository for code files (Python, shell, config, etc.)
2. Parse files and extract code chunks
3. Generate embeddings for each chunk
4. Store chunks and embeddings in `code_index` table
5. Update repository metadata with last indexed commit
6. Return statistics

**Error Conditions**:
- `ValueError`: If repository_path doesn't exist or isn't a valid repository
- `Exception`: If embedding generation fails (network, API errors)

---

### `parse_code_file(file_path: str, language: str) -> List[Dict[str, Any]]`

**Purpose**: Parse a code file and extract chunks with metadata.

**Input**:
- `file_path` (str): Path to code file
- `language` (str): Programming language (python, bash, yaml, etc.)

**Output**:
- `List[Dict[str, Any]]`: List of code chunks:
  ```python
  [
      {
          "chunk_text": "def configure_router(...):\n    ...",
          "metadata": {
              "function_name": "configure_router",
              "line_start": 45,
              "line_end": 78,
              "docstring": "..."
          }
      },
      ...
  ]
  ```

**Behavior**:
- For Python: Use AST to extract functions and classes
- For shell: Extract function definitions
- For config: Extract key sections
- For other: Use line-based chunking
- Include metadata (function names, line numbers, etc.)

**Error Conditions**:
- `ValueError`: If file_path doesn't exist or language is unsupported
- `SyntaxError`: If code file has syntax errors (log warning, continue with fallback)

---

### `generate_code_embedding(chunk_text: str, metadata: Dict[str, Any]) -> List[float]`

**Purpose**: Generate embedding for a code chunk with context.

**Input**:
- `chunk_text` (str): The code chunk text
- `metadata` (Dict[str, Any]): Chunk metadata (file path, function name, etc.)

**Output**:
- `List[float]`: 1536-dimensional embedding vector

**Behavior**:
1. Combine chunk_text with metadata context (file path, function name)
2. Call `embedding_service.generate_embedding()` with combined text
3. Return embedding vector

**Error Conditions**:
- `Exception`: If embedding generation fails (uses existing embedding_service error handling)

---

## Code Retrieval Functions

### `retrieve_thn_code(query: str, top_k: int = 5, repository_filter: List[str] = None, production_filter: str = None) -> List[Dict[str, Any]]`

**Purpose**: Retrieve relevant code chunks for a query using vector similarity search.

**Input**:
- `query` (str): User query text
- `top_k` (int): Number of top results to return (default: 5)
- `repository_filter` (List[str], optional): Filter by repository names
- `production_filter` (str, optional): Filter by production machine name

**Output**:
- `List[Dict[str, Any]]`: List of code chunks with similarity scores:
  ```python
  [
      {
          "id": "uuid",
          "repository_name": "thn-automation",
          "file_path": "scripts/network_setup.py",
          "language": "python",
          "chunk_text": "def configure_router(...):\n    ...",
          "chunk_metadata": {...},
          "similarity": 0.87,
          "production_targets": ["tumultymedia"]
      },
      ...
  ]
  ```

**Behavior**:
1. Generate embedding for query
2. Perform vector similarity search in `code_index` table
3. Filter by repository and production target if specified
4. Return top-k results ordered by similarity

**Error Conditions**:
- `ValueError`: If query is empty
- `Exception`: If embedding generation or database query fails

---

### `retrieve_code_by_file(file_path: str, repository_name: str = None) -> List[Dict[str, Any]]`

**Purpose**: Retrieve all code chunks from a specific file.

**Input**:
- `file_path` (str): File path pattern (can use wildcards)
- `repository_name` (str, optional): Filter by repository name

**Output**:
- `List[Dict[str, Any]]`: List of code chunks from matching files (same format as `retrieve_thn_code`)

**Behavior**:
1. Query `code_index` table by file_path pattern
2. Filter by repository if specified
3. Return all chunks from matching files

**Error Conditions**:
- `ValueError`: If file_path is empty
- Returns empty list if no matches found (not an error)

---

### `get_thn_code_context(user_message: str, top_k: int = 5) -> str`

**Purpose**: Main retrieval function that formats code chunks as context for LLM prompt.

**Input**:
- `user_message` (str): User's query message
- `top_k` (int): Number of code chunks to retrieve (default: 5)

**Output**:
- `str`: Formatted context string combining retrieved code chunks

**Behavior**:
1. Call `retrieve_thn_code()` to get relevant chunks
2. Format chunks with file paths and metadata
3. Combine into context string for prompt
4. Return formatted context

**Error Conditions**:
- Returns empty string if no code found (caller handles gracefully)

---

## Repository Management Functions

### `clone_repository(repository_url: str, repository_name: str, target_dir: str = "repos") -> str`

**Purpose**: Clone a Git repository into the repos directory.

**Input**:
- `repository_url` (str): Git repository URL (SSH or HTTPS)
- `repository_name` (str): Name identifier for the repository
- `target_dir` (str): Base directory for repositories (default: "repos")

**Output**:
- `str`: Local path to cloned repository

**Behavior**:
1. Create target directory if it doesn't exist
2. Clone repository using GitPython
3. Return local repository path

**Error Conditions**:
- `ValueError`: If repository_url is invalid
- `Exception`: If clone fails (network, authentication, etc.)

---

### `update_repository(repository_path: str) -> bool`

**Purpose**: Update an existing repository (pull latest changes).

**Input**:
- `repository_path` (str): Local path to repository

**Output**:
- `bool`: True if update succeeded, False otherwise

**Behavior**:
1. Check if repository has uncommitted changes (warn if so)
2. Pull latest changes from remote
3. Return success status

**Error Conditions**:
- `ValueError`: If repository_path doesn't exist
- `Exception`: If pull fails (network, conflicts, etc.)

---

## Integration Functions

### `build_thn_context(user_message: str, conversation_context: str = None) -> str`

**Purpose**: Build context string for THN conversations including code retrieval.

**Input**:
- `user_message` (str): User's current message
- `conversation_context` (str, optional): Existing conversation context

**Output**:
- `str`: Combined context string with code snippets and conversation context

**Behavior**:
1. Call `get_thn_code_context()` to retrieve relevant code
2. Combine with conversation context if provided
3. Format for LLM prompt
4. Return combined context

**Error Conditions**:
- Returns context without code if retrieval fails (graceful degradation)

---

## Modified Functions

### `context_builder.build_context()` (MODIFIED)

**Purpose**: Enhanced to support THN code retrieval.

**Changes**:
- Detects when `project == 'THN'`
- Calls `get_thn_code_context()` to retrieve relevant code
- Combines code context with existing conversation context
- Returns enhanced context string

**Behavior**:
- For THN project: Includes code retrieval
- For other projects: Unchanged behavior
- Maintains backward compatibility

---

## Error Handling

All functions should:
- Log errors with appropriate level (error, warning, debug)
- Return None or empty list/string on non-critical errors
- Raise exceptions only for critical failures (network, database connection)
- Provide clear error messages for debugging

---

## Performance Considerations

- **Batch processing**: Process embeddings in batches to respect rate limits
- **Caching**: Consider caching embeddings for unchanged code chunks
- **Incremental updates**: Only re-index changed files
- **Query optimization**: Use database indexes for fast retrieval

