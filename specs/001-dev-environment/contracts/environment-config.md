# Environment Configuration Contract

**Feature**: Development Environment  
**Date**: 2025-01-27

## Overview

This contract defines how the application determines its operating mode and loads configuration.

## Configuration Sources

### Priority Order (highest to lowest)
1. Environment variables (system/environment)
2. `.env.local` file (development-specific)
3. `.env` file (production/default)
4. Hard-coded defaults

## Environment Variables

### Required for Development Mode

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENV_MODE` | string | `"production"` | Operating mode: "development" or "production" |
| `DEV_DB_HOST` | string | `DB_HOST` | Development database host |
| `DEV_DB_PORT` | integer | `DB_PORT` | Development database port |
| `DEV_DB_NAME` | string | `DB_NAME + "_dev"` | Development database name |
| `DEV_DB_USER` | string | `DB_USER` | Development database user |
| `DEV_DB_PASSWORD` | string | `DB_PASSWORD` | Development database password |

### Required for Production Mode

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DB_HOST` | string | `"127.0.0.1"` | Production database host |
| `DB_PORT` | integer | `5432` | Production database port |
| `DB_NAME` | string | `"ongoing_projects"` | Production database name |
| `DB_USER` | string | `"thn_user"` | Production database user |
| `DB_PASSWORD` | string | `""` | Production database password |

### Optional

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MOCK_MODE` | boolean | `auto` | Force mock mode (auto-enabled in development) |
| `OPENAI_MODEL` | string | `"gpt-4.1"` | OpenAI model identifier |

## Configuration Loading Behavior

### On Application Start

1. Load `.env` file (if exists)
2. Load `.env.local` file (if exists, overrides `.env`)
3. Override with environment variables (if set)
4. Validate configuration
5. Set operating mode
6. Initialize database connection
7. Initialize AI client (mock or real)

### Validation Rules

- `ENV_MODE` must be "development" or "production" (case-insensitive)
- If `ENV_MODE=development`, development database config must be complete
- Database connection must be testable
- Invalid configuration → default to production mode + log warning

### Error Handling

- Missing required variables → use defaults or fail with clear error
- Invalid `ENV_MODE` → default to "production" + log warning
- Database connection failure → fail fast with error message
- Configuration file parse errors → log warning + continue with defaults

## Mode Detection

### Development Mode
- `ENV_MODE=development` OR
- `ENV_MODE=dev` (case-insensitive)
- Uses development database config
- Enables mock AI client (unless `MOCK_MODE=false`)

### Production Mode
- `ENV_MODE=production` OR
- `ENV_MODE=prod` OR
- `ENV_MODE` not set (default)
- Uses production database config
- Uses real OpenAI client

## Configuration Access

### Python Interface

```python
from brain_core.config import ENV_MODE, DB_CONFIG, MOCK_MODE, client

# ENV_MODE: "development" | "production"
# DB_CONFIG: dict with connection parameters
# MOCK_MODE: bool
# client: MockOpenAIClient | OpenAI client instance
```

### Runtime Behavior

- Configuration is read-only after initialization
- Mode cannot be changed without restart
- Database connection uses selected config
- AI client uses selected implementation

## Example Configurations

### Development (.env.local)
```bash
ENV_MODE=development
DEV_DB_HOST=127.0.0.1
DEV_DB_PORT=5432
DEV_DB_NAME=ongoing_projects_dev
DEV_DB_USER=thn_user
DEV_DB_PASSWORD=dev_password
MOCK_MODE=true
```

### Production (.env)
```bash
ENV_MODE=production
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=ongoing_projects
DB_USER=thn_user
DB_PASSWORD=production_password
OPENAI_MODEL=gpt-4.1
```

