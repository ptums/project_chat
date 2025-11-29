# Quick Start: Development Environment

**Feature**: Development Environment  
**Date**: 2025-01-27

## Overview

This guide helps you set up and use the development environment for local development without affecting production data or incurring API costs.

## Prerequisites

- Python 3.10+
- PostgreSQL instance (local or remote)
- Existing project codebase
- `.env.local` file with development configuration (you've already created this)

## Setup Steps

### 1. Configure Development Environment

Your `.env.local` file should contain:

```bash
ENV_MODE=development
DEV_DB_HOST=127.0.0.1
DEV_DB_PORT=5432
DEV_DB_NAME=ongoing_projects_dev
DEV_DB_USER=thn_user
DEV_DB_PASSWORD=your_dev_password
```

### 2. Initialize Development Database

Run the database initialization script:

```bash
python setup_dev_db.py
```

This will:
- Create the development database if it doesn't exist
- Set up the schema (conversations, messages, project_knowledge tables)
- Create necessary indexes

### 3. Verify Configuration

Start the application and verify it's using development mode:

```bash
# For CLI
python chat_cli.py

# For API server
python api_server.py
```

Check the logs/console for:
- "Development mode enabled" message
- Connection to development database
- Mock mode indicator

### 4. Test Development Mode

#### Test CLI
```bash
python chat_cli.py
# Create a conversation
# Send a message
# Verify response is from mock mode (should indicate [MOCK MODE])
```

#### Test API
```bash
python api_server.py
# In another terminal:
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "...", "message": "test"}'
# Verify response indicates mock mode
```

## Switching Between Modes

### To Development Mode

1. Ensure `.env.local` exists with `ENV_MODE=development`
2. Restart the application

### To Production Mode

1. Remove or rename `.env.local`, OR
2. Set `ENV_MODE=production` in your environment
3. Restart the application

**Important**: Mode switching requires application restart. No runtime switching is supported.

## Verification Checklist

- [ ] Development database created and accessible
- [ ] `.env.local` configured with development settings
- [ ] Application starts without errors
- [ ] Chat responses indicate mock mode
- [ ] No OpenAI API calls are made (check network logs)
- [ ] Data is stored in development database only
- [ ] Production database remains untouched

## Troubleshooting

### Database Connection Fails

**Error**: "Database connection error"

**Solutions**:
- Verify PostgreSQL is running
- Check database credentials in `.env.local`
- Ensure database exists (run `setup_dev_db.py`)
- Test connection manually: `psql -h HOST -p PORT -U USER -d DB_NAME`

### Wrong Mode Active

**Symptom**: Still using production database or real API

**Solutions**:
- Verify `ENV_MODE=development` in `.env.local`
- Check that `.env.local` is being loaded (python-dotenv)
- Restart the application
- Check for environment variable overrides

### Mock Mode Not Working

**Symptom**: Still making OpenAI API calls

**Solutions**:
- Verify `ENV_MODE=development` is set
- Check that `MOCK_MODE` is not explicitly set to `false`
- Verify mock client is being imported correctly
- Check application logs for mode detection

## Development Workflow

### Typical Development Session

1. **Start**: Ensure `.env.local` is configured
2. **Develop**: Make code changes, test with mock responses
3. **Test**: Run tests, verify functionality
4. **Iterate**: Repeat development cycle
5. **Switch to Production**: When ready, test with real API (optional)

### Best Practices

- Always work in development mode during feature development
- Use production mode only for final testing or actual use
- Keep development database separate (don't mix with production)
- Clear development database when needed (it's safe to recreate)

## Next Steps

After setup:
- Develop new features without API costs
- Test with mock responses
- Iterate quickly without production data concerns
- When ready, test with production mode

## Support

For issues or questions:
- Check application logs for error messages
- Verify configuration matches examples above
- Ensure all prerequisites are met
- Review troubleshooting section

