# Data Model: Development Environment

**Feature**: Development Environment  
**Date**: 2025-01-27

## Overview

This feature does not introduce new database entities. It adds configuration entities and modifies how existing entities are accessed based on environment mode.

## Configuration Entities

### Environment Configuration

**Purpose**: Determines application operating mode and associated settings.

**Attributes**:
- `mode`: String enum ("development" | "production")
- `database_config`: Database connection parameters (host, port, dbname, user, password)
- `mock_mode_enabled`: Boolean indicating if mock AI responses should be used
- `openai_model`: String model identifier (used in production mode)

**Behavior**:
- Loaded at application startup from environment variables
- Cannot be changed at runtime (requires restart)
- Defaults to "production" if not specified
- Validates database connection availability before use

**State Transitions**:
- Initialization: Load from environment → Validate → Set mode
- Error: Invalid configuration → Log error → Default to production mode

### Database Configuration

**Purpose**: Connection parameters for database access.

**Attributes**:
- `host`: Database server hostname/IP
- `port`: Database server port number
- `dbname`: Database name
- `user`: Database username
- `password`: Database password

**Behavior**:
- Different values for development vs production
- Loaded from environment variables or `.env.local`
- Used to establish database connections
- Validated on application startup

### Mock AI Response Metadata

**Purpose**: Track that a response came from mock mode, not real API.

**Attributes** (stored in message `meta_json`):
- `model`: String (set to "mock" in development mode)
- `created_at`: ISO timestamp
- `mock_mode`: Boolean (true for mock responses)

**Behavior**:
- Added to message metadata when saving mock responses
- Allows filtering/identification of mock vs real responses
- Stored in existing `messages.meta_json` field

## Existing Entities (No Changes)

### Conversations
- **No schema changes**
- Accessed via development or production database based on mode
- Same structure in both databases

### Messages
- **No schema changes**
- `meta_json` field used to store mock mode indicator
- Accessed via development or production database based on mode

### Project Knowledge
- **No schema changes**
- Accessed via development or production database based on mode

## Data Flow

### Development Mode
1. Application starts → Loads `.env.local` → Sets `ENV_MODE=development`
2. Config module → Selects development database config
3. Database operations → Use development database connection
4. Chat requests → Use mock client → Generate mock response
5. Save message → Store in development database with `mock_mode: true` in metadata

### Production Mode
1. Application starts → Loads `.env` → Sets `ENV_MODE=production` (or default)
2. Config module → Selects production database config
3. Database operations → Use production database connection
4. Chat requests → Use OpenAI client → Make API call
5. Save message → Store in production database with real model name in metadata

## Validation Rules

### Environment Configuration
- `ENV_MODE` must be "development" or "production" (case-insensitive)
- If invalid, default to "production" and log warning
- Development database config must be complete if `ENV_MODE=development`

### Database Configuration
- All connection parameters must be provided
- Connection must be testable on startup
- If connection fails, application should not start (fail fast)

### Mock Mode
- Automatically enabled when `ENV_MODE=development`
- Can be explicitly disabled via `MOCK_MODE=false` (for testing real API with dev DB)
- Mock responses must include metadata flag

## Relationships

- **Environment Configuration** → **Database Configuration**: One-to-one (different configs per mode)
- **Environment Configuration** → **Mock Client**: Controls which client is used
- **Messages** → **Mock Metadata**: Messages can have mock metadata (many-to-one relationship)

## Data Isolation Guarantees

- Development database operations never touch production database
- Production database operations never touch development database
- Mode switching requires application restart (enforced isolation)
- No shared state between modes (separate database connections)

