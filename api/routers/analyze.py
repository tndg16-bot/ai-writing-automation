"""Analysis router - SEO and content analysis endpoints"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ai_writing.core.seo_analyzer import analyze_seo, get_seo_recommendations

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    """Request model for SEO analysis"""

    keyword: str
    markdown_content: str


class AnalyzeResponse(BaseModel):
    """Response model for SEO analysis"""

    overall_score: float
    keyword_density: float
    heading_structure: float
    content_length: float
    keyword_in_title: bool
    keyword_in_headings: bool
    details: dict[str, object]
    recommendations: list[str]


@router.post("/seo")
async def analyze_seo_endpoint(request: AnalyzeRequest):
    """
    Analyze SEO quality of content

    Provides SEO score and recommendations for improvement.
    """
    try:
        score = analyze_seo(request.keyword, request.markdown_content)
        recommendations = get_seo_recommendations(score)

        return AnalyzeResponse(
            overall_score=score.overall_score,
            keyword_density=score.keyword_density,
            heading_structure=score.heading_structure,
            content_length=score.content_length,
            keyword_in_title=score.keyword_in_title,
            keyword_in_headings=score.keyword_in_headings,
            details=score.details,
            recommendations=recommendations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
