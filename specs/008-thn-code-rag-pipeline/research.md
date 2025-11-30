# Research: THN Code RAG Pipeline Enhancement

## Code File Parsing Strategy

### Decision: Parse code files by language type with syntax-aware chunking

**Rationale**:
- Different languages have different structures (functions, classes, modules)
- Syntax-aware chunking preserves code context better than fixed-size chunks
- Can extract meaningful code units (functions, classes) for better retrieval
- Handles comments and documentation within code files

**Alternatives Considered**:
- **Fixed-size chunking**: Simple but breaks code context (functions split across chunks)
- **Line-based chunking**: Better than fixed-size but still breaks context
- **File-level embedding**: Too large for some files, loses granularity
- **AST-based parsing**: More complex, requires language-specific parsers

**Implementation Notes**:
- Support Python, shell scripts, config files (YAML, JSON, TOML), and plain text
- For Python: Extract functions and classes as chunks
- For shell scripts: Extract functions and script sections
- For config files: Extract key-value pairs or sections
- Fallback to line-based chunking for unsupported languages
- Include file path and language metadata with each chunk

---

## Code Chunking Strategy

### Decision: Use overlapping chunks with function/class boundaries as primary units

**Rationale**:
- Function/class boundaries provide natural code units
- Overlapping chunks (e.g., 50 lines overlap) preserve context across boundaries
- Better retrieval when query spans multiple functions
- Handles large files by breaking into manageable chunks

**Alternatives Considered**:
- **No overlap**: Simpler but loses context at boundaries
- **Fixed-size chunks only**: Breaks code structure
- **Single embedding per file**: Too coarse-grained for large files

**Implementation Notes**:
- Primary chunk: Function or class (with docstring if present)
- Secondary chunk: Overlapping sections (e.g., function + surrounding context)
- Maximum chunk size: ~1000 tokens (OpenAI embedding limit is 8191, but smaller chunks are more precise)
- Include chunk metadata: file_path, language, function/class name, line numbers

---

## Repository Management

### Decision: Use GitPython for repository cloning and management

**Rationale**:
- Python-native library for Git operations
- Supports cloning, pulling, and tracking repository state
- Can detect changes between indexing runs
- Handles authentication and SSH keys
- Well-documented and maintained

**Alternatives Considered**:
- **Subprocess calls to git**: More error-prone, harder to handle edge cases
- **Manual git commands**: Requires user to clone manually (less automated)
- **GitHub API**: Only works for GitHub, adds API dependency

**Implementation Notes**:
- Clone repositories into `repos/` directory
- Track repository metadata: name, URL, branch, last indexed commit
- Support incremental updates (only index changed files)
- Handle repository errors gracefully (permission issues, network problems)

---

## Code Metadata Storage

### Decision: Store code chunks in new `code_index` table with pgvector embeddings

**Rationale**:
- Separate table keeps code indexing separate from conversation indexing
- Can track file-level and chunk-level metadata
- Supports filtering by repository, language, file path
- Follows DAAS pattern but adapted for code

**Alternatives Considered**:
- **Store in conversation_index**: Would mix code and conversations, harder to manage
- **File-based storage**: No database benefits (search, filtering, relationships)
- **External vector DB**: Adds complexity, existing pgvector infrastructure works

**Implementation Notes**:
- Table schema: `code_index` with columns:
  - `id` (UUID, PK)
  - `repository_name` (TEXT)
  - `file_path` (TEXT)
  - `language` (TEXT)
  - `chunk_text` (TEXT)
  - `chunk_metadata` (JSONB) - function name, line numbers, etc.
  - `embedding` (vector(1536))
  - `indexed_at` (TIMESTAMPTZ)
  - `production_targets` (TEXT[]) - which machines this code runs on
- Index on `embedding` using pgvector for similarity search
- Index on `repository_name` and `language` for filtering

---

## Production Environment Mapping

### Decision: Use metadata field to associate code with production machines

**Rationale**:
- Flexible: Can map files to multiple machines
- Extensible: Easy to add new machines or change mappings
- Queryable: Can filter by production target
- Doesn't require separate table (keeps schema simple)

**Alternatives Considered**:
- **Separate mapping table**: More normalized but requires joins
- **File path conventions**: Less flexible, harder to maintain
- **Configuration file**: Requires manual maintenance, not queryable

**Implementation Notes**:
- Store production targets as array: `production_targets TEXT[]`
- Examples: `['tumultymedia']`, `['tumultymedia', 'tumultymedia2']`
- Can filter retrieval by production target when relevant
- Default: empty array (code not yet deployed)
- Can be updated when deployment information is known

---

## Code Retrieval Integration

### Decision: Integrate THN code retrieval into context_builder.py following DAAS pattern

**Rationale**:
- Consistent with existing DAAS RAG implementation
- Reuses existing context building infrastructure
- Easy to enable/disable per project
- Maintains separation of concerns

**Alternatives Considered**:
- **Separate retrieval in chat.py**: Would duplicate context building logic
- **New context builder**: Unnecessary complexity, existing one works
- **Inline retrieval**: Breaks separation of concerns

**Implementation Notes**:
- Modify `context_builder.py` to detect THN project context
- Call `thn_code_retrieval.py` functions when `project == 'THN'`
- Combine retrieved code snippets with existing context
- Restrict to THN codebase by default (filter by repository_name or project tag)
- Allow cross-project references when explicitly requested

---

## File Type Support

### Decision: Support Python, shell scripts, and common config formats initially

**Rationale**:
- Covers most THN networking code (Python scripts, shell automation, configs)
- Can be extended later for other languages
- Focuses on most common use cases first
- Keeps initial implementation manageable

**Alternatives Considered**:
- **Support all languages**: Too broad, requires many parsers
- **Only Python**: Too restrictive for networking scripts
- **Plain text only**: Loses code structure benefits

**Implementation Notes**:
- Python: Use AST parsing for functions/classes
- Shell (bash/sh): Extract function definitions
- Config files: YAML, JSON, TOML - extract key sections
- Plain text: Line-based chunking
- Extensible: Can add language parsers incrementally

---

## Embedding Generation Performance

### Decision: Batch code chunks for embedding generation with rate limit handling

**Rationale**:
- OpenAI rate limits: 3000 requests/minute for embeddings
- Large codebases may have hundreds of chunks
- Batching with delays prevents rate limit issues
- Can process incrementally (only new/changed files)

**Alternatives Considered**:
- **Sequential processing**: Too slow for large codebases
- **Aggressive parallelization**: Risk of hitting rate limits
- **Overnight batch job**: Acceptable but delays feature availability

**Implementation Notes**:
- Process in batches of 50 chunks with 1-second delay
- Track progress for resumable indexing
- Skip chunks that already have embeddings (incremental updates)
- Log progress for user feedback
- Handle rate limit errors gracefully with retry logic

---

## Integration with Chat Workflow

### Decision: Automatic code retrieval when THN project context is active

**Rationale**:
- Seamless user experience (no manual commands needed)
- Context-aware by default
- Can be disabled or customized if needed
- Follows DAAS pattern for consistency

**Alternatives Considered**:
- **Manual command to enable**: Adds friction, user might forget
- **Always retrieve**: Too aggressive, might retrieve irrelevant code
- **Opt-in per message**: Too manual, breaks flow

**Implementation Notes**:
- Detect THN project context in `context_builder.py`
- Automatically query code_index when THN is active
- Retrieve top-k relevant code snippets (default 5)
- Combine with conversation context
- Allow explicit queries (e.g., "show me the code for X")

---

## Teaching and Learning Support

### Decision: Integrate teaching capabilities into THN chat responses using code context

**Rationale**:
- Code retrieval provides concrete examples for teaching
- Can explain concepts using actual codebase
- Proposes projects based on existing code patterns
- Natural extension of code-aware consultation

**Alternatives Considered**:
- **Separate teaching mode**: Adds complexity, might be underused
- **External teaching tool**: Breaks integration, harder to maintain
- **No teaching support**: Misses opportunity to enhance learning

**Implementation Notes**:
- Use retrieved code as examples in explanations
- Identify code patterns for lesson plans
- Suggest projects based on codebase complexity
- Can be triggered by explicit requests or automatically when appropriate

