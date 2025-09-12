# src/present/routers/cv_router.py
from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional, Dict, Any
from src.present.request.cv import (
    CVCreate, CVUpdate, CV, CVWithDetails, 
    CVBulkCreate, CVBulkResponse
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
    
    - **id_seta**: Employee SETA ID (must start with EMP)
    - **email**: Employee email (unique)
    - **full_name**: Employee full name
    - **gender**: Optional gender (Male/Female/Other)
    - **current_position**: Optional current position
    - **summary**: Optional CV summary
    - **languages**: Optional list of languages
    - **technical_skills**: Optional list of technical skills
    - **soft_skills**: Optional list of soft skills
    - **projects**: Optional list of projects
    """
    return controller.create_cv(cv)


@router.get("/", response_model=List[CV])
def get_cvs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    controller: CVController = Depends(get_cv_controller)
):
    """Get all CVs with pagination"""
    return controller.get_cvs(skip, limit)


@router.get("/search", response_model=List[CV])
def search_cvs(
    email: Optional[str] = Query(None, description="Search by email"),
    seta_id: Optional[str] = Query(None, description="Search by SETA ID"),
    position: Optional[str] = Query(None, description="Search by position"),
    skill: Optional[str] = Query(None, description="Search by technical skill"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    controller: CVController = Depends(get_cv_controller)
):
    """
    Search CVs by various criteria
    
    All search parameters are optional and can be combined:
    - **email**: Partial email search
    - **seta_id**: Partial SETA ID search  
    - **position**: Partial position search
    - **skill**: Search by technical skill name
    """
    return controller.search_cvs(
        email=email,
        seta_id=seta_id, 
        position=position,
        skill=skill,
        skip=skip,
        limit=limit
    )


@router.get("/by-email/{email}", response_model=CV)
def get_cv_by_email(
    email: str,
    controller: CVController = Depends(get_cv_controller)
):
    """Get CV by email address"""
    return controller.get_cv_by_email(email)


@router.get("/by-seta/{seta_id}", response_model=CV)
def get_cv_by_seta_id(
    seta_id: str,
    controller: CVController = Depends(get_cv_controller)
):
    """Get CV by SETA ID"""
    return controller.get_cv_by_seta_id(seta_id)


@router.get("/{cv_id}", response_model=CV)
def get_cv(
    cv_id: str, 
    controller: CVController = Depends(get_cv_controller)
): 
    """Get a specific CV by ID"""
    return controller.get_cv(cv_id)


@router.get("/{cv_id}/details", response_model=CVWithDetails)
def get_cv_with_details(
    cv_id: str,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Get CV with all related details including:
    - Languages
    - Technical Skills  
    - Soft Skills
    - Projects
    """
    return controller.get_cv_with_details(cv_id)


@router.put("/{cv_id}", response_model=CV)
def update_cv(
    cv_id: str, 
    cv_update: CVUpdate, 
    controller: CVController = Depends(get_cv_controller)
):
    """
    Update a CV
    
    All fields are optional - only provided fields will be updated
    """
    return controller.update_cv(cv_id, cv_update)


@router.delete("/{cv_id}", status_code=status.HTTP_200_OK)
def delete_cv(
    cv_id: str, 
    controller: CVController = Depends(get_cv_controller)
):
    """
    Delete a CV and all related data
    
    **Warning**: This action cannot be undone!
    """
    return controller.delete_cv(cv_id)


@router.post("/bulk", response_model=CVBulkResponse, status_code=status.HTTP_201_CREATED)
def bulk_create_cvs(
    bulk_request: CVBulkCreate,
    controller: CVController = Depends(get_cv_controller)
):
    """
    Bulk create multiple CVs
    
    - Creates multiple CVs in one request
    - Returns count of successful creations and any errors
    - Failed CVs don't stop the process for other CVs
    """
    return controller.bulk_create_cvs(bulk_request)