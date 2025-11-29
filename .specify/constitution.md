# Project Constitution

## Core Principles

### 1. Code Quality
- **Readability First**: Code must be immediately understandable. Prefer explicit over clever.
- **Minimal Dependencies**: Only add dependencies when they solve real problems. Avoid framework bloat.
- **Type Hints**: Use type hints for function signatures and complex data structures.
- **Consistent Style**: Follow PEP 8. Use `black` for formatting when possible.
- **Single Responsibility**: Functions and classes should do one thing well.

### 2. Accuracy
- **Error Handling**: Handle expected errors explicitly. Fail fast with clear messages.
- **Data Validation**: Validate inputs at boundaries (API endpoints, CLI inputs, DB writes).
- **State Consistency**: Ensure database and in-memory state stay synchronized.
- **No Silent Failures**: Log errors. Don't swallow exceptions without good reason.

### 3. Rapid Development
- **Pragmatic Over Perfect**: Ship working code. Refactor when patterns emerge.
- **Local-First**: Optimize for local development speed. Skip premature optimization.
- **Simple Solutions**: Choose the simplest solution that works. Avoid over-engineering.
- **Fast Iteration**: Prefer quick feedback loops over comprehensive planning.

### 4. Personal Use Context
- **No Multi-Tenancy**: Assume single user. Skip user isolation and complex permissions.
- **Trusted Environment**: Assume local machine is secure. Skip enterprise security overhead.
- **Direct Configuration**: Use environment variables and simple config files. No complex orchestration.
- **Manual Deployment**: Optimize for manual deployment on single machine.

### 5. Single Machine Deployment
- **No Scalability Concerns**: Don't design for horizontal scaling. Single process is fine.
- **Local Resources**: Use local SQLite. No need for distributed databases.
- **Simple Networking**: Localhost-first. No complex network topologies.
- **Resource Efficiency**: Be mindful of memory/CPU, but don't over-optimize.

## Development Guidelines

### Code Structure
- Keep modules focused and cohesive.
- Prefer composition over inheritance.
- Use dependency injection for testability, but keep it simple.

### Testing
- Write tests for critical paths (DB operations, API calls, core logic).
- Mock external APIs for development.
- Integration tests for key workflows.

### Documentation
- Docstrings for public functions and classes.
- README for setup and usage.
- Inline comments for non-obvious logic only.

### Performance
- Profile before optimizing.
- SQLite is sufficient for single-user workloads.
- Cache expensive operations when it improves UX.

### Security
- Sanitize user inputs to prevent injection.
- Use parameterized queries for all DB operations.
- Keep dependencies updated for known vulnerabilities.

## Anti-Patterns to Avoid

- **Over-Engineering**: Don't build abstractions until you need them.
- **Premature Optimization**: Don't optimize until you have performance data.
- **Framework Lock-In**: Prefer standard library and lightweight libraries.
- **Complex State Management**: Keep state simple and explicit.
- **Enterprise Patterns**: Skip patterns designed for large teams (microservices, complex CI/CD, etc.).

## Decision Framework

When making technical decisions, prioritize:
1. **Speed of Development** (for personal use)
2. **Code Clarity** (for future maintenance)
3. **Correctness** (accuracy matters)
4. **Simplicity** (avoid unnecessary complexity)

If a choice improves development speed without sacrificing correctness or clarity, choose it.

