"""Pydantic models for API requests and responses"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ============ Request Models ============


class GenerateRequest(BaseModel):
    """Request model for content generation"""

    keyword: str = Field(..., min_length=1, description="Main keyword for content generation")
    content_type: str = Field(default="blog", description="Content type: blog, youtube, yukkuri")
    client: str = Field(default="default", description="Client configuration name")


class GenerateProgress(BaseModel):
    """WebSocket progress update model"""

    task_id: str
    stage: str
    stage_index: int
    total_stages: int
    status: str  # "running" | "completed" | "failed"
    message: str | None = None
    error: str | None = None


# ============ Response Models ============


class GenerateResponse(BaseModel):
    """Response model for content generation"""

    id: int
    keyword: str
    content_type: str
    title: str | None
    lead: str | None
    sections_count: int
    images_count: int
    created_at: str
    markdown: str | None = None
    docs_url: str | None = None


class GenerationListItem(BaseModel):
    """List item for generation history"""

    id: int
    keyword: str
    content_type: str
    title: str | None
    sections_count: int
    images_count: int
    created_at: str


class GenerationDetail(BaseModel):
    """Detailed generation information"""

    id: int
    keyword: str
    content_type: str
    title: str | None
    lead: str | None
    sections_count: int
    images_count: int
    created_at: str
    images: list[dict[str, Any]] = Field(default_factory=list)
    versions: list[dict[str, Any]] = Field(default_factory=list)
    raw_responses: dict[str, str] = Field(default_factory=dict)


class StatsResponse(BaseModel):
    """Statistics response"""

    total_generations: int
    total_images: int
    by_content_type: dict[str, int]
    by_provider: dict[str, int]
    db_size_bytes: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
