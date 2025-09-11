# EMS Project Memory Bank

This file serves as a memory bank for Cursor AI to remember important context about the EMS project.

## Project Overview

- **Project Name**: EMS (Employee Management System)
- **Framework**: FastAPI with Python
- **Architecture**: 3-layer architecture (Controller → Service → Repository → Database)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration**: Alembic for database migrations

## Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Authentication**: Passlib with bcrypt for password hashing
- **HTTP Client**: httpx for external service calls
- **Environment**: pydantic-settings for configuration
- **Testing**: pytest with httpx for async testing

## Project Structure

```
src/
├── bootstrap/          # Application initialization
├── common/            # Shared utilities
│   ├── exception/     # Custom exceptions
│   └── log/          # Custom logging configuration
├── config/           # Configuration management
├── core/             # Business logic
│   ├── models/       # Database models
│   └── services/     # Business services
├── present/          # Presentation layer
│   ├── controllers/  # Request handlers
│   ├── middleware/   # Custom middleware
│   ├── request/      # Request models
│   └── routers/      # FastAPI routers
├── repository/       # Data access layer
└── sdk/             # External service clients
```

## Architecture Principles

### 3-Layer Architecture
1. **Presentation Layer** (`src/present/`): Controllers, routers, middleware
2. **Business Layer** (`src/core/`): Services containing business logic
3. **Data Layer** (`src/repository/`): Database access and models

### Dependency Injection
- Services are injected into controllers via bootstrap
- External clients (IAM) are injected into services
- Database sessions are managed by bootstrap

## Key Components

### Bootstrap System
- **File**: `src/bootstrap/application_bootstrap.py`
- **Purpose**: Centralized initialization of all application layers
- **Pattern**: Dependency injection with proper resource cleanup
- **Components**: Database, IAM client, repositories, services, controllers

### Custom Logging
- **Location**: `src/common/log/`
- **Features**: Request ID tracking, custom formatting
- **Middleware**: `RequestIDMiddleware` for request tracking
- **Configuration**: Suppresses uvicorn access logs, keeps custom request logs

### Exception Handling
- **File**: `src/common/exception/exceptions.py`
- **Base**: `EMSException` with HTTP status codes
- **Types**: ValidationException, NotFoundException, ConflictException, etc.
- **Handler**: Global exception handler in `main.py`

### External Service Integration
- **IAM Service**: `src/sdk/ems_iam_client.py`
- **Authentication**: Basic auth with configurable credentials
- **Integration**: Injected into UserService for sync operations
- **Features**: User management, authentication, role/permission checking

## Configuration

### Settings (`src/config/config.py`)
- Database URL, app settings, security config
- IAM service configuration
- Logging levels
- Environment-based with `.env` file support

### Key Settings
- `database_url`: PostgreSQL connection
- `iam_service_url`: EMS-IAM service endpoint
- `iam_username/password`: Basic auth credentials
- `log_level`: Logging configuration

## Database

### Models
- **User Model** (`src/core/models/user.py`): User entity with authentication
- **Base Repository** (`src/repository/base_repository.py`): Common CRUD operations

### Migration
- **Tool**: Alembic
- **Command**: `python migrate.py` for migrations
- **Files**: `alembic/versions/` for migration scripts

## User Management

### UserService (`src/core/services/user_service.py`)
- **Features**: CRUD operations, authentication, password management
- **IAM Integration**: Syncs users to EMS-IAM service
- **Security**: Password hashing with bcrypt
- **Validation**: Email/username uniqueness checks

### Authentication Flow
1. Local password verification with bcrypt
2. Optional IAM service authentication
3. Permission checking via IAM service
4. Role management through IAM integration

## API Structure

### Endpoints
- **Health**: `GET /ems/api/v1/health` - Service health check
- **Users**: 
  - `POST /ems/api/v1/users/` - Create user
  - `GET /ems/api/v1/users/` - List users (pagination)
  - `GET /ems/api/v1/users/{id}` - Get user by ID
  - `PUT /ems/api/v1/users/{id}` - Update user
  - `DELETE /ems/api/v1/users/{id}` - Delete user
- **Auth**:
  - `POST /ems/api/v1/auth/login` - User authentication
  - `POST /ems/api/v1/auth/change-password/{id}` - Change password

### Request/Response Models
- **UserCreate**: email, username, full_name, password, is_active
- **UserUpdate**: Optional fields for user updates
- **LoginRequest**: email, password
- **Token**: access_token, token_type
- **User**: Full user object (no password)

### Middleware Stack
1. RequestIDMiddleware (request tracking)
2. CORSMiddleware (cross-origin requests)
3. Custom exception handler

## Development Patterns

### Error Handling
- Graceful degradation for IAM service failures
- Comprehensive logging for debugging
- Structured exception responses

### Resource Management
- Context managers for external clients
- Proper cleanup in bootstrap shutdown
- Thread-safe implementations

### Testing
- Async test support with pytest-asyncio
- HTTP client testing with httpx
- Separation of concerns for unit testing

## User Preferences & Patterns

### Code Style
- User prefers concise solutions over verbose explanations
- Dependency injection pattern for external services
- Clean separation of concerns
- Vietnamese comments accepted when requested

### Integration Approach
- External services should be injectable dependencies
- Bootstrap-managed lifecycle for all components
- Configuration-driven external service connections
- Resilient error handling (don't fail on external service errors)

## Common Commands

```bash
# Run application
python main.py

# Database migration
python migrate.py

# Install dependencies
pip install -r requirements.txt
```

## Important Notes

1. **Request Logging**: Custom format without "request_tracker" prefix
2. **IAM Integration**: Resilient design - local operations continue if IAM fails
3. **Dependency Injection**: All external dependencies injected via bootstrap
4. **Resource Cleanup**: Proper shutdown handling for all managed resources
5. **Configuration**: Environment-driven with sensible defaults

## Recent Changes

- Implemented EMS-IAM client with basic authentication
- Added dependency injection for IAM client in UserService
- Removed default uvicorn access logs, kept custom request tracking
- Bootstrap now manages IAM client lifecycle
- UserService syncs users to IAM service automatically
- Created Cursor Memory Bank for project context persistence

## Testing

### Framework
- **pytest** with **pytest-asyncio** for async support
- **httpx** for HTTP client testing
- Test files in `tests/` directory

### Patterns
- Unit tests for services (business logic)
- Integration tests for API endpoints
- Mock external dependencies (IAM client) for testing

## External Services

### EMS-IAM Service
- **URL**: Configurable via `iam_service_url`
- **Auth**: Basic authentication
- **Features**: User management, authentication, roles, permissions
- **Integration**: Injected into UserService for seamless operation
