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
    pageIndex: int = Query(1, ge=1, description="Page number (starting from 1)"),
    pageSize: int = Query(100, ge=1, le=100, description="Number of records per page"),
    controller: CVController = Depends(get_cv_controller),
):
    """Get all CVs with pagination (page/page_size)"""
    return controller.get_cvs(pageIndex, pageSize)
