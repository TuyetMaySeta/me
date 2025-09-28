# alembic/env.py
from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import database bootstrap + Base
from src.core.models.base import Base
from src.config.config import settings

# Import ONLY employee models (cleaned up)
from src.core.models.employee import Employee
from src.core.models.employee_related import (
    EmployeeContact, EmployeeDocument, EmployeeEducation,
    EmployeeCertification, EmployeeProfile, Language,
    EmployeeTechnicalSkill, EmployeeProject, EmployeeChild
)
from src.core.models.employee_session import EmployeeSession
# Alembic Config object
config = context.config

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata của tất cả employee models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,            # So sánh enum types
        compare_server_default=True,  # So sánh default values
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
