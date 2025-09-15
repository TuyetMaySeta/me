# src/core/services/employee_related_service.py
import logging
from typing import Dict, Any, List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.present.request.employee_related import (
    LanguageCreateRequest, LanguageUpdateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillUpdateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillUpdateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    BulkComponentCreateRequest, BulkComponentResponse
)
from src.repository.employee_related_repository import (
    EmployeeLanguageRepository, EmployeeTechnicalSkillRepository,
    EmployeeSoftSkillRepository, EmployeeProjectRepository, EmployeeRelatedBulkOperations
)
from src.repository.employee_repository import EmployeeRepository
from src.common.exception.exceptions import (
    ValidationException, ConflictException, 
    NotFoundException, InternalServerException
)

logger = logging.getLogger(__name__)


class EmployeeRelatedService:
    """Service for Employee related entities (Languages, Skills, Projects)"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.employee_repository = EmployeeRepository(db_session)
        self.language_repo = EmployeeLanguageRepository(db_session)
        self.tech_skill_repo = EmployeeTechnicalSkillRepository(db_session)
        self.soft_skill_repo = EmployeeSoftSkillRepository(db_session)
        self.project_repo = EmployeeProjectRepository(db_session)
        self.bulk_operations = EmployeeRelatedBulkOperations(db_session)
    
    def _check_employee_exists(self, employee_id: str) -> None:
        """Check if Employee exists, raise NotFoundException if not"""
        if not self.employee_repository.employee_exists(employee_id):
            logger.warning(f"Employee with ID {employee_id} not found")
            raise NotFoundException(
                f"Employee with ID '{employee_id}' not found. Cannot create related data.",
                "EMPLOYEE_NOT_FOUND"
            )

    # ===================== LANGUAGE OPERATIONS =====================
    
    def create_language(self, request: LanguageCreateRequest) -> LanguageResponse:
        """Create a new language for an Employee"""
        logger.info(f"Creating language '{request.language_name}' for Employee: {request.employee_id}")
        
        try:
            self._check_employee_exists(request.employee_id)
            
            language_data = {
                "employee_id": request.employee_id,
                "language_name": request.language_name,
                "proficiency": request.proficiency.value,
                "description": request.description
            }
            
            language = self.language_repo.create_language(language_data)
            logger.info(f"Language created successfully: {language.language_name} (ID: {language.id})")
            
            return LanguageResponse.model_validate(language)
            
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating language: {str(e)}")
            raise InternalServerException(f"Language creation failed: {str(e)}", "LANGUAGE_CREATION_ERROR")

    def get_language(self, lang_id: int) -> LanguageResponse:
        """Get language by ID"""
        logger.info(f"Getting language: {lang_id}")
        
        language = self.language_repo.get_language_by_id(lang_id)
        if not language:
            raise NotFoundException(f"Language with ID {lang_id} not found", "LANGUAGE_NOT_FOUND")
        
        return LanguageResponse.model_validate(language)

    def get_languages_by_employee(self, employee_id: str) -> List[LanguageResponse]:
        """Get all languages for an Employee"""
        logger.info(f"Getting languages for Employee: {employee_id}")
        
        self._check_employee_exists(employee_id)
        languages = self.language_repo.get_languages_by_employee_id(employee_id)
        
        return [LanguageResponse.model_validate(lang) for lang in languages]

    def update_language(self, lang_id: int, request: LanguageUpdateRequest) -> LanguageResponse:
        """Update language by ID"""
        logger.info(f"Updating language: {lang_id}")
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            if 'proficiency' in update_data:
                update_data['proficiency'] = update_data['proficiency'].value
            
            updated_language = self.language_repo.update_language(lang_id, update_data)
            if not updated_language:
                raise NotFoundException(f"Language with ID {lang_id} not found", "LANGUAGE_NOT_FOUND")
            
            logger.info(f"Language updated successfully: {lang_id}")
            return LanguageResponse.model_validate(updated_language)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error updating language {lang_id}: {str(e)}")
            raise InternalServerException(f"Language update failed: {str(e)}", "LANGUAGE_UPDATE_ERROR")

    def delete_language(self, lang_id: int) -> None:
        """Delete language by ID"""
        logger.info(f"Deleting language: {lang_id}")
        
        try:
            if not self.language_repo.delete_language(lang_id):
                raise NotFoundException(f"Language with ID {lang_id} not found", "LANGUAGE_NOT_FOUND")
            
            logger.info(f"Language deleted successfully: {lang_id}")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting language {lang_id}: {str(e)}")
            raise InternalServerException(f"Language deletion failed: {str(e)}", "LANGUAGE_DELETE_ERROR")

    # ===================== TECHNICAL SKILL OPERATIONS =====================
    
    def create_technical_skill(self, request: TechnicalSkillCreateRequest) -> TechnicalSkillResponse:
        """Create a new technical skill for an Employee"""
        logger.info(f"Creating technical skill '{request.skill_name}' for Employee: {request.employee_id}")
        
        try:
            self._check_employee_exists(request.employee_id)
            
            skill_data = {
                "employee_id": request.employee_id,
                "category": request.category.value,
                "skill_name": request.skill_name,
                "description": request.description
            }
            
            skill = self.tech_skill_repo.create_skill(skill_data)
            logger.info(f"Technical skill created successfully: {skill.skill_name} (ID: {skill.id})")
            
            return TechnicalSkillResponse.model_validate(skill)
            
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating technical skill: {str(e)}")
            raise InternalServerException(f"Technical skill creation failed: {str(e)}", "TECHNICAL_SKILL_CREATION_ERROR")

    def get_technical_skill(self, skill_id: int) -> TechnicalSkillResponse:
        """Get technical skill by ID"""
        logger.info(f"Getting technical skill: {skill_id}")
        
        skill = self.tech_skill_repo.get_skill_by_id(skill_id)
        if not skill:
            raise NotFoundException(f"Technical skill with ID {skill_id} not found", "TECHNICAL_SKILL_NOT_FOUND")
        
        return TechnicalSkillResponse.model_validate(skill)

    def get_technical_skills_by_employee(self, employee_id: str) -> List[TechnicalSkillResponse]:
        """Get all technical skills for an Employee"""
        logger.info(f"Getting technical skills for Employee: {employee_id}")
        
        self._check_employee_exists(employee_id)
        skills = self.tech_skill_repo.get_skills_by_employee_id(employee_id)
        
        return [TechnicalSkillResponse.model_validate(skill) for skill in skills]

    def update_technical_skill(self, skill_id: int, request: TechnicalSkillUpdateRequest) -> TechnicalSkillResponse:
        """Update technical skill by ID"""
        logger.info(f"Updating technical skill: {skill_id}")
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            if 'category' in update_data:
                update_data['category'] = update_data['category'].value
            
            updated_skill = self.tech_skill_repo.update_skill(skill_id, update_data)
            if not updated_skill:
                raise NotFoundException(f"Technical skill with ID {skill_id} not found", "TECHNICAL_SKILL_NOT_FOUND")
            
            logger.info(f"Technical skill updated successfully: {skill_id}")
            return TechnicalSkillResponse.model_validate(updated_skill)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error updating technical skill {skill_id}: {str(e)}")
            raise InternalServerException(f"Technical skill update failed: {str(e)}", "TECHNICAL_SKILL_UPDATE_ERROR")

    def delete_technical_skill(self, skill_id: int) -> None:
        """Delete technical skill by ID"""
        logger.info(f"Deleting technical skill: {skill_id}")
        
        try:
            if not self.tech_skill_repo.delete_skill(skill_id):
                raise NotFoundException(f"Technical skill with ID {skill_id} not found", "TECHNICAL_SKILL_NOT_FOUND")
            
            logger.info(f"Technical skill deleted successfully: {skill_id}")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting technical skill {skill_id}: {str(e)}")
            raise InternalServerException(f"Technical skill deletion failed: {str(e)}", "TECHNICAL_SKILL_DELETE_ERROR")

    # ===================== SOFT SKILL OPERATIONS =====================
    
    def create_soft_skill(self, request: SoftSkillCreateRequest) -> SoftSkillResponse:
        """Create a new soft skill for an Employee"""
        logger.info(f"Creating soft skill '{request.skill_name}' for Employee: {request.employee_id}")
        
        try:
            self._check_employee_exists(request.employee_id)
            
            skill_data = {
                "employee_id": request.employee_id,
                "skill_name": request.skill_name.value,
                "description": request.description
            }
            
            skill = self.soft_skill_repo.create_soft_skill(skill_data)
            logger.info(f"Soft skill created successfully: {skill.skill_name} (ID: {skill.id})")
            
            return SoftSkillResponse.model_validate(skill)
            
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating soft skill: {str(e)}")
            raise InternalServerException(f"Soft skill creation failed: {str(e)}", "SOFT_SKILL_CREATION_ERROR")

    def get_soft_skill(self, skill_id: int) -> SoftSkillResponse:
        """Get soft skill by ID"""
        logger.info(f"Getting soft skill: {skill_id}")
        
        skill = self.soft_skill_repo.get_soft_skill_by_id(skill_id)
        if not skill:
            raise NotFoundException(f"Soft skill with ID {skill_id} not found", "SOFT_SKILL_NOT_FOUND")
        
        return SoftSkillResponse.model_validate(skill)

    def get_soft_skills_by_employee(self, employee_id: str) -> List[SoftSkillResponse]:
        """Get all soft skills for an Employee"""
        logger.info(f"Getting soft skills for Employee: {employee_id}")
        
        self._check_employee_exists(employee_id)
        skills = self.soft_skill_repo.get_soft_skills_by_employee_id(employee_id)
        
        return [SoftSkillResponse.model_validate(skill) for skill in skills]

    def update_soft_skill(self, skill_id: int, request: SoftSkillUpdateRequest) -> SoftSkillResponse:
        """Update soft skill by ID"""
        logger.info(f"Updating soft skill: {skill_id}")
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            if 'skill_name' in update_data:
                update_data['skill_name'] = update_data['skill_name'].value
            
            updated_skill = self.soft_skill_repo.update_soft_skill(skill_id, update_data)
            if not updated_skill:
                raise NotFoundException(f"Soft skill with ID {skill_id} not found", "SOFT_SKILL_NOT_FOUND")
            
            logger.info(f"Soft skill updated successfully: {skill_id}")
            return SoftSkillResponse.model_validate(updated_skill)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error updating soft skill {skill_id}: {str(e)}")
            raise InternalServerException(f"Soft skill update failed: {str(e)}", "SOFT_SKILL_UPDATE_ERROR")

    def delete_soft_skill(self, skill_id: int) -> None:
        """Delete soft skill by ID"""
        logger.info(f"Deleting soft skill: {skill_id}")
        
        try:
            if not self.soft_skill_repo.delete_soft_skill(skill_id):
                raise NotFoundException(f"Soft skill with ID {skill_id} not found", "SOFT_SKILL_NOT_FOUND")
            
            logger.info(f"Soft skill deleted successfully: {skill_id}")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting soft skill {skill_id}: {str(e)}")
            raise InternalServerException(f"Soft skill deletion failed: {str(e)}", "SOFT_SKILL_DELETE_ERROR")

    # ===================== PROJECT OPERATIONS =====================
    
    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project for an Employee"""
        logger.info(f"Creating project '{request.project_name}' for Employee: {request.employee_id}")
        
        try:
            self._check_employee_exists(request.employee_id)
            
            project_data = {
                "employee_id": request.employee_id,
                "project_name": request.project_name,
                "project_description": request.project_description,
                "position": request.position,
                "responsibilities": request.responsibilities,
                "programming_languages": request.programming_languages
            }
            
            project = self.project_repo.create_project(project_data)
            logger.info(f"Project created successfully: {project.project_name} (ID: {project.id})")
            
            return ProjectResponse.model_validate(project)
            
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating project: {str(e)}")
            raise InternalServerException(f"Project creation failed: {str(e)}", "PROJECT_CREATION_ERROR")

    def get_project(self, project_id: int) -> ProjectResponse:
        """Get project by ID"""
        logger.info(f"Getting project: {project_id}")
        
        project = self.project_repo.get_project_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project with ID {project_id} not found", "PROJECT_NOT_FOUND")
        
        return ProjectResponse.model_validate(project)

    def get_projects_by_employee(self, employee_id: str) -> List[ProjectResponse]:
        """Get all projects for an Employee"""
        logger.info(f"Getting projects for Employee: {employee_id}")
        
        self._check_employee_exists(employee_id)
        projects = self.project_repo.get_projects_by_employee_id(employee_id)
        
        return [ProjectResponse.model_validate(project) for project in projects]

    def update_project(self, project_id: int, request: ProjectUpdateRequest) -> ProjectResponse:
        """Update project by ID"""
        logger.info(f"Updating project: {project_id}")
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            
            updated_project = self.project_repo.update_project(project_id, update_data)
            if not updated_project:
                raise NotFoundException(f"Project with ID {project_id} not found", "PROJECT_NOT_FOUND")
            
            logger.info(f"Project updated successfully: {project_id}")
            return ProjectResponse.model_validate(updated_project)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise InternalServerException(f"Project update failed: {str(e)}", "PROJECT_UPDATE_ERROR")

    def delete_project(self, project_id: int) -> None:
        """Delete project by ID"""
        logger.info(f"Deleting project: {project_id}")
        
        try:
            if not self.project_repo.delete_project(project_id):
                raise NotFoundException(f"Project with ID {project_id} not found", "PROJECT_NOT_FOUND")
            
            logger.info(f"Project deleted successfully: {project_id}")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            raise InternalServerException(f"Project deletion failed: {str(e)}", "PROJECT_DELETE_ERROR")

    # ===================== BULK OPERATIONS =====================
    
    def get_employee_components(self, employee_id: str) -> Dict[str, List]:
        """Get all components for an Employee"""
        logger.info(f"Getting all components for Employee: {employee_id}")
        
        self._check_employee_exists(employee_id)
        components = self.bulk_operations.get_all_employee_components(employee_id)
        
        return {
            'languages': [LanguageResponse.model_validate(lang) for lang in components['languages']],
            'technical_skills': [TechnicalSkillResponse.model_validate(skill) for skill in components['technical_skills']],
            'soft_skills': [SoftSkillResponse.model_validate(skill) for skill in components['soft_skills']],
            'projects': [ProjectResponse.model_validate(project) for project in components['projects']]
        }

    def bulk_create_components(self, request: BulkComponentCreateRequest) -> BulkComponentResponse:
        """Bulk create components for an Employee"""
        logger.info(f"Bulk creating components for Employee: {request.employee_id}")
        
        try:
            self._check_employee_exists(request.employee_id)
            
            # Prepare components data
            components_data = {}
            
            if request.languages:
                # Remove employee_id from individual requests and use the main employee_id
                components_data['languages'] = [
                    {**lang.model_dump(exclude={'employee_id'}), 'proficiency': lang.proficiency.value}
                    for lang in request.languages
                ]
            
            if request.technical_skills:
                components_data['technical_skills'] = [
                    {**skill.model_dump(exclude={'employee_id'}), 'category': skill.category.value}
                    for skill in request.technical_skills
                ]
            
            if request.soft_skills:
                components_data['soft_skills'] = [
                    {**skill.model_dump(exclude={'employee_id'}), 'skill_name': skill.skill_name.value}
                    for skill in request.soft_skills
                ]
            
            if request.projects:
                components_data['projects'] = [
                    proj.model_dump(exclude={'employee_id'})
                    for proj in request.projects
                ]
            
            # Create components
            created_components = self.bulk_operations.bulk_create_employee_components(request.employee_id, components_data)
            
            # Calculate created counts
            created_counts = {
                'languages': len(created_components.get('languages', [])),
                'technical_skills': len(created_components.get('technical_skills', [])),
                'soft_skills': len(created_components.get('soft_skills', [])),
                'projects': len(created_components.get('projects', []))
            }
            
            logger.info(f"Bulk component creation completed for Employee {request.employee_id}: {created_counts}")
            
            return BulkComponentResponse(
                employee_id=request.employee_id,
                created_counts=created_counts,
                languages=[LanguageResponse.model_validate(lang) for lang in created_components.get('languages', [])],
                technical_skills=[TechnicalSkillResponse.model_validate(skill) for skill in created_components.get('technical_skills', [])],
                soft_skills=[SoftSkillResponse.model_validate(skill) for skill in created_components.get('soft_skills', [])],
                projects=[ProjectResponse.model_validate(project) for project in created_components.get('projects', [])]
            )
            
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Bulk component creation failed for Employee {request.employee_id}: {str(e)}")
            raise InternalServerException(f"Bulk component creation failed: {str(e)}", "BULK_COMPONENT_CREATION_ERROR")