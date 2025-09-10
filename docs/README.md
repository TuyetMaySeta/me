# EMS FastAPI Server - Documentation

This directory contains detailed documentation for the EMS FastAPI Server project.

## 📚 Documentation Index

### 🏗️ [SRC_ARCHITECTURE.md](SRC_ARCHITECTURE.md)
Complete guide to the 3-layer architecture implementation:
- **Present Layer**: Controllers, routers, middleware, request DTOs
- **Core Layer**: Business logic, models, services
- **Repository Layer**: Data access and database operations
- **Configuration Layer**: Settings and configuration management
- **Bootstrap Layer**: Database initialization and dependency injection

### 🔄 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
Comprehensive database migration system documentation:
- How to generate migrations from SQLAlchemy models
- Migration commands and best practices
- Alembic configuration and usage
- Step-by-step migration workflow

### 🛡️ [RECOVERY.md](RECOVERY.md)
Recovery and resilience system documentation:
- Global recovery middleware implementation
- Circuit breaker pattern and retry logic
- Health monitoring and status endpoints
- Graceful shutdown and startup procedures
- Database connection management

## 🚀 Quick Reference

### Common Commands

**Database Migrations:**
```bash
python3 migrate.py generate "Description"  # Generate migration
python3 migrate.py upgrade                 # Apply migrations
python3 migrate.py status                  # Check status
```

**Health Monitoring:**
```bash
curl http://localhost:8000/ems/health           # Basic health
curl http://localhost:8000/ems/health/detailed  # Detailed health
curl http://localhost:8000/ems/recovery/status  # Recovery status
```

**Development:**
```bash
python3 main.py                    # Start server
docker-compose up -d               # Start database
pytest                            # Run tests
```

## 📖 Getting Started

1. **Start Here**: Read the main [README.md](../README.md) for quick setup
2. **Understand Architecture**: Review [SRC_ARCHITECTURE.md](SRC_ARCHITECTURE.md)
3. **Database Setup**: Follow [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
4. **System Monitoring**: Learn about [RECOVERY.md](RECOVERY.md)

## 🤝 Contributing

When adding new features:
1. Update relevant documentation in this folder
2. Follow the 3-layer architecture pattern
3. Add appropriate tests
4. Update the main README if needed

For questions about the documentation or architecture, please open an issue in the repository.
