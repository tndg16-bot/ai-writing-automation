"""Pytest configuration and fixtures"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """プロジェクトルートパス"""
    return Path(__file__).parent.parent


@pytest.fixture
def config_path(project_root: Path) -> Path:
    """設定ファイルパス"""
    return project_root / "config" / "config.yaml"


@pytest.fixture
def prompts_path(project_root: Path) -> Path:
    """プロンプトフォルダパス"""
    return project_root / "prompts"
