"""
Test file to verify database connection and CV creation functionality.

This file tests:
1. Database connection
2. BaseRepository CREATE operations  
3. CVRepository CREATE operations with validation
4. Error handling and validation

Run this to ensure everything works before proceeding to next steps.
"""

import pytest
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Adjust imports based on your project structure
from src.repository.base_repository import BaseRepository
from src.repository.cv_repository import CVRepository
from src.core.models.cv import CV
from src.bootstrap.database_bootstrap import database_bootstrap

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDatabaseConnection:
    """Test database connection and basic operations."""
    
    def setup_method(self):
        """Setup test database session."""
        try:
            # Get database session - handle generator properly
            db_generator = database_bootstrap.get_session()
            self.db = next(db_generator)  # Extract session from generator
            self.cv_repo = CVRepository(self.db)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish database connection: {e}")
            raise
    
    def teardown_method(self):
        """Cleanup after each test."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def test_database_connection(self):
        """Test basic database connectivity."""
        try:
            # Simple query to test connection
            result = self.db.execute("SELECT 1").scalar()
            assert result == 1
            logger.info("✅ Database connection test passed")
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            raise
    
    def test_cv_table_exists(self):
        """Test if CV table exists and is accessible."""
        try:
            # Try to query CV table structure
            count = self.db.query(CV).count()
            logger.info(f"✅ CV table accessible, current count: {count}")
        except Exception as e:
            logger.error(f"❌ CV table test failed: {e}")
            raise
    
    def test_create_valid_cv(self):
        """Test creating a valid CV."""
        try:
            # Valid CV data
            cv_data = {
                'id_seta': 'EMP001',
                'email': 'test.employee@company.com',
                'full_name': 'Nguyen Van Test',
                'gender': 'Male',
                'current_position': 'Test Developer',
                'summary': 'This is a test CV for validation'
            }
            
            # Create CV
            created_cv = self.cv_repo.create_cv(cv_data)
            
            # Verify creation
            assert created_cv is not None
            assert created_cv.id is not None
            assert created_cv.email == cv_data['email']
            assert created_cv.id_seta == cv_data['id_seta']
            
            logger.info(f"✅ CV creation test passed - Created CV ID: {created_cv.id}")
            
            # Cleanup - delete test CV
            self.db.delete(created_cv)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ CV creation test failed: {e}")
            raise
    
    def test_validation_errors(self):
        """Test validation error handling."""
        try:
            # Invalid CV data (missing required fields)
            invalid_cv_data = {
                'email': 'invalid-email',  # Invalid format
                'full_name': 'A',  # Too short
                'gender': 'InvalidGender'  # Invalid enum
            }
            
            # Should raise ValueError due to validation errors
            with pytest.raises(ValueError) as exc_info:
                self.cv_repo.create_cv(invalid_cv_data)
            
            error_message = str(exc_info.value)
            assert 'required_fields' in error_message
            assert 'email' in error_message
            
            logger.info("✅ Validation error test passed")
            
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"❌ Validation test failed: {e}")
            raise
    
    def test_duplicate_email_prevention(self):
        """Test duplicate email prevention."""
        try:
            # Create first CV
            cv_data_1 = {
                'id_seta': 'EMP002',
                'email': 'duplicate.test@company.com',
                'full_name': 'First Employee'
            }
            
            created_cv = self.cv_repo.create_cv(cv_data_1)
            assert created_cv is not None
            
            # Try to create second CV with same email
            cv_data_2 = {
                'id_seta': 'EMP003',
                'email': 'duplicate.test@company.com',  # Same email
                'full_name': 'Second Employee'
            }
            
            # Should raise ValueError due to duplicate email
            with pytest.raises(ValueError) as exc_info:
                self.cv_repo.create_cv(cv_data_2)
            
            error_message = str(exc_info.value)
            assert 'already exists' in error_message.lower()
            
            logger.info("✅ Duplicate prevention test passed")
            
            # Cleanup
            self.db.delete(created_cv)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Duplicate prevention test failed: {e}")
            raise
    
    def test_bulk_create_cvs(self):
        """Test bulk CV creation."""
        try:
            # Multiple valid CVs
            cvs_data = [
                {
                    'id_seta': 'EMP004',
                    'email': 'bulk.test1@company.com',
                    'full_name': 'Bulk Test Employee 1'
                },
                {
                    'id_seta': 'EMP005', 
                    'email': 'bulk.test2@company.com',
                    'full_name': 'Bulk Test Employee 2'
                },
                {
                    'id_seta': 'EMP006',
                    'email': 'bulk.test3@company.com', 
                    'full_name': 'Bulk Test Employee 3'
                }
            ]
            
            # Create multiple CVs
            created_cvs = self.cv_repo.bulk_create_cvs(cvs_data)
            
            # Verify creation
            assert len(created_cvs) == 3
            assert all(cv.id is not None for cv in created_cvs)
            
            logger.info(f"✅ Bulk creation test passed - Created {len(created_cvs)} CVs")
            
            # Cleanup
            for cv in created_cvs:
                self.db.delete(cv)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Bulk creation test failed: {e}")
            raise
    
    def test_business_validation(self):
        """Test business rule validation (EMP prefix requirement)."""
        try:
            # Invalid SETA ID format (no EMP prefix)
            cv_data = {
                'id_seta': 'DEV001',  # Should start with EMP
                'email': 'business.test@company.com',
                'full_name': 'Business Test User'
            }
            
            # Should raise ValueError due to business rule violation
            with pytest.raises(ValueError) as exc_info:
                self.cv_repo.create_cv(cv_data)
            
            error_message = str(exc_info.value)
            assert 'EMP' in error_message
            
            logger.info("✅ Business validation test passed")
            
        except Exception as e:
            logger.error(f"❌ Business validation test failed: {e}")
            raise

def run_all_tests():
    """Run all tests and report results."""
    test_class = TestDatabaseConnection()
    tests = [
        'test_database_connection',
        'test_cv_table_exists', 
        'test_create_valid_cv',
        'test_validation_errors',
        'test_duplicate_email_prevention',
        'test_bulk_create_cvs',
        'test_business_validation'
    ]
    
    passed = 0
    failed = 0
    
    print("🧪 Starting CV Repository Tests...")
    print("=" * 50)
    
    for test_name in tests:
        try:
            test_class.setup_method()
            test_method = getattr(test_class, test_name)
            test_method()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            failed += 1
        finally:
            test_class.teardown_method()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Database and CV creation are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check your database connection and models.")
        return False

if __name__ == "__main__":
    # Run tests directly
    success = run_all_tests()
    exit(0 if success else 1)