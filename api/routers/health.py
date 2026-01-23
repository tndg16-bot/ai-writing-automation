"""Health check router"""

from datetime import datetime
from fastapi import APIRouter

from api.models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns API status and version information.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
    )
