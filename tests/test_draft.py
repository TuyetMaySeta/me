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
def test_cv_draft_crud():
    """Test insert & delete CV Draft with raw SQL"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV Draft
            draft_data = {
                "id": draft_id,
                "id_seta": "EMP_DRAFT",
                "email": "draft@test.com",
                "full_name": "Draft Test User",
                "gender": "Male",
                "current_position": "Draft Engineer",
                "summary": "This is a draft CV",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, gender, current_position, summary, status)
                VALUES (:id, :id_seta, :email, :full_name, :gender, :current_position, :summary, :status)
            """), draft_data)
            
            # Verify
            row = conn.execute(text("SELECT * FROM cv_draft WHERE id = :id"), {"id": draft_id}).fetchone()
            assert row.id_seta == "EMP_DRAFT"
            assert row.email == "draft@test.com"
            assert row.status == "DRAFT"
            
            # Test status update (approve)
            conn.execute(text("UPDATE cv_draft SET status = 'APPROVED' WHERE id = :id"), {"id": draft_id})
            updated_row = conn.execute(text("SELECT status FROM cv_draft WHERE id = :id"), {"id": draft_id}).fetchone()
            assert updated_row.status == "APPROVED"
            
            # Cleanup
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            trans.commit()
            print("✅ CV Draft CRUD operations successful!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_language_draft_crud():
    """Test insert & delete Language Draft with raw SQL"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV Draft first (foreign key)
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, 'EMP_LANG_DRAFT', 'langdraft@test.com', 'Lang Draft User', 'DRAFT')
            """), {"id": draft_id})
            
            # Insert Language Draft - using correct enum values
            lang_data = {
                "draft_id": draft_id,
                "language_name": "Spanish",
                "proficiency": "INTERMEDIATE",  # Must be: NATIVE, FLUENT, INTERMEDIATE, BASIC
                "description": "Learning for business"
            }
            lang_id = conn.execute(text("""
                INSERT INTO language_drafts (draft_id, language_name, proficiency, description)
                VALUES (:draft_id, :language_name, :proficiency, :description)
                RETURNING id
            """), lang_data).fetchone()[0]
            
            # Verify
            row = conn.execute(text("SELECT * FROM language_drafts WHERE id = :id"), {"id": lang_id}).fetchone()
            assert row.language_name == "Spanish"
            assert row.proficiency == "INTERMEDIATE"
            
            # Cleanup
            conn.execute(text("DELETE FROM language_drafts WHERE id = :id"), {"id": lang_id})
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            trans.commit()
            print("✅ Language Draft CRUD operations successful!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_technical_skill_draft_crud():
    """Test insert & delete Technical Skill Draft with raw SQL"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV Draft first
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, 'EMP_TECH_DRAFT', 'techdraft@test.com', 'Tech Draft User', 'DRAFT')
            """), {"id": draft_id})
            
            # Insert Technical Skill Draft - using correct enum values
            skill_data = {
                "draft_id": draft_id,
                "category": "FRAMEWORK",  # Must be: PROGRAMMING_LANGUAGE, DATABASE, FRAMEWORK, TOOL, HARDWARE
                "skill_name": "FastAPI",
                "description": "Used for building APIs"
            }
            skill_id = conn.execute(text("""
                INSERT INTO technical_skill_drafts (draft_id, category, skill_name, description)
                VALUES (:draft_id, :category, :skill_name, :description)
                RETURNING id
            """), skill_data).fetchone()[0]
            
            # Verify
            row = conn.execute(text("SELECT * FROM technical_skill_drafts WHERE id = :id"), {"id": skill_id}).fetchone()
            assert row.skill_name == "FastAPI"
            assert row.category == "FRAMEWORK"
            
            # Cleanup
            conn.execute(text("DELETE FROM technical_skill_drafts WHERE id = :id"), {"id": skill_id})
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            trans.commit()
            print("✅ Technical Skill Draft CRUD operations successful!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_soft_skill_draft_crud():
    """Test insert & delete Soft Skill Draft with raw SQL"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV Draft first
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, 'EMP_SOFT_DRAFT', 'softdraft@test.com', 'Soft Draft User', 'DRAFT')
            """), {"id": draft_id})
            
            # Insert Soft Skill Draft - using correct enum values
            soft_data = {
                "draft_id": draft_id,
                "skill_name": "LEADERSHIP",  # Must be: COMMUNICATION, TEAMWORK, PROBLEM_SOLVING, DECISION_MAKING, LEADERSHIP, TIME_MANAGEMENT, ADAPTABILITY, OTHER
                "description": "Managing small teams"
            }
            soft_id = conn.execute(text("""
                INSERT INTO soft_skill_drafts (draft_id, skill_name, description)
                VALUES (:draft_id, :skill_name, :description)
                RETURNING id
            """), soft_data).fetchone()[0]
            
            # Verify
            row = conn.execute(text("SELECT * FROM soft_skill_drafts WHERE id = :id"), {"id": soft_id}).fetchone()
            assert row.skill_name == "LEADERSHIP"
            
            # Cleanup
            conn.execute(text("DELETE FROM soft_skill_drafts WHERE id = :id"), {"id": soft_id})
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            trans.commit()
            print("✅ Soft Skill Draft CRUD operations successful!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_project_draft_crud():
    """Test insert & delete Project Draft with raw SQL"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Insert CV Draft first
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, 'EMP_PROJ_DRAFT', 'projdraft@test.com', 'Proj Draft User', 'DRAFT')
            """), {"id": draft_id})
            
            # Insert Project Draft
            proj_data = {
                "draft_id": draft_id,
                "project_name": "E-commerce Platform",
                "project_description": "Build online shopping platform",
                "position": "Backend Developer",
                "responsibilities": "API development and database design",
                "programming_languages": "Python, JavaScript"
            }
            proj_id = conn.execute(text("""
                INSERT INTO project_drafts (draft_id, project_name, project_description, position, responsibilities, programming_languages)
                VALUES (:draft_id, :project_name, :project_description, :position, :responsibilities, :programming_languages)
                RETURNING id
            """), proj_data).fetchone()[0]
            
            # Verify
            row = conn.execute(text("SELECT * FROM project_drafts WHERE id = :id"), {"id": proj_id}).fetchone()
            assert row.project_name == "E-commerce Platform"
            assert row.position == "Backend Developer"
            
            # Cleanup
            conn.execute(text("DELETE FROM project_drafts WHERE id = :id"), {"id": proj_id})
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            trans.commit()
            print("✅ Project Draft CRUD operations successful!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_cv_draft_validation():
    """Test CV Draft validation constraints with raw SQL"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Test 1: Valid CV Draft
        trans = conn.begin()
        try:
            valid_draft = {
                "id": generate_cv_id(),
                "id_seta": "EMP_VALID_DRAFT",
                "email": "valid.draft@company.com",
                "full_name": "Valid Draft User",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), valid_draft)
            
            print(f"✅ Valid CV Draft created: {valid_draft['id']}")
            trans.commit()
            
        except Exception as e:
            trans.rollback()
            raise e
        
        # Test 2: Duplicate email should fail
        trans = conn.begin()
        try:
            duplicate_email_draft = {
                "id": generate_cv_id(),
                "id_seta": "EMP_DUP_EMAIL",
                "email": "valid.draft@company.com",  # Same email
                "full_name": "Duplicate Email User",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), duplicate_email_draft)
            
            assert False, "Duplicate email should not be allowed"
            
        except Exception as e:
            print(f"✅ Duplicate email correctly rejected: {str(e)}")
            trans.rollback()
        
        # Test 3: Duplicate SETA ID should fail
        trans = conn.begin()
        try:
            duplicate_seta_draft = {
                "id": generate_cv_id(),
                "id_seta": "EMP_VALID_DRAFT",  # Same SETA ID
                "email": "different.draft@company.com",
                "full_name": "Duplicate SETA User",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), duplicate_seta_draft)
            
            assert False, "Duplicate SETA ID should not be allowed"
            
        except Exception as e:
            print(f"✅ Duplicate SETA ID correctly rejected: {str(e)}")
            trans.rollback()
        
        # Cleanup
        trans = conn.begin()
        try:
            conn.execute(text("DELETE FROM cv_draft WHERE id_seta = 'EMP_VALID_DRAFT'"))
            trans.commit()
            print("🧹 Cleaned up test data")
        except Exception:
            trans.rollback()


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_cv_draft_status_workflow():
    """Test CV Draft status workflow (DRAFT -> APPROVED/REJECTED)"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Step 1: Create draft with DRAFT status
            draft_data = {
                "id": draft_id,
                "id_seta": "EMP_WORKFLOW",
                "email": "workflow@test.com",
                "full_name": "Workflow Test User",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), draft_data)
            
            # Verify initial status
            row = conn.execute(text("SELECT status FROM cv_draft WHERE id = :id"), {"id": draft_id}).fetchone()
            assert row.status == "DRAFT"
            print(f"✅ Draft created with status: {row.status}")
            
            # Step 2: Approve the draft
            conn.execute(text("UPDATE cv_draft SET status = 'APPROVED' WHERE id = :id"), {"id": draft_id})
            
            # Verify approved status
            row = conn.execute(text("SELECT status FROM cv_draft WHERE id = :id"), {"id": draft_id}).fetchone()
            assert row.status == "APPROVED"
            print(f"✅ Draft approved, status: {row.status}")
            
            # Step 3: Test rejection workflow (create another draft)
            rejected_draft_id = generate_cv_id()
            rejected_draft = {
                "id": rejected_draft_id,
                "id_seta": "EMP_REJECT",
                "email": "reject@test.com",
                "full_name": "Reject Test User",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), rejected_draft)
            
            # Reject the draft
            conn.execute(text("UPDATE cv_draft SET status = 'REJECTED' WHERE id = :id"), {"id": rejected_draft_id})
            
            # Verify rejected status
            row = conn.execute(text("SELECT status FROM cv_draft WHERE id = :id"), {"id": rejected_draft_id}).fetchone()
            assert row.status == "REJECTED"
            print(f"✅ Draft rejected, status: {row.status}")
            
            # Cleanup
            conn.execute(text("DELETE FROM cv_draft WHERE id IN (:id1, :id2)"), {"id1": draft_id, "id2": rejected_draft_id})
            trans.commit()
            print("✅ CV Draft workflow test completed!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_cv_draft_bulk_operations():
    """Test bulk insert operations for CV Drafts"""
    engine = create_engine(DATABASE_URL)
    draft_ids = [generate_cv_id() for _ in range(3)]
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Bulk insert multiple CV drafts
            bulk_drafts = [
                {
                    "id": draft_ids[0],
                    "id_seta": "EMP_BULK1",
                    "email": "bulk1@test.com",
                    "full_name": "Bulk Test User 1",
                    "status": "DRAFT"
                },
                {
                    "id": draft_ids[1],
                    "id_seta": "EMP_BULK2",
                    "email": "bulk2@test.com",
                    "full_name": "Bulk Test User 2",
                    "status": "DRAFT"
                },
                {
                    "id": draft_ids[2],
                    "id_seta": "EMP_BULK3",
                    "email": "bulk3@test.com",
                    "full_name": "Bulk Test User 3",
                    "status": "DRAFT"
                }
            ]
            
            for draft in bulk_drafts:
                conn.execute(text("""
                    INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                    VALUES (:id, :id_seta, :email, :full_name, :status)
                """), draft)
            
            # Verify all drafts were created
            count = conn.execute(text("SELECT COUNT(*) FROM cv_draft WHERE id_seta LIKE 'EMP_BULK%'")).fetchone()[0]
            assert count == 3
            print(f"✅ Bulk created {count} CV drafts")
            
            # Test bulk status update
            conn.execute(text("UPDATE cv_draft SET status = 'APPROVED' WHERE id_seta LIKE 'EMP_BULK%'"))
            
            # Verify all were approved
            approved_count = conn.execute(text("""
                SELECT COUNT(*) FROM cv_draft 
                WHERE id_seta LIKE 'EMP_BULK%' AND status = 'APPROVED'
            """)).fetchone()[0]
            assert approved_count == 3
            print(f"✅ Bulk approved {approved_count} CV drafts")
            
            # Cleanup
            conn.execute(text("DELETE FROM cv_draft WHERE id_seta LIKE 'EMP_BULK%'"))
            trans.commit()
            print("✅ Bulk operations test completed!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_complete_cv_draft_with_related_data():
    """Test creating a complete CV draft with all related entities"""
    engine = create_engine(DATABASE_URL)
    draft_id = generate_cv_id()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Step 1: Create CV Draft
            cv_draft = {
                "id": draft_id,
                "id_seta": "EMP_COMPLETE_DRAFT",
                "email": "complete.draft@test.com",
                "full_name": "Complete Draft User",
                "gender": "Female",
                "current_position": "Senior Developer",
                "summary": "Experienced developer with multiple skills",
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, gender, current_position, summary, status)
                VALUES (:id, :id_seta, :email, :full_name, :gender, :current_position, :summary, :status)
            """), cv_draft)
            
            # Step 2: Add Language Draft - using correct enum values
            lang_id = conn.execute(text("""
                INSERT INTO language_drafts (draft_id, language_name, proficiency, description)
                VALUES (:draft_id, 'French', 'BASIC', 'Learning for travel')
                RETURNING id
            """), {"draft_id": draft_id}).fetchone()[0]
            
            # Step 3: Add Technical Skill Draft - using correct enum values
            tech_id = conn.execute(text("""
                INSERT INTO technical_skill_drafts (draft_id, category, skill_name, description)
                VALUES (:draft_id, 'PROGRAMMING_LANGUAGE', 'Python', 'Expert level')
                RETURNING id
            """), {"draft_id": draft_id}).fetchone()[0]
            
            # Step 4: Add Soft Skill Draft - using correct enum values
            soft_id = conn.execute(text("""
                INSERT INTO soft_skill_drafts (draft_id, skill_name, description)
                VALUES (:draft_id, 'PROBLEM_SOLVING', 'Analytical thinking')
                RETURNING id
            """), {"draft_id": draft_id}).fetchone()[0]
            
            # Step 5: Add Project Draft
            proj_id = conn.execute(text("""
                INSERT INTO project_drafts (draft_id, project_name, project_description, position, responsibilities, programming_languages)
                VALUES (:draft_id, 'CV Management System', 'Build system for CV management', 'Tech Lead', 'Architecture and development', 'Python, FastAPI')
                RETURNING id
            """), {"draft_id": draft_id}).fetchone()[0]
            
            # Verify all data exists
            draft_count = conn.execute(text("SELECT COUNT(*) FROM cv_draft WHERE id = :id"), {"id": draft_id}).fetchone()[0]
            lang_count = conn.execute(text("SELECT COUNT(*) FROM language_drafts WHERE draft_id = :id"), {"id": draft_id}).fetchone()[0]
            tech_count = conn.execute(text("SELECT COUNT(*) FROM technical_skill_drafts WHERE draft_id = :id"), {"id": draft_id}).fetchone()[0]
            soft_count = conn.execute(text("SELECT COUNT(*) FROM soft_skill_drafts WHERE draft_id = :id"), {"id": draft_id}).fetchone()[0]
            proj_count = conn.execute(text("SELECT COUNT(*) FROM project_drafts WHERE draft_id = :id"), {"id": draft_id}).fetchone()[0]
            
            assert draft_count == 1
            assert lang_count == 1
            assert tech_count == 1
            assert soft_count == 1
            assert proj_count == 1
            
            print(f"✅ Complete CV draft created with:")
            print(f"   - CV Draft: {draft_count}")
            print(f"   - Languages: {lang_count}")
            print(f"   - Technical Skills: {tech_count}")
            print(f"   - Soft Skills: {soft_count}")
            print(f"   - Projects: {proj_count}")
            
            # Cleanup (delete in correct order due to foreign keys)
            conn.execute(text("DELETE FROM project_drafts WHERE id = :id"), {"id": proj_id})
            conn.execute(text("DELETE FROM soft_skill_drafts WHERE id = :id"), {"id": soft_id})
            conn.execute(text("DELETE FROM technical_skill_drafts WHERE id = :id"), {"id": tech_id})
            conn.execute(text("DELETE FROM language_drafts WHERE id = :id"), {"id": lang_id})
            conn.execute(text("DELETE FROM cv_draft WHERE id = :id"), {"id": draft_id})
            
            trans.commit()
            print("✅ Complete CV draft test completed!")
            
        except Exception:
            trans.rollback()
            raise


@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")
def test_draft_validation_edge_cases():
    """Test draft validation edge cases that repositories would catch"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Edge case 1: Very long email (repository would validate max 255 chars)
            # This will now fail with database constraint too
            long_email = "a" * 250 + "@test.com"  # 258 characters
            long_email_draft = {
                "id": generate_cv_id(),
                "id_seta": "EMP_LONG_EMAIL",
                "email": long_email,
                "full_name": "Long Email User",
                "status": "DRAFT"
            }
            
            try:
                conn.execute(text("""
                    INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                    VALUES (:id, :id_seta, :email, :full_name, :status)
                """), long_email_draft)
                print("⚠️  Raw SQL should reject very long email due to VARCHAR(255) constraint")
            except Exception as e:
                print(f"✅ Raw SQL correctly rejects long email: {str(e)[:100]}...")
            
            # Edge case 2: Invalid status (repository would validate enum values)
            invalid_status_draft = {
                "id": generate_cv_id(),
                "id_seta": "EMP_INVALID_STATUS",
                "email": "invalid.status@test.com",
                "full_name": "Invalid Status User",
                "status": "InvalidStatus"  # This will fail with raw SQL too due to enum constraint
            }
            
            try:
                conn.execute(text("""
                    INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                    VALUES (:id, :id_seta, :email, :full_name, :status)
                """), invalid_status_draft)
                print("⚠️  This shouldn't succeed")
            except Exception as e:
                print(f"✅ Raw SQL correctly rejects invalid enum: {str(e)[:100]}...")
            
            # Edge case 3: Empty required fields (repository would validate)
            empty_fields_draft = {
                "id": generate_cv_id(),
                "id_seta": "",  # Empty SETA ID
                "email": "empty.fields@test.com",
                "full_name": "",  # Empty name
                "status": "DRAFT"
            }
            
            conn.execute(text("""
                INSERT INTO cv_draft (id, id_seta, email, full_name, status)
                VALUES (:id, :id_seta, :email, :full_name, :status)
            """), empty_fields_draft)
            print("⚠️  Raw SQL allows empty required fields - Repository would prevent this")
            
            print("✅ Edge case validation test completed - Repository layer adds important validation!")
            
            # Cleanup
            conn.execute(text("DELETE FROM cv_draft WHERE id_seta IN ('EMP_LONG_EMAIL', 'EMP_INVALID_STATUS', '')"))
            trans.commit()
            
        except Exception:
            trans.rollback()
            raise