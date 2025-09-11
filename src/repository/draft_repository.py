from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import re

from .base_repository import BaseRepository
from src.core.models.cv_draft import (
    CVDraft, LanguageDraft, TechnicalSkillDraft, 
    SoftSkillDraft, ProjectDraft, DraftStatusEnum
)

logger = logging.getLogger(__name__)


class CVDraftRepository(BaseRepository[CVDraft]):
    """
    Repository for CV Draft CREATE operations with comprehensive validation.
    
    Handles CV draft creation, approval workflow, and conversion to final CV.
    """
    
    def __init__(self, db: Session):
        """Initialize CV Draft repository with CVDraft model."""
        super().__init__(db, CVDraft)
    
    def create_cv_draft(self, cv_data: Dict[str, Any]) -> CVDraft:
        """
        Create a new CV draft with comprehensive validation.
        
        Args:
            cv_data: Dictionary containing CV draft data
            
        Returns:
            Created CV draft instance
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Step 1: Validation
            validation_errors = self.validate_cv_draft_data(cv_data)
            if validation_errors:
                error_msg = self._format_validation_errors(validation_errors)
                logger.error(f"CV draft creation failed - validation errors: {error_msg}")
                raise ValueError(error_msg)
            
            # Step 2: Set default status if not provided
            if 'status' not in cv_data:
                cv_data['status'] = DraftStatusEnum.DRAFT
            
            # Step 3: Create CV draft using base repository
            cv_draft = self.create(cv_data)
            logger.info(f"Successfully created CV draft: {cv_draft.id} for employee: {cv_draft.id_seta}")
            return cv_draft
            
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            error_msg = self._handle_integrity_error(e, cv_data)
            logger.error(f"CV draft creation failed - integrity error: {error_msg}")
            raise ValueError(error_msg)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"CV draft creation failed - database error: {str(e)}")
            raise ValueError(f"Database error occurred: {str(e)}")
    
    def bulk_create_cv_drafts(self, cvs_data: List[Dict[str, Any]]) -> List[CVDraft]:
        """Create multiple CV drafts in a single transaction."""
        try:
            # Validate all drafts first
            all_errors = {}
            for i, cv_data in enumerate(cvs_data):
                # Set default status if not provided
                if 'status' not in cv_data:
                    cv_data['status'] = DraftStatusEnum.DRAFT
                    
                validation_errors = self.validate_cv_draft_data(cv_data)
                if validation_errors:
                    all_errors[f"CV_Draft_{i+1}"] = validation_errors
            
            if all_errors:
                error_msg = f"Bulk CV draft creation failed - validation errors: {all_errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Cross-validate for duplicates
            self._validate_batch_duplicates(cvs_data)
            
            # Create all CV drafts
            created_drafts = self.bulk_create(cvs_data)
            
            logger.info(f"Successfully bulk created {len(created_drafts)} CV drafts")
            return created_drafts
            
        except ValueError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Bulk CV draft creation failed - database error: {str(e)}")
            raise ValueError(f"Bulk creation failed: {str(e)}")
    
    def validate_cv_draft_data(self, cv_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Comprehensive validation of CV draft data."""
        errors = {}
        
        # Required fields validation
        self._validate_required_fields(cv_data, errors)
        
        # Field format validation
        self._validate_field_formats(cv_data, errors)
        
        # Status validation
        self._validate_status(cv_data, errors)
        
        # Business constraints validation
        self._validate_business_constraints(cv_data, errors)
        
        # Database uniqueness validation
        self._validate_uniqueness_constraints(cv_data, errors)
        
        logger.debug(f"CV draft validation completed with {len(errors)} error types")
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
    
    def _validate_status(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate draft status."""
        status = cv_data.get('status')
        if status:
            if isinstance(status, str):
                # Convert string to enum
                try:
                    status_enum = DraftStatusEnum(status)
                    cv_data['status'] = status_enum
                except ValueError:
                    self._add_error(errors, 'status', f"Invalid status: {status}. Must be one of: DRAFT, APPROVED, REJECTED")
            elif not isinstance(status, DraftStatusEnum):
                self._add_error(errors, 'status', "Status must be a valid DraftStatusEnum")
    
    def _validate_business_constraints(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate business-specific constraints."""
        
        # Email domain validation
        email = cv_data.get('email')
        if email:
            forbidden_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            domain = email.split('@')[1].lower() if '@' in email else ''
            if domain in forbidden_domains:
                self._add_error(errors, 'email', f"Email domain '{domain}' is not allowed")
        
        # SETA ID format validation (must start with EMP)
        id_seta = cv_data.get('id_seta')
        if id_seta:
            if not id_seta.upper().startswith('EMP'):
                self._add_error(errors, 'id_seta', "SETA ID must start with 'EMP' prefix")
    
    def _validate_uniqueness_constraints(self, cv_data: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
        """Validate database uniqueness constraints for drafts."""
        
        # Check email uniqueness in drafts
        email = cv_data.get('email')
        if email:
            existing_email = self.db.query(CVDraft).filter(CVDraft.email == email).first()
            if existing_email:
                self._add_error(errors, 'email', f"Email '{email}' already exists in draft system")
        
        # Check SETA ID uniqueness in drafts
        id_seta = cv_data.get('id_seta')
        if id_seta:
            existing_seta = self.db.query(CVDraft).filter(CVDraft.id_seta == id_seta).first()
            if existing_seta:
                self._add_error(errors, 'id_seta', f"SETA ID '{id_seta}' already exists in draft system")
    
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
    
    # Helper methods
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_seta_id(self, seta_id: str) -> bool:
        """Validate SETA ID format."""
        return (3 <= len(seta_id) <= 50 and 
                re.match(r'^[A-Za-z0-9_-]+$', seta_id))
    
    def _is_valid_full_name(self, name: str) -> bool:
        """Validate full name format (supports Vietnamese characters)."""
        if not (2 <= len(name.strip()) <= 255):
            return False
        # Allow Vietnamese characters, spaces, dots, hyphens, apostrophes
        pattern = r'^[a-zA-ZÀ-ỹ\s\.\-\']+$'
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
            return f"Email '{cv_data.get('email')}' already exists in draft system"
        elif 'id_seta' in error_str:
            return f"Employee ID '{cv_data.get('id_seta')}' already exists in draft system"
        else:
            return f"Database constraint violation: {str(error)}"


class LanguageDraftRepository(BaseRepository[LanguageDraft]):
    """Repository for Language Draft operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, LanguageDraft)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate language draft data."""
        errors = {}
        if not data.get("draft_id") or len(str(data["draft_id"])) != 6:
            errors["draft_id"] = ["Draft ID must be exactly 6 characters"]
        if not data.get("language_name") or len(data["language_name"]) > 100:
            errors["language_name"] = ["Language name is required (max 100 chars)"]
        if data.get("proficiency") and data.get("proficiency") not in ["Native", "Fluent", "Intermediate", "Basic"]:
            errors["proficiency"] = ["Invalid proficiency value"]
        return errors

    def create_language_draft(self, data: Dict[str, Any]) -> LanguageDraft:
        """Create a language draft with validation."""
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class TechnicalSkillDraftRepository(BaseRepository[TechnicalSkillDraft]):
    """Repository for Technical Skill Draft operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, TechnicalSkillDraft)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate technical skill draft data."""
        errors = {}
        if not data.get("draft_id") or len(str(data["draft_id"])) != 6:
            errors["draft_id"] = ["Draft ID must be exactly 6 characters"]
        if not data.get("skill_name") or len(data["skill_name"]) > 255:
            errors["skill_name"] = ["Skill name is required (max 255 chars)"]
        if data.get("category") and data.get("category") not in [
            "Programming Language", "Database", "Framework", "Tool", "Hardware"
        ]:
            errors["category"] = ["Invalid category"]
        return errors

    def create_skill_draft(self, data: Dict[str, Any]) -> TechnicalSkillDraft:
        """Create a technical skill draft with validation."""
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class SoftSkillDraftRepository(BaseRepository[SoftSkillDraft]):
    """Repository for Soft Skill Draft operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, SoftSkillDraft)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate soft skill draft data."""
        errors = {}
        if not data.get("draft_id") or len(str(data["draft_id"])) != 6:
            errors["draft_id"] = ["Draft ID must be exactly 6 characters"]
        if data.get("skill_name") and data.get("skill_name") not in [
            "Communication", "Teamwork", "Problem Solving", "Decision Making",
            "Leadership", "Time Management", "Adaptability", "Other"
        ]:
            errors["skill_name"] = ["Invalid soft skill"]
        return errors

    def create_soft_skill_draft(self, data: Dict[str, Any]) -> SoftSkillDraft:
        """Create a soft skill draft with validation."""
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class ProjectDraftRepository(BaseRepository[ProjectDraft]):
    """Repository for Project Draft operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, ProjectDraft)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate project draft data."""
        errors = {}
        if not data.get("draft_id") or len(str(data["draft_id"])) != 6:
            errors["draft_id"] = ["Draft ID must be exactly 6 characters"]
        if not data.get("project_name") or len(data["project_name"]) > 255:
            errors["project_name"] = ["Project name is required (max 255 chars)"]
        return errors

    def create_project_draft(self, data: Dict[str, Any]) -> ProjectDraft:
        """Create a project draft with validation."""
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)