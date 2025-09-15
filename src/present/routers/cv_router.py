# src/present/routers/cv_router.py
from fastapi import APIRouter, Depends, status, Query, Path
from typing import List, Dict

from src.present.request.cv import (
    CVCreate, CVUpdate, CV, CVWithDetails,
    CVBulkCreate, CVBulkResponse, CVSearchRequest, 
    CVPaginationResponse, CVComponentCreateRequest, CVComponentsResponse
)
from src.present.controllers.cv_controller import CVController
from src.bootstrap.dependencies import get_cv_controller

router = APIRouter(prefix="/cvs", tags=["CVs"])


@router.post("/", response_model=CV, status_code=status.HTTP_201_CREATED)
def create_cv(
    cv: CVCreate, 
    controller: CVController = Depends(get_cv_controller)
):
    """
    Create a new CV
    
    - **email**: Valid email address (unique)
    - **full_name**: Full name (required, min 2 characters)
    - **gender**: Optional gender (Male/Female/Other)
    - **current_position**: Optional current position
    - **summary**: Optional summary/bio
    - **languages**: Optional list of languages with proficiency
    - **technical_skills**: Optional list of technical skills
    - **soft_skills**: Optional list of soft skills
    - **projects**: Optional list of projects
    """
    return controller.create_cv(cv)


@router.get("/", response_model=CVPaginationResponse)
def get_cvs(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    controller: CVController = Depends(get_cv_controller),
):
    """
    Get all CVs with pagination
    
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10, max: 100)
    """
    return controller.get_cvs(page, page_size)


@router.get("/{cv_id}", response_model=CV)
def get_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Get CV by ID
    
    - **cv_id**: CV identifier (exactly 6 characters)
    """
    return controller.get_cv(cv_id)


@router.get("/{cv_id}/details", response_model=CVWithDetails)
def get_cv_with_details(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Get CV with all related components (languages, skills, projects)
    
    - **cv_id**: CV identifier (exactly 6 characters)
    """
    return controller.get_cv_with_details(cv_id)


@router.put("/{cv_id}", response_model=CV)
def update_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    cv_update: CVUpdate = ...,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Update CV by ID
    
    - **cv_id**: CV identifier (exactly 6 characters)
    - **cv_update**: Fields to update (all optional)
    """
    return controller.update_cv(cv_id, cv_update)


@router.delete("/{cv_id}")
def delete_cv(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Delete CV and all related data
    
    - **cv_id**: CV identifier (exactly 6 characters)
    
    **Warning**: This will permanently delete the CV and ALL related data (languages, skills, projects)
    """
    return controller.delete_cv(cv_id)


@router.post("/search", response_model=CVPaginationResponse)
def search_cvs(
    search_request: CVSearchRequest,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Search CVs by various criteria
    
    - **email**: Search by email pattern (case-insensitive)
    - **position**: Search by position pattern (case-insensitive)
    - **skill**: Search by skill name (case-insensitive)
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10)
    """
    return controller.search_cvs(search_request)


@router.post("/bulk", response_model=CVBulkResponse)
def bulk_create_cvs(
    bulk_request: CVBulkCreate,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Bulk create multiple CVs
    
    - **cvs**: List of CV creation requests
    
    **Note**: Partial success is possible - some CVs may be created while others fail
    """
    return controller.bulk_create_cvs(bulk_request)


@router.post("/{cv_id}/components", response_model=CVComponentsResponse)
def create_cv_components(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    request: CVComponentCreateRequest = ...,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Create components for existing CV
    
    - **cv_id**: CV identifier (exactly 6 characters)
    - **request**: Components to create (languages, skills, projects)
    """
    # Override cv_id in request with path parameter
    request.cv_id = cv_id
    return controller.create_cv_components(request)


@router.get("/{cv_id}/components", response_model=CVComponentsResponse)
def get_cv_components(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Get all components for a CV
    
    - **cv_id**: CV identifier (exactly 6 characters)
    """
    return controller.get_cv_components(cv_id)


# Additional utility endpoints
@router.get("/{cv_id}/summary")
def get_cv_summary(
    cv_id: str = Path(..., description="CV ID (6 characters)", min_length=6, max_length=6),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Get CV summary statistics
    
    - **cv_id**: CV identifier (exactly 6 characters)
    """
    components = controller.get_cv_components(cv_id)
    cv = controller.get_cv(cv_id)
    
    return {
        "cv_id": cv_id,
        "email": cv.email,
        "full_name": cv.full_name,
        "current_position": cv.current_position,
        "component_counts": {
            "languages": len(components.languages),
            "technical_skills": len(components.technical_skills),
            "soft_skills": len(components.soft_skills),
            "projects": len(components.projects)
        },
        "created_at": cv.created_at,
        "updated_at": cv.updated_at
    }
