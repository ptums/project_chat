# THN Code RAG Pipeline Enhancement

## Problem Statement

Project THN serves as a technical consultant for home networking projects, but currently lacks awareness of the production codebase. When debugging production issues, the user must manually copy error output into Cursor, which has no context about the production environment (tumultymedia, tumultymedia2, tumultymedia3, etc.) or the actual code running in those environments.

The goal is to give THN the ability to analyze and understand the code that runs on production systems, enabling holistic debugging that understands both code and environment context.

## User Stories

### US1: Repository Code Indexing (P1)

**As a** developer  
**I want** all THN-related repository code to be indexed with vector embeddings  
**So that** the system can retrieve relevant code snippets during conversations

**Acceptance Criteria:**
- All THN repositories are cloned into `repos/` directory
- Code files are parsed and converted to embeddings using text-embedding-3-small (1536 dimensions)
- Embeddings are stored in PostgreSQL using pgvector
- System can handle multiple repositories and file types (Python, shell scripts, config files, etc.)
- Indexing can be run incrementally to update when repositories change

### US2: Code Retrieval for THN Context (P1)

**As a** developer  
**I want** relevant code snippets retrieved automatically when discussing THN topics  
**So that** I get context-aware answers about my actual codebase

**Acceptance Criteria:**
- When project context is THN, system queries vector database for relevant code
- Retrieved code snippets are combined with the model prompt
- System restricts references to THN codebase by default
- Cross-project references only when explicitly requested
- Retrieval works for both specific file queries and semantic searches

### US3: Production Environment Awareness (P2)

**As a** developer  
**I want** THN to understand which code runs on which production machine  
**So that** debugging can consider environment-specific configurations

**Acceptance Criteria:**
- System can associate code files with production machines (tumultymedia, tumultymedia2, tumultymedia3)
- Code metadata includes deployment target information
- Retrieval can filter by production environment when relevant
- System understands deployment workflow (local → GitLab main → production pull)

### US4: Teaching and Learning Support (P2)

**As a** developer  
**I want** THN to explain technical concepts and propose learning projects  
**So that** I can deepen my understanding of the systems I'm building

**Acceptance Criteria:**
- System can explain technical concepts found in the codebase
- System can create lesson plans based on code patterns
- System can propose practical projects to strengthen technical skills
- Teaching mode is integrated with code retrieval for context-aware explanations

## Technical Requirements

1. **Repository Management:**
   - Clone THN repositories into `repos/` directory structure
   - Support multiple repositories
   - Track repository metadata (name, path, last indexed, etc.)

2. **Code Parsing and Embedding:**
   - Parse code files (Python, shell, config, etc.)
   - Generate embeddings using text-embedding-3-small (1536 dimensions)
   - Handle large files (chunking if needed)
   - Store file metadata (path, language, size, etc.)

3. **Vector Storage:**
   - Use pgvector extension in PostgreSQL
   - Store embeddings with code snippets and metadata
   - Support similarity search for semantic code retrieval
   - Index embeddings for fast retrieval

4. **RAG Pipeline:**
   - Query vector database when THN context is active
   - Retrieve top-k relevant code snippets
   - Combine with model prompt for context-aware responses
   - Restrict to THN codebase by default

5. **Integration:**
   - Integrate with existing chat_cli.py workflow
   - Use existing embedding_service.py infrastructure
   - Follow DAAS RAG pattern for consistency
   - Maintain backward compatibility with other projects

## Out of Scope

- Real-time code synchronization (indexing is manual/incremental)
- Code execution or testing capabilities
- Automatic repository discovery (repositories must be manually cloned)
- Cross-project code analysis (unless explicitly requested)
- Code modification or generation (read-only analysis)

## Phase 1 Implementation

Focus on core functionality:
1. Repository cloning and structure
2. Code file parsing and embedding generation
3. Vector storage in PostgreSQL
4. Basic RAG retrieval for THN context
5. Integration with chat workflow

