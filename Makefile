# EMS FastAPI Server Makefile
# Simplifies common development tasks

.PHONY: help install db-start db-stop db-reset migrate migrate-generate migrate-up migrate-down migrate-status server server-dev test clean lint format health

# Default target
help:
	@echo "EMS FastAPI Server - Available Commands:"
	@echo ""
	@echo "🚀 Server Commands:"
	@echo "  make server          Start production server"
	@echo "  make server-dev      Start development server with reload"
	@echo "  make health          Check server health"
	@echo ""
	@echo "🗃️  Database Commands:"
	@echo "  make db-start        Start PostgreSQL database (Docker)"
	@echo "  make db-stop         Stop PostgreSQL database"
	@echo "  make db-reset        Reset database (removes all data)"
	@echo ""
	@echo "📦 Migration Commands:"
	@echo "  make migrate MSG='message'           Generate and apply migration"
	@echo "  make migrate-generate MSG='message'  Generate new migration only"
	@echo "  make migrate-up                      Apply all pending migrations"
	@echo "  make migrate-down                    Rollback last migration"
	@echo "  make migrate-status                  Check migration status"
	@echo ""
	@echo "🛠️  Development Commands:"
	@echo "  make install         Install dependencies"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linting checks"
	@echo "  make format         Format code"
	@echo "  make clean          Clean cache and temp files"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make migrate MSG='Add user profile table'"
	@echo "  make migrate-generate MSG='Add user profile table'"
	@echo "  make server-dev"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Database Management
db-start:
	@echo "🚀 Starting PostgreSQL database..."
	docker-compose up -d
	@echo "✅ Database started successfully!"
	@echo "📊 Database info:"
	@echo "   Host: localhost:5432"
	@echo "   Database: ems_db"
	@echo "   Username: ems_user"

db-stop:
	@echo "🛑 Stopping PostgreSQL database..."
	docker-compose down
	@echo "✅ Database stopped successfully!"

db-reset:
	@echo "⚠️  Resetting database (this will remove all data)..."
	@read -p "Are you sure? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v && \
		docker-compose up -d && \
		echo "✅ Database reset successfully!"; \
	else \
		echo "❌ Database reset cancelled."; \
	fi

# Migration Management
migrate:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Migration message required."; \
		echo "Usage: make migrate MSG='your migration message'"; \
		exit 1; \
	fi
	@echo "🚀 Generating and applying migration: $(MSG)..."
	@echo "📝 Step 1: Generating migration..."
	python3 migrate.py generate "$(MSG)"
	@echo "📈 Step 2: Applying migration..."
	python3 migrate.py upgrade
	@echo "✅ Migration generated and applied successfully!"

migrate-generate:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Migration message required."; \
		echo "Usage: make migrate-generate MSG='your migration message'"; \
		exit 1; \
	fi
	@echo "📝 Generating migration: $(MSG)..."
	python3 migrate.py generate "$(MSG)"
	@echo "✅ Migration generated successfully!"

migrate-up:
	@echo "📈 Applying migrations..."
	python3 migrate.py upgrade
	@echo "✅ Migrations applied successfully!"

migrate-down:
	@echo "📉 Rolling back last migration..."
	@read -p "Are you sure you want to rollback? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		python3 migrate.py downgrade; \
		echo "✅ Migration rolled back successfully!"; \
	else \
		echo "❌ Rollback cancelled."; \
	fi

migrate-status:
	@echo "📊 Migration status:"
	python3 migrate.py status

# Server Management
server:
	@echo "🚀 Starting production server..."
	@echo "📊 Server will be available at:"
	@echo "   API: http://localhost:8000/ems"
	@echo "   Docs: http://localhost:8000/ems/docs"
	python3 main.py

server-dev:
	@echo "🔧 Starting development server with auto-reload..."
	@echo "📊 Server will be available at:"
	@echo "   API: http://localhost:8000/ems"
	@echo "   Docs: http://localhost:8000/ems/docs"
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Health Check
health:
	@echo "🔍 Checking server health..."
	@curl -s http://localhost:8000/ems/health | python3 -m json.tool || echo "❌ Server is not running or health endpoint failed"
	@echo ""
	@echo "🔍 Checking detailed health..."
	@curl -s http://localhost:8000/ems/health/detailed | python3 -m json.tool || echo "❌ Detailed health endpoint failed"
	@echo ""
	@echo "🔍 Checking recovery status..."
	@curl -s http://localhost:8000/ems/recovery/status | python3 -m json.tool || echo "❌ Recovery status endpoint failed"

# Development Tools
test:
	@echo "🧪 Running tests..."
	pytest -v
	@echo "✅ Tests completed!"

lint:
	@echo "🔍 Running linting checks..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics; \
	else \
		echo "⚠️  flake8 not installed. Install with: pip install flake8"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/; \
	else \
		echo "⚠️  mypy not installed. Install with: pip install mypy"; \
	fi
	@echo "✅ Linting completed!"

format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black src/ tests/; \
		echo "✅ Code formatted with black"; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort src/ tests/; \
		echo "✅ Imports sorted with isort"; \
	else \
		echo "⚠️  isort not installed. Install with: pip install isort"; \
	fi

clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Quick Setup (for new environments)
setup: install db-start migrate-up
	@echo "🎉 Setup completed! Your EMS server is ready."
	@echo "💡 Run 'make server-dev' to start the development server."

# Quick Start (for existing environments)
start: db-start migrate-up server-dev

# Production Deployment
deploy: install migrate-up server

# Development Workflow
dev-reset: db-reset migrate-up
	@echo "🔄 Development environment reset completed!"

# Show project status
status:
	@echo "📊 EMS FastAPI Server Status:"
	@echo ""
	@echo "🗃️  Database:"
	@docker-compose ps 2>/dev/null || echo "   Docker Compose not available"
	@echo ""
	@echo "📦 Migration Status:"
	@python3 migrate.py status 2>/dev/null || echo "   Migration status unavailable"
	@echo ""
	@echo "🔍 Server Health (if running):"
	@curl -s http://localhost:8000/ems/health >/dev/null 2>&1 && echo "   ✅ Server is running" || echo "   ❌ Server is not running"
