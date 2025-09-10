from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    logger.error("Health check endpoint called")
    return "ok"
