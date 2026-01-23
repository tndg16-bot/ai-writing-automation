"""FastAPI dependencies"""

from typing import AsyncGenerator
import sys
from pathlib import Path

# Add src to path to import ai_writing package
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ai_writing.core.config import Config, EnvSettings
from ai_writing.core.history_manager import HistoryManager

security = HTTPBearer(auto_error=False)


# ============ Global instances ============

_config: Config | None = None
_env_settings: EnvSettings | None = None
_history_manager: HistoryManager | None = None


def get_config() -> Config:
    """Get or create config instance"""
    global _config
    if _config is None:
        config_path = Path("config/config.yaml")
        _config = Config.load(config_path)
    return _config


def get_env_settings() -> EnvSettings:
    """Get or create environment settings"""
    global _env_settings
    if _env_settings is None:
        _env_settings = EnvSettings()
    return _env_settings


def get_history_manager() -> HistoryManager:
    """Get or create history manager instance"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> bool:
    """Verify API key (optional - skip if no credentials provided)"""
    # For now, skip API key verification
    # TODO: Add proper API key authentication if needed
    return True


# ============ WebSocket connection manager ============

from fastapi import WebSocket
from typing import Dict, Set
import json
import uuid


class ConnectionManager:
    """Manager for WebSocket connections and task progress"""

    def __init__(self):
        # task_id -> list of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # task_id -> progress data
        self.task_progress: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, task_id: str) -> None:
        """Accept a WebSocket connection"""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str) -> None:
        """Remove a WebSocket connection"""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast(self, task_id: str, message: dict) -> None:
        """Broadcast a message to all connections for a task"""
        if task_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, task_id)

    def generate_task_id(self) -> str:
        """Generate a unique task ID"""
        return str(uuid.uuid4())


# Global connection manager
manager = ConnectionManager()
