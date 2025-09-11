from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return "ok"
