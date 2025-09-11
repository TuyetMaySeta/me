# EMS Project Context for Cursor AI

## Quick Reference

### Current State
- ✅ FastAPI application with 3-layer architecture
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Custom logging system with request tracking
- ✅ EMS-IAM service integration via SDK
- ✅ Dependency injection pattern implemented
- ✅ Bootstrap system for component lifecycle

### Active Integrations
- **Database**: PostgreSQL via SQLAlchemy
- **IAM Service**: EMS-IAM with basic auth
- **Logging**: Custom system with request ID tracking

### User Preferences
- Prefers concise, practical solutions
- Uses dependency injection for external services
- Wants resilient error handling
- Accepts Vietnamese comments when requested
- Values clean architecture patterns

## Key File Locations

### Core Files
- `main.py` - FastAPI application entry point
- `src/bootstrap/application_bootstrap.py` - Component initialization
- `src/config/config.py` - Configuration management
- `src/core/services/user_service.py` - User business logic
- `src/sdk/ems_iam_client.py` - IAM service client

### Architecture Layers
- **Presentation**: `src/present/` (controllers, routers, middleware)
- **Business**: `src/core/` (services, models)
- **Data**: `src/repository/` (data access)

### Configuration
- Environment variables in `.env`
- Settings class in `src/config/config.py`
- Database URL, IAM credentials, logging levels

## Common Tasks

### Adding New Services
1. Create service in `src/core/services/`
2. Add to bootstrap initialization
3. Inject dependencies via constructor
4. Add controllers in `src/present/controllers/`

### External Service Integration
1. Create client in `src/sdk/`
2. Add configuration to `settings`
3. Initialize in bootstrap
4. Inject into services that need it

### Database Changes
1. Modify models in `src/core/models/`
2. Run `python migrate.py` for migrations
3. Update repositories if needed

## Current Technology Stack

```
FastAPI (web framework)
├── SQLAlchemy (ORM)
├── Alembic (migrations)
├── PostgreSQL (database)
├── Passlib (password hashing)
├── httpx (HTTP client)
├── Pydantic (validation)
└── Pytest (testing)
```

## Recent Interactions Context

The user has been working on:
1. Setting up custom logging (removed uvicorn logs, kept custom tracking)
2. Creating EMS-IAM service integration
3. Implementing dependency injection pattern
4. Managing component lifecycle via bootstrap

The user's style:
- Direct, practical approach
- Prefers working solutions over extensive documentation
- Values clean, maintainable code architecture
- Uses English for development communication
