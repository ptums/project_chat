# Implementation Plan: Development Environment

**Branch**: `001-dev-environment` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-dev-environment/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable a development environment that isolates development work from production by:
1. Supporting environment mode switching (development/production) via configuration
2. Using a separate development database when in development mode
3. Providing mock AI responses without OpenAI API calls in development mode
4. Ensuring zero production data contamination during development

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Flask, psycopg2, python-dotenv, openai (Python SDK)  
**Storage**: PostgreSQL (production and development databases)  
**Testing**: pytest (for unit/integration tests)  
**Target Platform**: Linux/macOS (single machine deployment)  
**Project Type**: Single project (CLI + API server)  
**Performance Goals**: Mock responses <100ms, configuration validation <5s  
**Constraints**: Must not affect production data, zero API costs in dev mode  
**Scale/Scope**: Single developer, local development environment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality ✓
- **Readability First**: Configuration-based mode switching keeps code explicit
- **Minimal Dependencies**: Uses existing dependencies (python-dotenv, psycopg2)
- **Type Hints**: Will add type hints to new configuration functions
- **Single Responsibility**: Separate modules for config, mock client, database connection

### Accuracy ✓
- **Error Handling**: Will validate database connections and configuration at startup
- **Data Validation**: Environment mode validation prevents accidental production use
- **State Consistency**: Separate database connections ensure isolation
- **No Silent Failures**: Clear error messages for misconfiguration

### Rapid Development ✓
- **Pragmatic Over Perfect**: Simple environment variable-based switching
- **Local-First**: Optimized for local development workflow
- **Simple Solutions**: Configuration file (.env.local) for dev settings
- **Fast Iteration**: Quick mode switching via restart

### Personal Use Context ✓
- **No Multi-Tenancy**: Single developer use case
- **Trusted Environment**: Local configuration files acceptable
- **Direct Configuration**: Environment variables and .env files
- **Manual Deployment**: Single machine deployment

### Single Machine Deployment ✓
- **No Scalability Concerns**: Single process, local database
- **Local Resources**: Local PostgreSQL instance for development
- **Simple Networking**: Localhost connections
- **Resource Efficiency**: Minimal overhead for mode switching

**GATE STATUS**: ✅ PASSED - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-dev-environment/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
brain_core/
├── __init__.py
├── config.py            # Updated: environment mode detection, DB config selection
├── chat.py              # Updated: uses client from config (mock or real)
├── db.py                # Updated: uses DB_CONFIG from config
├── memory.py            # No changes needed
└── mock_client.py       # NEW: Mock OpenAI client implementation

api_server.py            # No changes needed (uses brain_core modules)
chat_cli.py              # No changes needed (uses brain_core modules)

.env.local               # NEW: Development configuration file
.env.example             # NEW: Example configuration template
setup_dev_db.py          # NEW: Development database initialization script
```

**Structure Decision**: Extending existing single-project structure. New files:
- `brain_core/mock_client.py` for mock OpenAI client
- `.env.local` for development configuration (user-created)
- `.env.example` as configuration template
- `setup_dev_db.py` for database initialization

## Complexity Tracking

> **No violations identified - all changes align with constitution principles**
