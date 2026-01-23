"""Generate router - content generation endpoints"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import Optional
import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from api.models import (
    GenerateRequest,
    GenerateResponse,
    GenerateProgress,
)
from api.dependencies import (
    get_config,
    get_history_manager,
    manager,
)

from ai_writing.pipeline.blog import BlogPipeline
from ai_writing.pipeline.youtube import YouTubePipeline
from ai_writing.pipeline.yukkuri import YukkuriPipeline
from ai_writing.core.history_manager import HistoryManager

router = APIRouter(prefix="/api/generate", tags=["generate"])


class TaskResult(BaseModel):
    task_id: str
    status: str
    generation_id: Optional[int] = None
    markdown: Optional[str] = None
    error: Optional[str] = None


# Store task results for WebSocket clients to fetch
task_results: dict[str, TaskResult] = {}


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=dict)
async def start_generation(
    request: GenerateRequest,
    config=Depends(get_config),
    history_manager: HistoryManager = Depends(get_history_manager),
):
    """
    Start content generation task

    Returns a task_id that can be used to track progress via WebSocket.
    """
    task_id = manager.generate_task_id()

    # Initialize task result
    task_results[task_id] = TaskResult(
        task_id=task_id,
        status="pending",
    )

    # Start pipeline in background
    asyncio.create_task(_run_pipeline(task_id, request, config, history_manager))

    return {"task_id": task_id}


async def _run_pipeline(
    task_id: str,
    request: GenerateRequest,
    config,
    history_manager: HistoryManager,
):
    """Run pipeline and broadcast progress"""
    try:
        # Broadcast start
        await manager.broadcast(
            task_id,
            {
                "type": "progress",
                "task_id": task_id,
                "stage": "initializing",
                "stage_index": 0,
                "total_stages": 0,
                "status": "running",
                "message": "Initializing pipeline...",
            },
        )

        # Select pipeline
        if request.content_type == "blog":
            pipeline = BlogPipeline(config)
        elif request.content_type == "youtube":
            pipeline = YouTubePipeline(config)
        elif request.content_type == "yukkuri":
            pipeline = YukkuriPipeline(config)
        else:
            raise ValueError(f"Unknown content type: {request.content_type}")

        # Progress callback
        def progress_callback(stage_index: int = 1, description: str | None = None):
            """Callback for pipeline progress updates"""
            stage_name = (
                description or f"Stage {stage_index}" if description else f"Stage {stage_index}"
            )

            # Send progress update
            asyncio.create_task(
                manager.broadcast(
                    task_id,
                    {
                        "type": "progress",
                        "task_id": task_id,
                        "stage": stage_name,
                        "stage_index": stage_index,
                        "total_stages": len(pipeline.stages),
                        "status": "running",
                    },
                )
            )

        # Run pipeline
        context = await pipeline.run(
            request.keyword, request.content_type, progress_callback=progress_callback
        )

        # Broadcast completion
        await manager.broadcast(
            task_id,
            {
                "type": "progress",
                "task_id": task_id,
                "stage": "completed",
                "stage_index": len(pipeline.stages),
                "total_stages": len(pipeline.stages),
                "status": "completed",
                "message": "Generation completed",
            },
        )

        # Save to history
        generation_id = history_manager.save_generation(context)

        # Generate markdown
        markdown = _context_to_markdown(context)

        # Store result
        task_results[task_id] = TaskResult(
            task_id=task_id,
            status="completed",
            generation_id=generation_id,
            markdown=markdown,
        )

    except Exception as e:
        # Broadcast error
        await manager.broadcast(
            task_id,
            {
                "type": "progress",
                "task_id": task_id,
                "stage": "error",
                "stage_index": 0,
                "total_stages": 0,
                "status": "failed",
                "error": str(e),
            },
        )

        # Store error result
        task_results[task_id] = TaskResult(
            task_id=task_id,
            status="failed",
            error=str(e),
        )


@router.websocket("/ws/{task_id}")
async def websocket_generate(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time progress updates

    Connect to ws://host/api/generate/ws/{task_id} to receive progress updates.
    """
    await manager.connect(websocket, task_id)

    try:
        while True:
            # Keep connection alive and send results when available
            await asyncio.sleep(0.1)

            if task_id in task_results:
                result = task_results[task_id]

                if result.status == "completed":
                    await websocket.send_json(
                        {
                            "type": "result",
                            "task_id": task_id,
                            "status": "completed",
                            "generation_id": result.generation_id,
                            "markdown": result.markdown,
                        }
                    )
                    break
                elif result.status == "failed":
                    await websocket.send_json(
                        {
                            "type": "result",
                            "task_id": task_id,
                            "status": "failed",
                            "error": result.error,
                        }
                    )
                    break

    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)


def _context_to_markdown(context) -> str:
    """Convert GenerationContext to Markdown"""
    lines = []

    # Title
    if context.selected_title:
        lines.append(f"# {context.selected_title}")
        lines.append("")

    # Lead
    if context.lead:
        lines.append(context.lead)
        lines.append("")

    # Sections
    for section in context.sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        lines.append(section.content)
        lines.append("")

    # Summary
    if context.summary:
        lines.append("## まとめ")
        lines.append("")
        lines.append(context.summary)

    return "\n".join(lines)


@router.get("/{task_id}")
async def get_task_result(task_id: str):
    """Get task result by task_id"""
    if task_id not in task_results:
        return {"status": "not_found"}

    result = task_results[task_id]
    return {
        "task_id": task_id,
        "status": result.status,
        "generation_id": result.generation_id,
        "markdown": result.markdown if result.status == "completed" else None,
        "error": result.error if result.status == "failed" else None,
    }
