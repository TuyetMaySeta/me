# src/present/routers/employee_related_router.py
from fastapi import APIRouter, Depends, status, Path
from typing import List, Dict

from src.present.request.employee_related import (
    LanguageCreateRequest, LanguageUpdateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillUpdateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillUpdateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    BulkComponentCreateRequest, BulkComponentResponse
)
from src.present.controllers.employee_related_controller import EmployeeRelatedController
from src.bootstrap.dependencies import get_employee_related_controller

router = APIRouter(prefix="/employee-components", tags=["Employee Components"])


# ===================== LANGUAGE ENDPOINTS =====================

@router.post("/languages", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(
    request: LanguageCreateRequest,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new language for an Employee
    
    - **employee_id**: Employee technical ID (must be exactly 6 characters and exist)
    - **language_name**: Name of the language (max 100 characters)
    - **proficiency**: Language proficiency level (NATIVE/FLUENT/INTERMEDIATE/BASIC)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_language(request)


@router.get("/languages/{lang_id}", response_model=LanguageResponse)
def get_language(
    lang_id: int = Path(..., description="Language ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get language by ID"""
    return controller.get_language(lang_id)


@router.get("/employee/{employee_id}/languages", response_model=List[LanguageResponse])
def get_languages_by_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all languages for an Employee"""
    return controller.get_languages_by_employee(employee_id)


@router.put("/languages/{lang_id}", response_model=LanguageResponse)
def update_language(
    lang_id: int = Path(..., description="Language ID", gt=0),
    request: LanguageUpdateRequest = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Update language by ID
    
    - **lang_id**: Language identifier
    - **request**: Fields to update (all optional)
    """
    return controller.update_language(lang_id, request)


@router.delete("/languages/{lang_id}")
def delete_language(
    lang_id: int = Path(..., description="Language ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete language by ID"""
    return controller.delete_language(lang_id)


# ===================== TECHNICAL SKILL ENDPOINTS =====================

@router.post("/technical-skills", response_model=TechnicalSkillResponse, status_code=status.HTTP_201_CREATED)
def create_technical_skill(
    request: TechnicalSkillCreateRequest,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new technical skill for an Employee
    
    - **employee_id**: Employee technical ID (must be exactly 6 characters and exist)
    - **category**: Skill category (PROGRAMMING_LANGUAGE/DATABASE/FRAMEWORK/TOOL/HARDWARE)
    - **skill_name**: Name of the skill (max 255 characters)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_technical_skill(request)


@router.get("/technical-skills/{skill_id}", response_model=TechnicalSkillResponse)
def get_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get technical skill by ID"""
    return controller.get_technical_skill(skill_id)


@router.get("/employee/{employee_id}/technical-skills", response_model=List[TechnicalSkillResponse])
def get_technical_skills_by_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all technical skills for an Employee"""
    return controller.get_technical_skills_by_employee(employee_id)


@router.put("/technical-skills/{skill_id}", response_model=TechnicalSkillResponse)
def update_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    request: TechnicalSkillUpdateRequest = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Update technical skill by ID
    
    - **skill_id**: Technical skill identifier
    - **request**: Fields to update (all optional)
    """
    return controller.update_technical_skill(skill_id, request)


@router.delete("/technical-skills/{skill_id}")
def delete_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete technical skill by ID"""
    return controller.delete_technical_skill(skill_id)


# ===================== SOFT SKILL ENDPOINTS =====================

@router.post("/soft-skills", response_model=SoftSkillResponse, status_code=status.HTTP_201_CREATED)
def create_soft_skill(
    request: SoftSkillCreateRequest,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new soft skill for an Employee
    
    - **employee_id**: Employee technical ID (must be exactly 6 characters and exist)
    - **skill_name**: Soft skill name from predefined list
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_soft_skill(request)


@router.get("/soft-skills/{skill_id}", response_model=SoftSkillResponse)
def get_soft_skill(
    skill_id: int = Path(..., description="Soft Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get soft skill by ID"""
    return controller.get_soft_skill(skill_id)


@router.get("/employee/{employee_id}/soft-skills", response_model=List[SoftSkillResponse])
def get_soft_skills_by_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all soft skills for an Employee"""
    return controller.get_soft_skills_by_employee(employee_id)


@router.put("/soft-skills/{skill_id}", response_model=SoftSkillResponse)
def update_soft_skill(
    skill_id: int = Path(..., description="Soft Skill ID", gt=0),
    request: SoftSkillUpdateRequest = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Update soft skill by ID
    
    - **skill_id**: Soft skill identifier
    - **request**: Fields to update (all optional)
    """
    return controller.update_soft_skill(skill_id, request)


@router.delete("/soft-skills/{skill_id}")
def delete_soft_skill(
    skill_id: int = Path(..., description="Soft Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete soft skill by ID"""
    return controller.delete_soft_skill(skill_id)


# ===================== PROJECT ENDPOINTS =====================

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new project for an Employee
    
    - **employee_id**: Employee technical ID (must be exactly 6 characters and exist)
    - **project_name**: Name of the project (max 255 characters)
    - **project_description**: Optional project description (max 2000 characters)
    - **position**: Optional position in project (max 255 characters)
    - **responsibilities**: Optional responsibilities (max 2000 characters)
    - **programming_languages**: Optional programming languages used (max 500 characters)
    """
    return controller.create_project(request)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get project by ID"""
    return controller.get_project(project_id)


@router.get("/employee/{employee_id}/projects", response_model=List[ProjectResponse])
def get_projects_by_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all projects for an Employee"""
    return controller.get_projects_by_employee(employee_id)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    request: ProjectUpdateRequest = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Update project by ID
    
    - **project_id**: Project identifier
    - **request**: Fields to update (all optional)
    """
    return controller.update_project(project_id, request)


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete project by ID"""
    return controller.delete_project(project_id)


# ===================== BULK OPERATIONS =====================

@router.get("/employee/{employee_id}/all", response_model=Dict[str, List])
def get_employee_components(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Get all components for an Employee
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    
    Returns all languages, technical skills, soft skills, and projects for the Employee
    """
    return controller.get_employee_components(employee_id)


@router.post("/employee/{employee_id}/bulk", response_model=BulkComponentResponse)
def bulk_create_components(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    request: BulkComponentCreateRequest = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Bulk create components for an Employee
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    - **request**: Components to create (languages, technical_skills, soft_skills, projects)
    
    Create multiple components for an Employee in a single request
    """
    # Override employee_id in request with path parameter
    request.employee_id = employee_id
    return controller.bulk_create_components(request)


# ===================== UTILITY ENDPOINTS =====================

@router.get("/employee/{employee_id}/stats")
def get_employee_component_stats(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Get component statistics for an Employee
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    
    Returns count of each component type
    """
    components = controller.get_employee_components(employee_id)
    
    return {
        "employee_id": employee_id,
        "statistics": {
            "languages_count": len(components.get('languages', [])),
            "technical_skills_count": len(components.get('technical_skills', [])),
            "soft_skills_count": len(components.get('soft_skills', [])),
            "projects_count": len(components.get('projects', [])),
            "total_components": (
                len(components.get('languages', [])) +
                len(components.get('technical_skills', [])) +
                len(components.get('soft_skills', [])) +
                len(components.get('projects', []))
            )
        },
        "breakdown": {
            "has_languages": len(components.get('languages', [])) > 0,
            "has_technical_skills": len(components.get('technical_skills', [])) > 0,
            "has_soft_skills": len(components.get('soft_skills', [])) > 0,
            "has_projects": len(components.get('projects', [])) > 0
        }
    }