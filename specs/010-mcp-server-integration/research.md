# Research: MCP Server Integration

## MCP Protocol Implementation

### Decision: JSON-RPC 2.0 over stdio

**Rationale**: MCP servers communicate via JSON-RPC 2.0 protocol over stdin/stdout. This is a standard protocol that allows for structured request/response communication with external processes.

**Alternatives considered**:
- HTTP/WebSocket: Rejected - MCP servers use stdio for simplicity and portability
- Custom protocol: Rejected - JSON-RPC 2.0 is standard and well-supported

### Decision: Subprocess with Persistent Connection

**Rationale**: MCP servers are long-running processes that maintain state. We need to:
1. Start the MCP server process once
2. Keep it alive for the duration of the chat session
3. Send multiple requests over the same connection
4. Handle process lifecycle (start, stop, restart on failure)

**Implementation approach**:
- Use `subprocess.Popen` with `stdin`, `stdout`, `stderr` pipes
- Maintain process handle for the session
- Send JSON-RPC requests via stdin
- Read JSON-RPC responses from stdout
- Handle process termination and restart on errors

**Alternatives considered**:
- One-shot subprocess per request: Rejected - too slow, loses server state
- Threading vs asyncio: Use threading for simplicity (project uses sync code)

## Subprocess Management

### Decision: Threading for Non-Blocking Operations

**Rationale**: Project_chat uses synchronous code patterns. For non-blocking MCP calls:
- Use threading to run MCP requests in background
- Main thread continues chat interaction
- Cache results for immediate access

**Alternatives considered**:
- asyncio: Rejected - would require async/await throughout codebase
- Synchronous blocking: Rejected - would block chat during MCP calls
- Threading: Chosen - minimal code changes, fits existing patterns

### Decision: Process Lifecycle Management

**Rationale**: MCP servers should:
- Start on first use (lazy initialization)
- Restart on failure (with backoff)
- Shutdown gracefully on chat exit
- Support multiple servers (one process per server)

**Implementation**:
- MCP client manager tracks active processes
- Each server has its own subprocess
- Process health checks before requests
- Automatic restart with exponential backoff

## Caching Strategy

### Decision: In-Memory Cache with TTL

**Rationale**: MCP resources should be cached to:
- Reduce latency for repeated access
- Avoid excessive calls to MCP server
- Support offline access to recently accessed resources

**Implementation**:
- Cache resources by URI with TTL (default: 5 minutes)
- Cache resource lists (default: 1 minute)
- Invalidate cache on sync operations
- Simple dict-based cache (no external dependencies)

**Alternatives considered**:
- No cache: Rejected - too slow for repeated access
- Persistent cache (database/file): Rejected - unnecessary complexity for this use case
- External cache (Redis): Rejected - overkill, adds dependency

## Error Handling

### Decision: Graceful Degradation

**Rationale**: MCP servers are optional enhancements. If unavailable:
- Log warnings but don't fail chat
- Continue without MCP context
- Provide clear error messages to user
- Support retry with backoff

**Error scenarios**:
1. MCP server not configured → skip MCP features
2. MCP server process fails → log error, continue without MCP
3. MCP request timeout → return empty result, log warning
4. MCP server returns error → log error, continue without that resource

**Alternatives considered**:
- Fail hard: Rejected - breaks chat if MCP server has issues
- Silent failure: Rejected - user should know when MCP unavailable

## Configuration Management

### Decision: JSON Config File + Environment Variables

**Rationale**: MCP server configuration should be:
- Easy to configure (JSON file)
- Support environment variables for sensitive data (tokens)
- Allow multiple servers
- Support server-specific environment variables

**Implementation**:
- Optional `mcp_config.json` in project root
- Environment variables override JSON config
- Support for server-specific env vars (e.g., `MCP_MEDITATION_GITLAB_TOKEN`)
- Fallback to config.py if JSON not present

**Alternatives considered**:
- Only environment variables: Rejected - too verbose for multiple servers
- Only config.py: Rejected - less flexible, harder to share configs
- Only JSON: Rejected - can't easily handle secrets

## Context Integration

### Decision: Project-Specific MCP Server Association

**Rationale**: Different projects may benefit from different MCP servers:
- DAAS project → meditation notes
- THN project → code repositories (future)
- General → no MCP servers

**Implementation**:
- Configuration maps projects to MCP servers
- Context builder checks project and includes relevant MCP resources
- Automatic inclusion in conversation context when relevant
- Manual access via `/mcp` command regardless of project

**Alternatives considered**:
- All MCP servers for all projects: Rejected - too much context, slower
- No automatic inclusion: Rejected - reduces value of integration

## Performance Considerations

### Decision: Async Resource Loading

**Rationale**: MCP resource retrieval should not block chat:
- Load resources in background thread
- Use cached resources when available
- Timeout after 500ms for resource requests
- Parallel requests for multiple resources

**Implementation**:
- Thread pool for concurrent MCP requests
- Timeout handling for slow servers
- Cache-first strategy (check cache before MCP call)

**Alternatives considered**:
- Synchronous blocking: Rejected - blocks chat interaction
- Full async/await: Rejected - requires major refactoring

