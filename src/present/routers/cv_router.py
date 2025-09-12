# src/present/routers/cv_router.py
# Keep POST create and GET all only

from fastapi import APIRouter, Depends, status, Query
from typing import List
from src.present.request.cv import CVCreate, CV
from src.present.controllers.cv_controller import CVController
from src.bootstrap.dependencies import get_cv_controller

router = APIRouter(prefix="/cvs", tags=["CVs"])


@router.post("/", response_model=CV, status_code=status.HTTP_201_CREATED)
def create_cv(
    cv: CVCreate, 
    controller: CVController = Depends(get_cv_controller)
):
    """Create a new CV"""
    return controller.create_cv(cv)

@router.get("/", response_model=List[CV])
def get_cvs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    controller: CVController = Depends(get_cv_controller)
):
    """Get all CVs with pagination"""
    return controller.get_cvs(skip, limit)