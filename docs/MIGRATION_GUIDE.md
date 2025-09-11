# Database Migration Guide

This guide explains how to generate and manage database migrations from your SQLAlchemy models.

## Overview

The migration system uses Alembic to automatically generate database migrations from your SQLAlchemy models. Migrations are stored in the `migrations/` directory outside the `src/` folder for better organization.

## Project Structure

```
ems/
├── migrations/              # Migration files (outside src/)
│   ├── versions/           # Generated migration files
│   ├── env.py              # Alembic environment configuration
│   └── script.py.mako      # Migration template
├── src/                    # Source code
│   ├── core/models/        # SQLAlchemy models
│   └── bootstrap/          # Database bootstrap
├── alembic.ini             # Alembic configuration
├── migrate.py              # Migration helper script
└── main.py                 # Application entry point
```

## Quick Start

### 1. Generate Initial Migration

```bash
# Generate migration from current models
python migrate.py generate "Initial migration"

# This will create a migration file in migrations/versions/
```

### 2. Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Check current status
python migrate.py status
```

### 3. View Migration History

```bash
# Show all migrations
python migrate.py history

# Show current revision
python migrate.py current
```

## Migration Commands

### Generate Migration

```bash
# Generate migration with custom message
python migrate.py generate "Add user table"

# Generate migration with default message
python migrate.py generate
```

### Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Downgrade to specific revision
python migrate.py downgrade base

# Downgrade to previous revision
python migrate.py downgrade -1
```

### View Status

```bash
# Show current database revision
python migrate.py current

# Show migration history
python migrate.py history

# Show current status and history
python migrate.py status
```

## How It Works

### 1. Model Detection

The migration system automatically detects your SQLAlchemy models by importing them in `migrations/env.py`:

```python
# Import all models to ensure they are registered with Base
from src.core.models.user import User  # Add new models here
```

### 2. Migration Generation

When you run `python migrate.py generate`, Alembic:

1. **Compares** your current models with the database schema
2. **Detects** changes (new tables, columns, indexes, etc.)
3. **Generates** a migration file with the necessary SQL commands
4. **Stores** the migration in `migrations/versions/`

### 3. Migration Application

When you run `python migrate.py upgrade`, Alembic:

1. **Reads** the migration files in order
2. **Applies** only the migrations that haven't been applied yet
3. **Updates** the database schema to match your models
4. **Records** the applied migrations in the database

## Adding New Models

### 1. Create Your Model

```python
# src/core/models/product.py
from sqlalchemy import Column, Integer, String, Float
from src.bootstrap.database_bootstrap import database_bootstrap

Base = database_bootstrap.get_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500))
```

### 2. Import Model in Migration Environment

```python
# migrations/env.py
from src.core.models.user import User
from src.core.models.product import Product  # Add new model here
```

### 3. Generate Migration

```bash
python migrate.py generate "Add product table"
```

### 4. Apply Migration

```bash
python migrate.py upgrade
```

## Modifying Existing Models

### 1. Update Your Model

```python
# src/core/models/user.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add new field
    phone_number = Column(String(20), nullable=True)
```

### 2. Generate Migration

```bash
python migrate.py generate "Add phone number to users"
```

### 3. Apply Migration

```bash
python migrate.py upgrade
```

## Migration File Structure

Generated migration files look like this:

```python
"""Add phone number to users

Revision ID: 001
Revises: 000
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = '000'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade() -> None:
    # Remove column
    op.drop_column('users', 'phone_number')
```

## Best Practices

### 1. Always Review Generated Migrations

```bash
# Generate migration
python migrate.py generate "Add new feature"

# Review the generated file in migrations/versions/
# Edit if necessary before applying
```

### 2. Use Descriptive Messages

```bash
# Good
python migrate.py generate "Add user profile table with avatar field"

# Bad
python migrate.py generate "Update"
```

### 3. Test Migrations

```bash
# Test on development database first
python migrate.py upgrade

# Verify the changes
python migrate.py status
```

### 4. Backup Before Major Changes

```bash
# Create database backup before major migrations
pg_dump ems_db > backup_before_migration.sql

# Apply migration
python migrate.py upgrade
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'src'
   ```
   **Solution**: Make sure you're running from the project root directory

2. **Database Connection Failed**
   ```
   Database connection failed
   ```
   **Solution**: Check your database is running and `DATABASE_URL` is correct

3. **Migration Conflicts**
   ```
   Multiple heads detected
   ```
   **Solution**: Merge the conflicting migrations or reset to a common point

### Reset Migrations

If you need to start fresh:

```bash
# Remove all migration files
rm -rf migrations/versions/*

# Generate new initial migration
python migrate.py generate "Initial migration"

# Apply migration
python migrate.py upgrade
```

## Environment Variables

Make sure these environment variables are set:

```bash
# Database connection
DATABASE_URL=postgresql://username:password@localhost:5432/ems_db

# Application settings
DEBUG=true
APP_NAME=EMS FastAPI Server
```

## Integration with Docker

If using Docker for your database:

```bash
# Start database
docker-compose up -d

# Wait for database to be ready
sleep 10

# Run migrations
python migrate.py upgrade
```

## Advanced Usage

### Custom Migration Scripts

For complex migrations, you can edit the generated migration files:

```python
def upgrade() -> None:
    # Custom migration logic
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
    op.add_column('users', sa.Column('last_login', sa.DateTime()))
```

### Data Migrations

```python
def upgrade() -> None:
    # Add column
    op.add_column('users', sa.Column('full_name', sa.String(100)))
    
    # Migrate data
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = CONCAT(first_name, ' ', last_name)"
    )
    
    # Drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

This migration system provides a robust way to manage your database schema changes alongside your code changes! 🚀
