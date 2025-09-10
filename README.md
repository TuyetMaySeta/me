# EMS FastAPI Server

A modern Python web server built with FastAPI, SQLAlchemy, Alembic, and PostgreSQL using **3-Layer Architecture**.

## ✨ Features

- **FastAPI**: Modern, fast web framework for building APIs
- **3-Layer Architecture**: Clean separation of concerns (Present, Core, Repository)
- **SQLAlchemy**: Powerful SQL toolkit and Object-Relational Mapping (ORM)
- **Alembic**: Database migration tool for SQLAlchemy
- **PostgreSQL**: Robust, open-source relational database
- **Pydantic**: Data validation using Python type annotations
- **Password Hashing**: Secure password hashing with bcrypt
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-Origin Resource Sharing middleware
- **Recovery Middleware**: Global error recovery and circuit breaker
- **Health Monitoring**: Comprehensive health checks
- **Dependency Injection**: Clean dependency management in bootstrap layer

## 🏗️ Project Structure

```
ems/
├── src/                        # Source code directory
│   ├── present/               # PRESENT LAYER
│   │   ├── controllers/       # Business logic controllers
│   │   ├── routers/          # FastAPI routers
│   │   ├── middleware/       # HTTP middleware
│   │   ├── request/          # Request/Response DTOs
│   │   └── validators/       # Request validators
│   ├── core/                 # CORE LAYER
│   │   ├── models/          # Database models
│   │   └── services/        # Business logic services
│   ├── repository/          # REPOSITORY LAYER
│   │   ├── base_repository.py
│   │   └── user_repository.py
│   ├── config/              # CONFIGURATION LAYER
│   │   └── config.py        # App settings
│   └── bootstrap/           # BOOTSTRAP LAYER
│       ├── database_bootstrap.py
│       └── dependencies.py  # Dependency injection
├── alembic/                 # Database migrations
├── docs/                    # Documentation
│   ├── MIGRATION_GUIDE.md   # Database migration guide
│   ├── RECOVERY.md          # Recovery system documentation
│   └── SRC_ARCHITECTURE.md  # Detailed architecture docs
├── tests/                   # Test files
├── docker-compose.yml       # PostgreSQL database
├── main.py                 # Application entry point
├── migrate.py              # Migration helper script
└── requirements.txt        # Dependencies
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** (or Docker)
- **pip** (Python package installer)
- **make** (for convenient commands)

### 2. Super Quick Setup (Using Makefile)

```bash
# Complete setup in one command
make setup

# Or step by step
make install          # Install dependencies
make db-start         # Start database
make migrate-up       # Apply migrations
make server-dev       # Start development server
```

### 3. Manual Setup (Alternative)

**Database Setup (Docker - Recommended):**
```bash
# Start PostgreSQL database
docker-compose up -d

# Verify database is running
docker-compose ps
```

**Database Connection:**
- Host: localhost:5432
- Database: ems_db
- Username: ems_user
- Password: ems_password

**Installation:**
```bash
# Clone and navigate to project
cd /home/hoangle/ems/ems

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Environment Configuration:**
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
nano .env
```

**Database Migration:**
```bash
# Generate initial migration
python3 migrate.py generate "Initial migration"

# Apply migration to database
python3 migrate.py upgrade

# Check migration status
python3 migrate.py status
```

**Run the Server:**
```bash
# Start the FastAPI server
python3 main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server URLs:**
- **API**: http://localhost:8000/ems
- **API Docs**: http://localhost:8000/ems/docs
- **ReDoc**: http://localhost:8000/ems/redoc
- **Health Check**: http://localhost:8000/ems/health

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- **[Architecture](docs/SRC_ARCHITECTURE.md)**: Complete 3-layer architecture guide
- **[Migrations](docs/MIGRATION_GUIDE.md)**: Database migration system guide
- **[Recovery](docs/RECOVERY.md)**: Recovery and resilience documentation

## 🔧 API Endpoints

### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get a specific user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

### Authentication
- `POST /api/v1/auth/login` - User login with JWT token
- `POST /api/v1/auth/change-password/{user_id}` - Change password

### System
- `GET /` - Root endpoint with API information
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health
- `GET /recovery/status` - Recovery middleware status

## 🎯 Architecture Overview

### 3-Layer Architecture Pattern

1. **Present Layer** (`src/present/`): HTTP handling, routing, middleware, request DTOs
2. **Core Layer** (`src/core/`): Business logic, models, services  
3. **Repository Layer** (`src/repository/`): Data access and database operations

### Additional Layers

4. **Configuration Layer** (`src/config/`): Settings and configuration
5. **Bootstrap Layer** (`src/bootstrap/`): Database initialization and dependency injection

### Data Flow
```
HTTP Request → Router → Controller → Service → Repository → Database
```

## 🛠️ Development

### Makefile Commands

The project includes a comprehensive Makefile for common tasks:

```bash
# See all available commands
make help

# Development workflow
make server-dev              # Start development server
make migrate MSG="message"   # Generate and apply migration
make migrate-generate MSG="message"  # Generate migration only
make health                 # Check server health

# Database management
make db-start              # Start PostgreSQL
make db-stop               # Stop PostgreSQL
make db-reset              # Reset database

# Utilities
make test                  # Run tests
make clean                 # Clean cache files
make status                # Show project status
```

### Database Migrations

**Using Makefile (Recommended):**
```bash
# Generate and apply migration in one command
make migrate MSG="Add new field"

# Or generate migration only (without applying)
make migrate-generate MSG="Add new field"

# Apply existing migrations
make migrate-up

# Check migration status
make migrate-status

# Rollback (if needed)
make migrate-down
```

**Using migrate.py directly:**
```bash
# Generate migration from model changes
python3 migrate.py generate "Add new field"

# Apply migrations
python3 migrate.py upgrade

# View migration history
python3 migrate.py history

# Rollback (if needed)
python3 migrate.py downgrade
```

### Health Monitoring

**Using Makefile (Recommended):**
```bash
# Check all health endpoints with formatted output
make health
```

**Using curl directly:**
```bash
# Check basic health
curl http://localhost:8000/ems/health

# Check detailed health with database status
curl http://localhost:8000/ems/health/detailed

# Check recovery system status
curl http://localhost:8000/ems/recovery/status
```

### Example API Usage

**Create User:**
```bash
curl -X POST "http://localhost:8000/ems/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com", 
       "username": "john_doe",
       "full_name": "John Doe",
       "password": "secure_password"
     }'
```

**User Login:**
```bash
curl -X POST "http://localhost:8000/ems/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "secure_password"
     }'
```

## 🐳 Docker Commands

```bash
# Start database
docker-compose up -d

# Stop database  
docker-compose down

# View logs
docker-compose logs

# Reset database (removes all data)
docker-compose down -v
```

## 🏭 Production

### Environment Variables

Set these in production:

```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-super-secret-key-here
DEBUG=false
APP_NAME=EMS FastAPI Server
ROOT_PATH=/ems
```

### Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## 📖 Key Features

- **🔄 Recovery System**: Global middleware with retry logic and circuit breaker
- **📊 Health Monitoring**: Real-time health checks for all components
- **🗃️ Migration System**: Alembic-based database versioning
- **🏗️ Clean Architecture**: Well-organized 3-layer + config + bootstrap structure  
- **🔐 Security**: JWT authentication and password hashing
- **🚀 Performance**: FastAPI with async support and connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions and support:
- 📧 Open an issue in the repository
- 📚 Check the documentation in `docs/`
- 🔍 Review the API docs at `/docs` endpoint