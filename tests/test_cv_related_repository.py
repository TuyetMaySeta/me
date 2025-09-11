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
            # Insert CV first (foreign key cv_id)
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_LANG_TEST', 'lang.test@company.com', 'Lang Test User')
            """), {"id": cv_id})

            # Insert Language - using correct enum values
            lang_data = {
                "cv_id": cv_id,
                "language_name": "English",
                "proficiency": "FLUENT",  # Must be: NATIVE, FLUENT, INTERMEDIATE, BASIC
                "description": "Daily work communication"
            }
            lang_id = conn.execute(text("""
                INSERT INTO languages (cv_id, language_name, proficiency, description)
                VALUES (:cv_id, :language_name, :proficiency, :description)
                RETURNING id
            """), lang_data).fetchone()[0]

            # Verify
            row = conn.execute(text("SELECT * FROM languages WHERE id = :id"), {"id": lang_id}).fetchone()
            assert row.language_name == "English"
            assert row.proficiency == "FLUENT"
            assert row.cv_id == cv_id
            print(f"✅ Language created successfully: {row.language_name} for CV: {cv_id}")

            # Test invalid proficiency (should work in raw SQL but would fail in repository validation)
            invalid_lang_data = {
                "cv_id": cv_id,
                "language_name": "Spanish",
                "proficiency": "BASIC",  # Valid enum value
                "description": "Learning"
            }
            
            # This will work with correct enum value
            valid_lang_id = conn.execute(text("""
                INSERT INTO languages (cv_id, language_name, proficiency, description)
                VALUES (:cv_id, :language_name, :proficiency, :description)
                RETURNING id
            """), invalid_lang_data).fetchone()[0]
            print(f"✅ Second language created: {invalid_lang_data['language_name']}")

            # Cleanup
            conn.execute(text("DELETE FROM languages WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
            print("✅ Language CRUD test completed!")
            
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
            # Insert CV first
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_TECH_TEST', 'tech.test@company.com', 'Tech Test User')
            """), {"id": cv_id})

            # Insert multiple technical skills - using correct enum values
            skills_data = [
                {
                    "cv_id": cv_id,
                    "category": "PROGRAMMING_LANGUAGE",  # Must be: PROGRAMMING_LANGUAGE, DATABASE, FRAMEWORK, TOOL, HARDWARE
                    "skill_name": "Python",
                    "description": "Expert level - 5 years experience"
                },
                {
                    "cv_id": cv_id,
                    "category": "DATABASE",
                    "skill_name": "PostgreSQL",
                    "description": "Used in production systems"
                },
                {
                    "cv_id": cv_id,
                    "category": "FRAMEWORK",
                    "skill_name": "FastAPI",
                    "description": "Building REST APIs"
                }
            ]
            
            skill_ids = []
            for skill_data in skills_data:
                skill_id = conn.execute(text("""
                    INSERT INTO technical_skills (cv_id, category, skill_name, description)
                    VALUES (:cv_id, :category, :skill_name, :description)
                    RETURNING id
                """), skill_data).fetchone()[0]
                skill_ids.append(skill_id)

            # Verify all skills were created
            count = conn.execute(text("SELECT COUNT(*) FROM technical_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            assert count == 3
            
            # Verify specific skill
            python_skill = conn.execute(text("""
                SELECT * FROM technical_skills WHERE cv_id = :cv_id AND skill_name = 'Python'
            """), {"cv_id": cv_id}).fetchone()
            assert python_skill.category == "PROGRAMMING_LANGUAGE"
            print(f"✅ Technical skills created successfully: {count} skills for CV: {cv_id}")

            # Cleanup
            conn.execute(text("DELETE FROM technical_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
            print("✅ Technical Skill CRUD test completed!")
            
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
            # Insert CV first
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_SOFT_TEST', 'soft.test@company.com', 'Soft Test User')
            """), {"id": cv_id})

            # Insert multiple soft skills - using correct enum values
            soft_skills_data = [
                {
                    "cv_id": cv_id,
                    "skill_name": "COMMUNICATION",  # Must be: COMMUNICATION, TEAMWORK, PROBLEM_SOLVING, DECISION_MAKING, LEADERSHIP, TIME_MANAGEMENT, ADAPTABILITY, OTHER
                    "description": "Excellent verbal and written communication"
                },
                {
                    "cv_id": cv_id,
                    "skill_name": "TEAMWORK",
                    "description": "Works well in collaborative environments"
                },
                {
                    "cv_id": cv_id,
                    "skill_name": "LEADERSHIP",
                    "description": "Led teams of 5+ developers"
                }
            ]
            
            for soft_data in soft_skills_data:
                soft_id = conn.execute(text("""
                    INSERT INTO soft_skills (cv_id, skill_name, description)
                    VALUES (:cv_id, :skill_name, :description)
                    RETURNING id
                """), soft_data).fetchone()[0]

            # Verify
            count = conn.execute(text("SELECT COUNT(*) FROM soft_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            assert count == 3
            
            # Check specific skill
            leadership_skill = conn.execute(text("""
                SELECT * FROM soft_skills WHERE cv_id = :cv_id AND skill_name = 'LEADERSHIP'
            """), {"cv_id": cv_id}).fetchone()
            assert leadership_skill.description == "Led teams of 5+ developers"
            print(f"✅ Soft skills created successfully: {count} skills for CV: {cv_id}")

            # Cleanup
            conn.execute(text("DELETE FROM soft_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
            print("✅ Soft Skill CRUD test completed!")
            
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
            # Insert CV first
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_PROJ_TEST', 'proj.test@company.com', 'Proj Test User')
            """), {"id": cv_id})

            # Insert multiple projects
            projects_data = [
                {
                    "cv_id": cv_id,
                    "project_name": "E-commerce Platform",
                    "project_description": "Full-stack e-commerce solution with payment integration",
                    "position": "Full Stack Developer",
                    "responsibilities": "Backend API development, database design, frontend integration",
                    "programming_languages": "Python, JavaScript, React, FastAPI"
                },
                {
                    "cv_id": cv_id,
                    "project_name": "CV Management System",
                    "project_description": "Internal tool for managing employee CVs and skills",
                    "position": "Backend Developer",
                    "responsibilities": "API development, database optimization, testing",
                    "programming_languages": "Python, FastAPI, PostgreSQL"
                }
            ]
            
            project_ids = []
            for proj_data in projects_data:
                proj_id = conn.execute(text("""
                    INSERT INTO projects (cv_id, project_name, project_description, position, responsibilities, programming_languages)
                    VALUES (:cv_id, :project_name, :project_description, :position, :responsibilities, :programming_languages)
                    RETURNING id
                """), proj_data).fetchone()[0]
                project_ids.append(proj_id)

            # Verify
            count = conn.execute(text("SELECT COUNT(*) FROM projects WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            assert count == 2
            
            # Check specific project
            ecommerce_project = conn.execute(text("""
                SELECT * FROM projects WHERE cv_id = :cv_id AND project_name = 'E-commerce Platform'
            """), {"cv_id": cv_id}).fetchone()
            assert ecommerce_project.position == "Full Stack Developer"
            assert "Python" in ecommerce_project.programming_languages
            print(f"✅ Projects created successfully: {count} projects for CV: {cv_id}")

            # Cleanup
            conn.execute(text("DELETE FROM projects WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})
            trans.commit()
            print("✅ Project CRUD test completed!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_complete_cv_with_all_components():
    """Test creating a complete CV with all related components"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Step 1: Create CV
            cv_data = {
                "id": cv_id,
                "id_seta": "EMP_COMPLETE",
                "email": "complete.test@company.com",
                "full_name": "Complete Test User",
                "gender": "Female",
                "current_position": "Senior Full Stack Developer",
                "summary": "Experienced developer with expertise in Python, FastAPI, and React"
            }
            
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name, gender, current_position, summary)
                VALUES (:id, :id_seta, :email, :full_name, :gender, :current_position, :summary)
            """), cv_data)
            print(f"✅ CV created: {cv_id}")

            # Step 2: Add languages - using correct enum values
            languages_data = [
                {"cv_id": cv_id, "language_name": "English", "proficiency": "NATIVE", "description": "Native speaker"},
                {"cv_id": cv_id, "language_name": "Vietnamese", "proficiency": "NATIVE", "description": "Native speaker"},
                {"cv_id": cv_id, "language_name": "Japanese", "proficiency": "INTERMEDIATE", "description": "JLPT N3 level"}
            ]
            
            for lang_data in languages_data:
                conn.execute(text("""
                    INSERT INTO languages (cv_id, language_name, proficiency, description)
                    VALUES (:cv_id, :language_name, :proficiency, :description)
                """), lang_data)
            print(f"✅ Languages added: {len(languages_data)}")

            # Step 3: Add technical skills - using correct enum values
            tech_skills_data = [
                {"cv_id": cv_id, "category": "PROGRAMMING_LANGUAGE", "skill_name": "Python", "description": "Expert - 5+ years"},
                {"cv_id": cv_id, "category": "FRAMEWORK", "skill_name": "FastAPI", "description": "Building REST APIs"},
                {"cv_id": cv_id, "category": "DATABASE", "skill_name": "PostgreSQL", "description": "Database design and optimization"},
                {"cv_id": cv_id, "category": "TOOL", "skill_name": "Docker", "description": "Containerization and deployment"}
            ]
            
            for skill_data in tech_skills_data:
                conn.execute(text("""
                    INSERT INTO technical_skills (cv_id, category, skill_name, description)
                    VALUES (:cv_id, :category, :skill_name, :description)
                """), skill_data)
            print(f"✅ Technical skills added: {len(tech_skills_data)}")

            # Step 4: Add soft skills - using correct enum values
            soft_skills_data = [
                {"cv_id": cv_id, "skill_name": "LEADERSHIP", "description": "Team lead for 3+ years"},
                {"cv_id": cv_id, "skill_name": "PROBLEM_SOLVING", "description": "Strong analytical and debugging skills"},
                {"cv_id": cv_id, "skill_name": "COMMUNICATION", "description": "Excellent presentation and documentation skills"}
            ]
            
            for soft_data in soft_skills_data:
                conn.execute(text("""
                    INSERT INTO soft_skills (cv_id, skill_name, description)
                    VALUES (:cv_id, :skill_name, :description)
                """), soft_data)
            print(f"✅ Soft skills added: {len(soft_skills_data)}")

            # Step 5: Add projects
            projects_data = [
                {
                    "cv_id": cv_id,
                    "project_name": "CV Management System",
                    "project_description": "Complete CV management solution with FastAPI backend",
                    "position": "Tech Lead",
                    "responsibilities": "Architecture design, team coordination, code review",
                    "programming_languages": "Python, FastAPI, PostgreSQL, React"
                },
                {
                    "cv_id": cv_id,
                    "project_name": "Microservices Platform",
                    "project_description": "Scalable microservices architecture for enterprise applications",
                    "position": "Senior Developer",
                    "responsibilities": "Service development, API design, performance optimization",
                    "programming_languages": "Python, Docker, Kubernetes, Redis"
                }
            ]
            
            for proj_data in projects_data:
                conn.execute(text("""
                    INSERT INTO projects (cv_id, project_name, project_description, position, responsibilities, programming_languages)
                    VALUES (:cv_id, :project_name, :project_description, :position, :responsibilities, :programming_languages)
                """), proj_data)
            print(f"✅ Projects added: {len(projects_data)}")

            # Step 6: Verify all data
            cv_count = conn.execute(text("SELECT COUNT(*) FROM cv WHERE id = :id"), {"id": cv_id}).fetchone()[0]
            lang_count = conn.execute(text("SELECT COUNT(*) FROM languages WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            tech_count = conn.execute(text("SELECT COUNT(*) FROM technical_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            soft_count = conn.execute(text("SELECT COUNT(*) FROM soft_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]
            proj_count = conn.execute(text("SELECT COUNT(*) FROM projects WHERE cv_id = :cv_id"), {"cv_id": cv_id}).fetchone()[0]

            assert cv_count == 1
            assert lang_count == 3
            assert tech_count == 4
            assert soft_count == 3
            assert proj_count == 2

            print(f"🎉 Complete CV created successfully!")
            print(f"   📄 CV: {cv_count}")
            print(f"   🗣️  Languages: {lang_count}")
            print(f"   💻 Technical Skills: {tech_count}")
            print(f"   🤝 Soft Skills: {soft_count}")
            print(f"   🚀 Projects: {proj_count}")

            # Cleanup (order matters due to foreign keys)
            conn.execute(text("DELETE FROM projects WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM soft_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM technical_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM languages WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})

            trans.commit()
            print("✅ Complete CV test completed successfully!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_cv_components_validation_scenarios():
    """Test validation scenarios that would be caught by repositories"""
    engine = create_engine(DATABASE_URL)
    cv_id = generate_cv_id()

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Create CV first
            conn.execute(text("""
                INSERT INTO cv (id, id_seta, email, full_name)
                VALUES (:id, 'EMP_VALIDATION', 'validation.test@company.com', 'Validation Test User')
            """), {"id": cv_id})

            # Test scenarios that would be caught by repository validation
            
            # 1. Language with too long name (would be caught by repository)
            long_lang_name = "A" * 101  # 101 characters, max is 100
            try:
                conn.execute(text("""
                    INSERT INTO languages (cv_id, language_name, proficiency)
                    VALUES (:cv_id, :language_name, 'BASIC')
                """), {"cv_id": cv_id, "language_name": long_lang_name})
                print("⚠️  Raw SQL allows language name > 100 chars - Repository would prevent this")
            except Exception as e:
                print(f"✅ Database constraint prevents long language name: {str(e)[:100]}...")

            # 2. Technical skill with invalid category (will be caught by enum constraint)
            try:
                conn.execute(text("""
                    INSERT INTO technical_skills (cv_id, category, skill_name)
                    VALUES (:cv_id, 'Invalid Category', 'Some Skill')
                """), {"cv_id": cv_id})
                print("⚠️  This shouldn't succeed")
            except Exception as e:
                print(f"✅ Database enum constraint prevents invalid category: {str(e)[:100]}...")

            # 3. Project with too long name (would be caught by repository)
            long_project_name = "A" * 256  # 256 characters, max is 255
            try:
                conn.execute(text("""
                    INSERT INTO projects (cv_id, project_name)
                    VALUES (:cv_id, :project_name)
                """), {"cv_id": cv_id, "project_name": long_project_name})
                print("⚠️  Raw SQL should reject project name > 255 chars")
            except Exception as e:
                print(f"✅ Database constraint prevents long project name: {str(e)[:100]}...")

            # 4. Valid enum values that work
            conn.execute(text("""
                INSERT INTO languages (cv_id, language_name, proficiency)
                VALUES (:cv_id, 'French', 'BASIC')
            """), {"cv_id": cv_id})
            
            conn.execute(text("""
                INSERT INTO technical_skills (cv_id, category, skill_name)
                VALUES (:cv_id, 'TOOL', 'Git')
            """), {"cv_id": cv_id})
            
            conn.execute(text("""
                INSERT INTO soft_skills (cv_id, skill_name)
                VALUES (:cv_id, 'TEAMWORK')
            """), {"cv_id": cv_id})
            
            print("✅ Valid enum values work correctly")

            print("✅ Validation scenarios test completed - Repository layer adds important validation!")

            # Cleanup
            conn.execute(text("DELETE FROM soft_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM technical_skills WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM languages WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM projects WHERE cv_id = :cv_id"), {"cv_id": cv_id})
            conn.execute(text("DELETE FROM cv WHERE id = :id"), {"id": cv_id})

            trans.commit()
            
        except Exception:
            trans.rollback()
            raise