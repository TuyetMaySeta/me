# 3-Layer Architecture with src/ Directory

This FastAPI project follows the **3-Layer Architecture** pattern with source code organized in a `src/` directory following Python best practices.

## Project Structure

```
ems/
├── src/                       # Source code directory
│   ├── present/              # PRESENT LAYER
│   │   ├── controllers/     # Business logic controllers
│   │   │   ├── __init__.py
│   │   │   ├── user_controller.py
│   │   │   └── auth_controller.py
│   │   ├── routers/         # FastAPI routers
│   │   │   ├── __init__.py
│   │   │   ├── user_router.py
│   │   │   └── auth_router.py
│   │   ├── middleware/      # HTTP middleware
│   │   │   ├── __init__.py
│   │   │   └── recovery_middleware.py
│   │   ├── request/         # Request/Response DTOs
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── auth.py
│   │   └── validators/      # Request validators
│   │       └── __init__.py
│   ├── core/                # CORE LAYER
│   │   ├── models/         # Database models
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   └── services/       # Business logic services
│   │       ├── __init__.py
│   │       └── user_service.py
│   ├── repository/         # REPOSITORY LAYER
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   └── user_repository.py
│   ├── config/             # CONFIGURATION LAYER
│   │   ├── __init__.py
│   │   └── config.py       # App settings
│   └── bootstrap/          # BOOTSTRAP LAYER
│       ├── __init__.py
│       ├── database_bootstrap.py # Database initialization
│       └── dependencies.py # Dependency injection
├── alembic/                # Database migrations
├── tests/                  # Test files
├── docker-compose.yml      # PostgreSQL database
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Layer Responsibilities

### 1. Present Layer (`src/present/`)
**Responsibilities**:
- Handle HTTP requests and responses
- Route mapping and endpoint definitions
- Request validation and error handling
- Dependency injection for controllers
- Apply middleware for cross-cutting concerns
- Define request/response DTOs

**Structure**:
- `controllers/` - Business logic controllers
- `routers/` - FastAPI routers
- `middleware/` - HTTP middleware (recovery, auth, etc.)
- `request/` - Request/Response DTOs (Pydantic schemas)
- `validators/` - Request validators

### 2. Core Layer (`src/core/`)
**Responsibilities**:
- Database models (SQLAlchemy entities)
- Business logic services
- Data validation and transformation
- Complex business operations

**Structure**:
- `models/` - Database models
- `services/` - Business logic services

### 3. Repository Layer (`src/repository/`)
**Responsibilities**:
- Database operations (CRUD)
- Query optimization
- Data mapping between database and models
- Database-specific logic

**Structure**:
- `base_repository.py` - Generic repository
- `user_repository.py` - User-specific repository

### 4. Configuration Layer (`src/config/`)
**Responsibilities**:
- **App Settings**: Environment variables and configuration
- **Configuration Management**: Centralized settings

**Files**:
- `config.py`: Application settings and environment variables

### 5. Bootstrap Layer (`src/bootstrap/`)
**Responsibilities**:
- **Database Initialization**: Centralized database setup and management
- **Dependency Injection**: Complete dependency chain (DB → Service → Controller)
- **Application Wiring**: Connecting all components together
- **Service Initialization**: Setting up service instances
- **Controller Initialization**: Setting up controller instances

**Files**:
- `database_bootstrap.py`: Database engine, session, and connection management
- `dependencies.py`: Complete dependency injection functions

**Dependency Chain**:
- `database_bootstrap` → Database engine and session factory
- `get_db()` → Database session with retry logic
- `get_user_service(db)` → User service with database
- `get_user_controller(user_service)` → User controller with service
- `get_auth_controller(user_service)` → Auth controller with service

## Data Flow

```
HTTP Request → Router → Controller → Service → Repository → Database
                ↓         ↓          ↓         ↓
HTTP Response ← Router ← Controller ← Service ← Repository ← Database
```

## Dependencies

- **Controller** contains **Service**
- **Service** contains **Repository**
- **Repository** interacts with **Database**

## Import Structure

```python
# From src directory
from src.present.controllers.user_controller import UserController
from src.core.services.user_service import UserService
from src.repository.user_repository import UserRepository
```

## Benefits of src/ Directory

- **Clean separation** between source code and configuration
- **Python best practices** - follows PEP 8 recommendations
- **Easy testing** - clear source code organization
- **Scalable** - easy to add new modules
- **Professional structure** - industry standard layout

## Running the Application

```bash
# Start database
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start application
python main.py
```

The application will automatically detect and display all routes from the `src/` directory structure.
