import logging
from datetime import datetime

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "ok",
    }
