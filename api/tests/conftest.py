"""Tests configuration for API tests"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def test_app():
    """Fixture for FastAPI test app"""
    from api.main import app

    return app
