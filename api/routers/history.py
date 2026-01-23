"""History router - generation history endpoints"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.models import (
    GenerationListItem,
    GenerationDetail,
    ErrorResponse,
)
from api.dependencies import get_history_manager

from ai_writing.core.history_manager import HistoryManager

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[GenerationListItem])
async def list_history(
    keyword: Optional[str] = Query(None, description="Filter by keyword (partial match)"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    List generation history with optional filters

    - **keyword**: Filter by keyword (partial match)
    - **content_type**: Filter by content type (blog, youtube, yukkuri)
    - **limit**: Maximum number of results (1-200)
    - **offset**: Offset for pagination
    """
    generations = history_manager.list_generations(
        keyword=keyword,
        content_type=content_type,
        limit=limit,
        offset=offset,
    )

    return [
        GenerationListItem(
            id=gen["id"],
            keyword=gen["keyword"],
            content_type=gen["content_type"],
            title=gen.get("title"),
            sections_count=gen.get("sections_count", 0),
            images_count=gen.get("images_count", 0),
            created_at=gen["created_at"],
        )
        for gen in generations
    ]


@router.get("/{generation_id}", response_model=GenerationDetail)
async def get_generation(
    generation_id: int,
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Get detailed generation information by ID

    Includes images, versions, and raw responses.
    """
    generation = history_manager.get_generation(generation_id)

    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    return GenerationDetail(**generation)


@router.delete("/{generation_id}")
async def delete_generation(
    generation_id: int,
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Delete a generation by ID

    Also deletes associated images and versions.
    """
    success = history_manager.delete_generation(generation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Generation not found")

    return {"message": f"Generation {generation_id} deleted"}


@router.get("/{generation_id}/markdown")
async def export_generation(
    generation_id: int,
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Export generation as Markdown

    Returns the generation content in Markdown format.
    """
    markdown = history_manager.export_generation(generation_id)

    if markdown is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    return {"markdown": markdown}
