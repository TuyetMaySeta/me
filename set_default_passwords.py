#!/usr/bin/env python3
"""
Script to set default passwords for existing employees
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import sau khi đã set path
from src.bootstrap.database_bootstrap import database_bootstrap
from src.core.utils.password_utils import hash_password, generate_default_password
from sqlalchemy import text

def main():
    print("Setting default passwords for existing employees...")
    
    try:
        db = database_bootstrap.SessionLocal()
        
        try:
            # Hash default password
            default_password = generate_default_password()
            default_password_hash = hash_password(default_password)
            current_time = datetime.now(timezone.utc)  # Thay vì datetime.utcnow()
            
            # Update employees with null passwords
            result = db.execute(text("""
                UPDATE employees 
                SET password_hash = :password_hash,
                    password_is_changed_at = :current_time,
                    is_password_default = true
                WHERE password_hash IS NULL
            """), {
                "password_hash": default_password_hash,
                "current_time": current_time
            })
            
            db.commit()
            count = result.rowcount
            
            print(f"Successfully set default passwords for {count} employees")
            print(f"Default password: {default_password}")
            print("Employees should change passwords on first login")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()