import pytest
import os
import random
import string
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Helper: random CV ID
def generate_cv_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_language_crud():
    """Test insert & delete Language with raw SQL"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV trước (foreign key cv_id)
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_LANG', 'lang@test.com', 'Lang Test User')
            """), {"id": cv_id})

            # Insert Language
            lang_data = {
                "cv_id": cv_id,
                "language_name": "English",
                "proficiency": "Fluent",
                "description": "Daily work"
            }
            lang_id = conn.execute(text("""
                INSERT INTO languages (cv_id, language_name, proficiency, description)
                VALUES (:cv_id, :language_name, :proficiency, :description)
                RETURNING id
            """), lang_data).fetchone()[0]

            # Verify
            row = conn.execute(text("SELECT * FROM languages WHERE id = :id"), {"id": lang_id}).fetchone()
            assert row.language_name == "English"

            # Cleanup
            conn.execute(text("DELETE FROM languages WHERE id = :id"), {"id": lang_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_technical_skill_crud():
    """Test insert & delete TechnicalSkill with raw SQL"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV trước
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_TECH', 'tech@test.com', 'Tech Test User')
            """), {"id": cv_id})

            # Insert skill
            skill_data = {
                "cv_id": cv_id,
                "category": "Database",
                "skill_name": "PostgreSQL",
                "description": "Used in production"
            }
            skill_id = conn.execute(text("""
                INSERT INTO technical_skills (cv_id, category, skill_name, description)
                VALUES (:cv_id, :category, :skill_name, :description)
                RETURNING id
            """), skill_data).fetchone()[0]

            # Verify
            row = conn.execute(text("SELECT * FROM technical_skills WHERE id = :id"), {"id": skill_id}).fetchone()
            assert row.skill_name == "PostgreSQL"

            # Cleanup
            conn.execute(text("DELETE FROM technical_skills WHERE id = :id"), {"id": skill_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_soft_skill_crud():
    """Test insert & delete SoftSkill with raw SQL"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV trước
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_SOFT', 'soft@test.com', 'Soft Test User')
            """), {"id": cv_id})

            # Insert soft skill
            soft_data = {
                "cv_id": cv_id,
                "skill_name": "Teamwork",
                "description": "Good team player"
            }
            soft_id = conn.execute(text("""
                INSERT INTO soft_skills (cv_id, skill_name, description)
                VALUES (:cv_id, :skill_name, :description)
                RETURNING id
            """), soft_data).fetchone()[0]

            # Verify
            row = conn.execute(text("SELECT * FROM soft_skills WHERE id = :id"), {"id": soft_id}).fetchone()
            assert row.skill_name == "Teamwork"

            # Cleanup
            conn.execute(text("DELETE FROM soft_skills WHERE id = :id"), {"id": soft_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_project_crud():
    """Test insert & delete Project with raw SQL"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV trước
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_PROJ', 'proj@test.com', 'Proj Test User')
            """), {"id": cv_id})

            # Insert project
            proj_data = {
                "cv_id": cv_id,
                "project_name": "AI Chatbot",
                "project_description": "Build chatbot with FastAPI",
                "position": "Developer",
                "responsibilities": "Backend APIs",
                "programming_languages": "Python"
            }
            proj_id = conn.execute(text("""
                INSERT INTO projects (cv_id, project_name, project_description, position, responsibilities, programming_languages)
                VALUES (:cv_id, :project_name, :project_description, :position, :responsibilities, :programming_languages)
                RETURNING id
            """), proj_data).fetchone()[0]

            # Verify
            row = conn.execute(text("SELECT * FROM projects WHERE id = :id"), {"id": proj_id}).fetchone()
            assert row.project_name == "AI Chatbot"

            # Cleanup
            conn.execute(text("DELETE FROM projects WHERE id = :id"), {"id": proj_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
        except Exception:
            trans.rollback()
            raise
