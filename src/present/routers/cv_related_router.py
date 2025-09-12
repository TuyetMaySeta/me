from fastapi import APIRouter, Depends, status
from src.present.request.cv_related import (
    LanguageCreateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectResponse
)
from src.present.controllers.cv_related_controller import CVRelatedController
from src.bootstrap.dependencies import get_cv_related_controller

router = APIRouter(prefix="/cv-components", tags=["CV Components"])


# Language endpoints
@router.post("/languages", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(
    request: LanguageCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new language for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
    - **language_name**: Name of the language (max 100 characters)
    - **proficiency**: Language proficiency level (Native/Fluent/Intermediate/Basic)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_language(request)


# Technical Skill endpoints
@router.post("/technical-skills", response_model=TechnicalSkillResponse, status_code=status.HTTP_201_CREATED)
def create_technical_skill(
    request: TechnicalSkillCreateRequest,
    controller: CVRelatedController = Depends(get_cv_related_controller)
):
    """
    Create a new technical skill for a CV
    
    - **cv_id**: CV ID (must be exactly 6 characters and exist)
    - **category**: Skill category (Programming Language/Database/Framework/Tool/Hardware)
    - **skill_name**: Name of the skill (max 255 characters)
    - **description**: Optional description (max 1000 characters)
    """
    return controller.create_technical_skill(request)


# Soft Skill endpoints
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


# Project endpoints
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
