#!/usr/bin/env python3
"""
Migration script for EMS FastAPI application
Generates and runs database migrations from SQLAlchemy models
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    try:
        from src.bootstrap.database_bootstrap import database_bootstrap
        if database_bootstrap.test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def generate_migration(message="Auto-generated migration"):
    """Generate a new migration from models"""
    if not check_database_connection():
        print("❌ Cannot generate migration: Database not accessible")
        return False
    
    command = f'alembic revision --autogenerate -m "{message}"'
    return run_command(command, f"Generating migration: {message}")

def upgrade_database():
    """Apply all pending migrations"""
    if not check_database_connection():
        print("❌ Cannot upgrade database: Database not accessible")
        return False
    
    return run_command("alembic upgrade head", "Upgrading database to latest migration")

def downgrade_database(revision="base"):
    """Downgrade database to a specific revision"""
    if not check_database_connection():
        print("❌ Cannot downgrade database: Database not accessible")
        return False
    
    return run_command(f"alembic downgrade {revision}", f"Downgrading database to {revision}")

def show_migration_history():
    """Show migration history"""
    return run_command("alembic history", "Showing migration history")

def show_current_revision():
    """Show current database revision"""
    return run_command("alembic current", "Showing current database revision")

def main():
    """Main migration script"""
    print("🚀 EMS FastAPI Migration Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command> [options]")
        print("\nCommands:")
        print("  generate [message]  - Generate new migration from models")
        print("  upgrade            - Apply all pending migrations")
        print("  downgrade [rev]    - Downgrade to specific revision")
        print("  history            - Show migration history")
        print("  current            - Show current revision")
        print("  status             - Show current status")
        print("\nExamples:")
        print("  python migrate.py generate 'Add user table'")
        print("  python migrate.py upgrade")
        print("  python migrate.py downgrade base")
        print("  python migrate.py history")
        return
    
    command = sys.argv[1].lower()
    
    if command == "generate":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto-generated migration"
        generate_migration(message)
    
    elif command == "upgrade":
        upgrade_database()
    
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "base"
        downgrade_database(revision)
    
    elif command == "history":
        show_migration_history()
    
    elif command == "current":
        show_current_revision()
    
    elif command == "status":
        show_current_revision()
        print("\n" + "=" * 50)
        show_migration_history()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python migrate.py' for usage information")

if __name__ == "__main__":
    main()
