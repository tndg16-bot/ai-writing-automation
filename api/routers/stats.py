"""Stats router - statistics endpoints"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import APIRouter, Depends

from api.models import StatsResponse
from api.dependencies import get_history_manager

from ai_writing.core.history_manager import HistoryManager

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
async def get_stats(
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Get generation statistics

    Returns:
    - total_generations: Total number of generations
    - total_images: Total number of images generated
    - by_content_type: Breakdown by content type
    - by_provider: Breakdown by image provider
    - db_size_bytes: Database size in bytes
    """
    stats = history_manager.get_stats()

    return StatsResponse(
        total_generations=stats["total_generations"],
        total_images=stats["total_images"],
        by_content_type=stats["by_content_type"],
        by_provider=stats["by_provider"],
        db_size_bytes=stats["db_size_bytes"],
    )


@router.get("/content-type")
async def get_stats_by_content_type(
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Get statistics grouped by content type

    Returns a dictionary with content type as key and count as value.
    """
    stats = history_manager.get_stats()
    return stats["by_content_type"]


@router.get("/image-provider")
async def get_stats_by_provider(
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Get statistics grouped by image provider

    Returns a dictionary with provider name as key and count as value.
    """
    stats = history_manager.get_stats()
    return stats["by_provider"]
