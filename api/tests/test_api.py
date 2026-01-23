"""Tests for FastAPI - API endpoints (Simplified)"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Writing Automation API"
    assert "docs" in data


def test_generate_endpoint():
    """Test generate endpoint"""
    response = client.post(
        "/api/generate", json={"keyword": "test keyword", "content_type": "blog"}
    )
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data


def test_stats_endpoint():
    """Test stats endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_generations" in data or "total_generations" in data


def test_analyze_seo_endpoint():
    """Test SEO analysis endpoint"""
    response = client.post(
        "/api/analyze/seo",
        json={"keyword": "AI副業", "markdown_content": "# AI副業\n\nこれはAI副業の記事です。"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data or "overall_score" in data
