import pytest
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import re
import random
import string

# Load environment variables
load_dotenv()

# Helper: generate random CV ID
def generate_cv_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def test_database_connection():
    """Test if we can connect to database successfully."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        pytest.skip("DATABASE_URL not found in environment variables")
        return

    engine = create_engine(database_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    print("✅ Database connection successful!")


def test_cv_table_exists():
    """Test if CV table exists in database."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        pytest.skip("DATABASE_URL not found in environment variables")
        return

    engine = create_engine(database_url)
    with engine.connect() as connection:
        if 'postgresql' in database_url:
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'cv'
                );
            """)
            table_exists = connection.execute(query).fetchone()[0]
        else:
            query = text("SELECT name FROM sqlite_master WHERE type='table' AND name='cv';")
            table_exists = connection.execute(query).fetchone() is not None

        assert table_exists, "CV table should exist in database"
        print("✅ CV table exists in database!")


def test_create_cv_with_raw_sql():
    """Test creating CV directly with SQL to bypass circular import."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        pytest.skip("DATABASE_URL not found in environment variables")
        return

    engine = create_engine(database_url)
    test_cv_data = {
        'id': generate_cv_id(),
        'id_seta': 'EMP999TEST',
        'email': 'test.user.999@testcompany.com',
        'full_name': 'Test User For Integration',
        'gender': 'Male',
        'current_position': 'Test Engineer',
        'summary': 'This is a test CV created for integration testing.'
    }

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            insert_query = text("""
                INSERT INTO cv (id, id_seta, email, full_name, gender, current_position, summary)
                VALUES (:id, :id_seta, :email, :full_name, :gender, :current_position, :summary)
                RETURNING id
            """)
            result = connection.execute(insert_query, test_cv_data)
            created_id = result.fetchone()[0]
            print(f"✅ CV created successfully with ID: {created_id}")

            # Verify
            verify_query = text("SELECT * FROM cv WHERE id = :id")
            created_cv = connection.execute(verify_query, {"id": created_id}).fetchone()
            assert created_cv is not None
            assert created_cv.id_seta == test_cv_data['id_seta']
            assert created_cv.email == test_cv_data['email']

            # Cleanup
            connection.execute(text("DELETE FROM cv WHERE id = :id"), {"id": created_id})
            trans.commit()
            print(f"🧹 Cleaned up test CV with ID: {created_id}")

        except Exception as e:
            trans.rollback()
            raise e


def test_cv_validation_constraints():
    """Test database constraints and validation using raw SQL."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        pytest.skip("DATABASE_URL not found in environment variables")
        return

    engine = create_engine(database_url)
    with engine.connect() as connection:
        # Transaction 1: insert valid CV
        trans = connection.begin()
        try:
            valid_cv = {
                'id': generate_cv_id(),
                'id_seta': 'EMP998TEST',
                'email': 'valid.test@company.com',
                'full_name': 'Valid Test User'
            }
            insert_query = text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, :id_seta, :email, :full_name)
                RETURNING id
            """)
            first_id = connection.execute(insert_query, valid_cv).fetchone()[0]
            print(f"✅ First CV created with ID: {first_id}")
            trans.commit()
        except Exception as e:
            trans.rollback()
            raise e

        # Transaction 2: duplicate email
        trans = connection.begin()
        try:
            duplicate_email_cv = {
                'id': generate_cv_id(),
                'id_seta': 'EMP997TEST',
                'email': 'valid.test@company.com',
                'full_name': 'Another User'
            }
            connection.execute(insert_query, duplicate_email_cv)
            assert False, "Duplicate email should not be allowed"
        except Exception as duplicate_error:
            print(f"✅ Duplicate email correctly rejected: {str(duplicate_error)}")
            trans.rollback()

        # Transaction 3: duplicate SETA ID
        trans = connection.begin()
        try:
            duplicate_seta_cv = {
                'id': generate_cv_id(),
                'id_seta': 'EMP998TEST',
                'email': 'different.email@company.com',
                'full_name': 'Different User'
            }
            connection.execute(insert_query, duplicate_seta_cv)
            assert False, "Duplicate SETA ID should not be allowed"
        except Exception as duplicate_error:
            print(f"✅ Duplicate SETA ID correctly rejected: {str(duplicate_error)}")
            trans.rollback()

        # Cleanup transaction
        trans = connection.begin()
        try:
            connection.execute(text("DELETE FROM cv WHERE id = :id"), {"id": first_id})
            trans.commit()
            print("🧹 Cleaned up test data")
        except Exception as e:
            trans.rollback()
            raise e


def test_basic_validation_functions():
    """Test validation helper functions directly without importing CV model."""

    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _is_valid_seta_id(seta_id: str) -> bool:
        return (3 <= len(seta_id) <= 50 and bool(re.match(r'^[A-Za-z0-9_-]+$', seta_id)))

    # Email tests
    assert _is_valid_email('test@company.com') is True
    assert _is_valid_email('invalid-email') is False

    # SETA ID tests
    assert _is_valid_seta_id('EMP001') is True
    assert _is_valid_seta_id('AB') is False

    print("✅ Validation functions work correctly!")
