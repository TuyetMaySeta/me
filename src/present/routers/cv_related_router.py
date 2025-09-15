# src/present/routers/cv_related_router.py
from fastapi import APIRouter, Depends, status, Path
from typing import List, Dict

from src.present.request.cv_related import (
    LanguageCreateRequest, LanguageUpdateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillUpdateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillUpdateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    BulkComponentCreateRequest, BulkComponentResponse
)
from src.present.controllers.cv_related_controller import CVRelatedController
from src.bootstrap.dependencies import get_cv_related_controller

router = APIRouter(prefix="/cv-components", tags=["CV Components"])


# ===================== LANGUAGE ENDPOINTS =====================

@router.post("/languages", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(
    request: LanguageCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new language for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
    - **language_name**: Name of the language (max 100 characters)
    - **proficiency**: Language proficiency level (NATIVE/FLUENT/INTERMEDIATE/BASIC)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_language(request)


@router.get("/languages/{lang_id}", response_model=LanguageResponse)
def get_language(
    lang_id: int = Path(..., description="Language ID", gt=0),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get language by ID"""
    return controller.get_language(lang_id)


@router.get("/cv/{cv_id}/languages", response_model=List[LanguageResponse])
def get_languages_by_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get all languages for a CV"""
    return controller.get_languages_by_cv(cv_id)


@router.put("/languages/{lang_id}", response_model=LanguageResponse)
def update_language(
    lang_id: int = Path(..., description="Language ID", gt=0),
    request: LanguageUpdateRequest = ...,
    controller: CVRelatedController = Depends(get_cv_related_controller)
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
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Delete language by ID"""
    return controller.delete_language(lang_id)


# ===================== TECHNICAL SKILL ENDPOINTS =====================

@router.post("/technical-skills", response_model=TechnicalSkillResponse, status_code=status.HTTP_201_CREATED)
def create_technical_skill(
    request: TechnicalSkillCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new technical skill for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
    - **category**: Skill category (PROGRAMMING_LANGUAGE/DATABASE/FRAMEWORK/TOOL/HARDWARE)
    - **skill_name**: Name of the skill (max 255 characters)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_technical_skill(request)


@router.get("/technical-skills/{skill_id}", response_model=TechnicalSkillResponse)
def get_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get technical skill by ID"""
    return controller.get_technical_skill(skill_id)


@router.get("/cv/{cv_id}/technical-skills", response_model=List[TechnicalSkillResponse])
def get_technical_skills_by_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get all technical skills for a CV"""
    return controller.get_technical_skills_by_cv(cv_id)


@router.put("/technical-skills/{skill_id}", response_model=TechnicalSkillResponse)
def update_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    request: TechnicalSkillUpdateRequest = ...,
    controller: CVRelatedController = Depends(get_cv_related_controller)
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
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Delete technical skill by ID"""
    return controller.delete_technical_skill(skill_id)


# ===================== SOFT SKILL ENDPOINTS =====================

@router.post("/soft-skills", response_model=SoftSkillResponse, status_code=status.HTTP_201_CREATED)
def create_soft_skill(
    request: SoftSkillCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new soft skill for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
    - **skill_name**: Soft skill name from predefined list
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_soft_skill(request)


@router.get("/soft-skills/{skill_id}", response_model=SoftSkillResponse)
def get_soft_skill(
    skill_id: int = Path(..., description="Soft Skill ID", gt=0),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get soft skill by ID"""
    return controller.get_soft_skill(skill_id)


@router.get("/cv/{cv_id}/soft-skills", response_model=List[SoftSkillResponse])
def get_soft_skills_by_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get all soft skills for a CV"""
    return controller.get_soft_skills_by_cv(cv_id)


@router.put("/soft-skills/{skill_id}", response_model=SoftSkillResponse)
def update_soft_skill(
    skill_id: int = Path(..., description="Soft Skill ID", gt=0),
    request: SoftSkillUpdateRequest = ...,
    controller: CVRelatedController = Depends(get_cv_related_controller)
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
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Delete soft skill by ID"""
    return controller.delete_soft_skill(skill_id)


# ===================== PROJECT ENDPOINTS =====================

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new project for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
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
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get project by ID"""
    return controller.get_project(project_id)


@router.get("/cv/{cv_id}/projects", response_model=List[ProjectResponse])
def get_projects_by_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Get all projects for a CV"""
    return controller.get_projects_by_cv(cv_id)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    request: ProjectUpdateRequest = ...,
    controller: CVRelatedController = Depends(get_cv_related_controller)
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
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """Delete project by ID"""
    return controller.delete_project(project_id)


# ===================== BULK OPERATIONS =====================

@router.get("/cv/{cv_id}/all", response_model=Dict[str, List])
def get_cv_components(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Get all components for a CV
    
    - **cv_id**: CV identifier (exactly 6 characters)
    
    Returns all languages, technical skills, soft skills, and projects for the CV
    """
    return controller.get_cv_components(cv_id)


@router.post("/cv/{cv_id}/bulk", response_model=BulkComponentResponse)
def bulk_create_components(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    request: BulkComponentCreateRequest = ...,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Bulk create components for a CV
    
    - **cv_id**: CV identifier (exactly 6 characters)
    - **request**: Components to create (languages, technical_skills, soft_skills, projects)
    
    Create multiple components for a CV in a single request
    """
    # Override cv_id in request with path parameter
    request.cv_id = cv_id
    return controller.bulk_create_components(request)


# ===================== UTILITY ENDPOINTS =====================

@router.get("/cv/{cv_id}/stats")
def get_cv_component_stats(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Get component statistics for a CV
    
    - **cv_id**: CV identifier (exactly 6 characters)
    
    Returns count of each component type
    """
    components = controller.get_cv_components(cv_id)
    
    return {
        "cv_id": cv_id,
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
