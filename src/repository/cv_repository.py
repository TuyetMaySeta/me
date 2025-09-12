from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
import logging
import re

from .base_repository import BaseRepository
from ..core.models.cv import CV

logger = logging.getLogger(__name__)

class CVRepository(BaseRepository[CV]):
    """
    Repository for CV CREATE operations with comprehensive validation.
    
    Handles CV creation with detailed validation, business rules enforcement,
    and error handling. All other CRUD operations inherited from BaseRepository.
    """
    
    def __init__(self, db: Session):
        """Initialize CV repository with CV model."""
        super().__init__(db, CV)
    
    # ==================== CREATE OPERATIONS ====================
    
    def create_cv(self, cv_data: Dict[str, Any]) -> CV:
        """
        Create a new CV with comprehensive validation.
        
        Args:
            cv_data: Dictionary containing CV data:
                Required fields:
                - id_seta: Employee SETA ID (unique, 3-50 chars, alphanumeric)
                - email: Employee email (unique, valid format, max 255 chars)
                - full_name: Employee full name (2-255 chars, Vietnamese names allowed)
                
                Optional fields:
                - gender: 'Male', 'Female', or 'Other'
                - current_position: Current position (2-255 chars)
                - summary: CV summary (max 5000 chars)
            
        Returns:
            Created CV instance with auto-generated ID
            
        Raises:
            ValueError: If validation fails with detailed error messages
            SQLAlchemyError: If database operation fails
        """
        try:
            # Step 1: Comprehensive validation
            validation_errors = self.validate_cv_data(cv_data)
            if validation_errors:
                error_msg = self._format_validation_errors(validation_errors)
                logger.error(f"CV creation failed - validation errors: {error_msg}")
                raise ValueError(error_msg)
            
            # Step 2: Additional business validation
            self._validate_business_rules(cv_data)
            
            # Step 3: Create CV using base repository
            cv = self.create(cv_data)
            logger.info(f"Successfully created CV: {cv.id} for employee: {cv.id_seta}")
            return cv
            
        except ValueError:
            # Re-raise validation errors as-is
            raise
        except IntegrityError as e:
            self.db.rollback()
            # Handle database constraint violations
            error_msg = self._handle_integrity_error(e, cv_data)
            logger.error(f"CV creation failed - integrity error: {error_msg}")
            raise ValueError(error_msg)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"CV creation failed - database error: {str(e)}")
            raise ValueError(f"Database error occurred: {str(e)}")
        
    # ==================== VALIDATION METHODS ====================
    
    def validate_cv_data(self, cv_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Comprehensive validation of CV data.
        
        Args:
            cv_data: Dictionary containing CV data to validate
            
        Returns:
            Dictionary with validation errors grouped by field (empty if valid)
        """
        errors = {}
        
        # Required fields validation
        self._validate_required_fields(cv_data, errors)
        
        # Field format validation
        self._validate_field_formats(cv_data, errors)
        
        # Business constraints validation
        self._validate_business_constraints(cv_data, errors)
        
        # Database uniqueness validation (if not bulk operation)
        self._validate_uniqueness_constraints(cv_data, errors)
        
        logger.debug(f"CV validation completed with {len(errors)} error types")
        return errors
    
    def _validate_required_fields(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate required fields are present and not empty."""
        required_fields = {
            'id_seta': 'Employee SETA ID',
            'email': 'Email address', 
            'full_name': 'Full name'
        }
        
        for field, display_name in required_fields.items():
            value = cv_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                self._add_error(errors, 'required_fields', f"{display_name} is required and cannot be empty")
    
    def _validate_field_formats(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate field formats and data constraints."""
        
        # Email format validation
        email = cv_data.get('email')
        if email:
            if not self._is_valid_email(email):
                self._add_error(errors, 'email', "Invalid email format")
            elif len(email) > 255:
                self._add_error(errors, 'email', "Email must not exceed 255 characters")
        
        # ID SETA format validation
        id_seta = cv_data.get('id_seta')
        if id_seta:
            if not self._is_valid_seta_id(id_seta):
                self._add_error(errors, 'id_seta', "SETA ID must be 3-50 characters, alphanumeric only")
        
        # Full name validation
        full_name = cv_data.get('full_name')
        if full_name:
            if not self._is_valid_full_name(full_name):
                self._add_error(errors, 'full_name', "Full name must be 2-255 characters, letters only")
        
        # Gender validation
        gender = cv_data.get('gender')
        if gender and gender not in ['Male', 'Female', 'Other']:
            self._add_error(errors, 'gender', "Gender must be 'Male', 'Female', or 'Other'")
        
        # Current position validation
        position = cv_data.get('current_position')
        if position and not self._is_valid_position(position):
            self._add_error(errors, 'current_position', "Position must be 2-255 characters")
        
        # Summary validation
        summary = cv_data.get('summary')
        if summary and len(summary) > 5000:
            self._add_error(errors, 'summary', "Summary must not exceed 5000 characters")
    
    def _validate_business_constraints(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate business-specific constraints."""
        
        # Email domain validation (if company has domain restrictions)
        email = cv_data.get('email')
        if email:
            forbidden_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            domain = email.split('@')[1].lower() if '@' in email else ''
            if domain in forbidden_domains:
                self._add_error(errors, 'email', f"Email domain '{domain}' is not allowed")
        
        # SETA ID format validation (company-specific format)
        id_seta = cv_data.get('id_seta')
        if id_seta:
            # Example: Must start with 'EMP' for employees
            if not id_seta.upper().startswith('EMP'):
                self._add_error(errors, 'id_seta', "SETA ID must start with 'EMP' prefix")
    
    def _validate_uniqueness_constraints(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate database uniqueness constraints."""
        
        # Check email uniqueness
        email = cv_data.get('email')
        if email:
            existing_email = self.db.query(CV).filter(CV.email == email).first()
            if existing_email:
                self._add_error(errors, 'email', f"Email '{email}' already exists in the system")
        
        # Check SETA ID uniqueness
        id_seta = cv_data.get('id_seta')
        if id_seta:
            existing_seta = self.db.query(CV).filter(CV.id_seta == id_seta).first()
            if existing_seta:
                self._add_error(errors, 'id_seta', f"SETA ID '{id_seta}' already exists in the system")
    
    def _validate_batch_duplicates(self, cvs_data: List[Dict[str, Any]]) -> None:
        """Validate no duplicates within the batch itself."""
        emails = []
        seta_ids = []
        
        for i, cv_data in enumerate(cvs_data):
            email = cv_data.get('email')
            seta_id = cv_data.get('id_seta')
            
            if email in emails:
                raise ValueError(f"Duplicate email '{email}' found in batch at position {i+1}")
            if seta_id in seta_ids:
                raise ValueError(f"Duplicate SETA ID '{seta_id}' found in batch at position {i+1}")
            
            if email:
                emails.append(email)
            if seta_id:
                seta_ids.append(seta_id)
    
    def _validate_business_rules(self, cv_data: Dict[str, Any]) -> None:
        """Additional business rule validation."""
        
        # Example: Senior positions require summary
        position = cv_data.get('current_position', '').lower()
        if 'senior' in position or 'lead' in position:
            if not cv_data.get('summary', '').strip():
                raise ValueError("Senior/Lead positions require a summary")
    
    # ==================== HELPER METHODS ====================
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_seta_id(self, seta_id: str) -> bool:
        """Validate SETA ID format."""
        return (3 <= len(seta_id) <= 50 and 
                re.match(r'^[A-Za-z0-9_-]+$', seta_id))
    
    def _is_valid_full_name(self, name: str) -> bool:
        """Validate full name format (English only)."""
        if not (2 <= len(name.strip()) <= 255):
            return False
        # Allow only English letters, spaces, dots, hyphens, apostrophes
        pattern = r'^[a-zA-Z\s\.\-\']+$'
        return bool(re.match(pattern, name))
    
    def _is_valid_position(self, position: str) -> bool:
        """Validate position format."""
        return 2 <= len(position.strip()) <= 255
    
    def _add_error(self, errors: Dict[str, List[str]], field: str, message: str) -> None:
        """Helper to add validation error."""
        if field not in errors:
            errors[field] = []
        errors[field].append(message)
    
    def _format_validation_errors(self, errors: Dict[str, List[str]]) -> str:
        """Format validation errors for display."""
        formatted_errors = []
        for field, messages in errors.items():
            formatted_errors.append(f"{field}: {'; '.join(messages)}")
        return " | ".join(formatted_errors)
    
    def _handle_integrity_error(self, error: IntegrityError, cv_data: Dict[str, Any]) -> str:
        """Handle database integrity constraint violations."""
        error_str = str(error).lower()
        
        if 'email' in error_str:
            return f"Email '{cv_data.get('email')}' already exists in the system"
        elif 'id_seta' in error_str:
            return f"Employee ID '{cv_data.get('id_seta')}' already exists in the system"
        else:
            return f"Database constraint violation: {str(error)}"