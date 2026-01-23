"""Tests for WebSocket connection and real-time progress updates"""

import pytest
import asyncio
import json
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import manager


@pytest.mark.asyncio
class TestWebSocketConnection:
    """Test WebSocket connection handling"""

    async def test_websocket_accept_connection(self):
        """Test that WebSocket accepts connection with valid task_id"""
        client = TestClient(app)

        # Start a generation task first
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        assert response.status_code == 202
        task_id = response.json()["task_id"]

        # Test WebSocket connection
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Connection should be accepted
            assert websocket is not None

    async def test_websocket_reject_invalid_task_id(self):
        """Test that WebSocket rejects connection with invalid task_id"""
        client = TestClient(app)

        with pytest.raises(Exception):  # WebSocket will fail to connect
            with client.websocket_connect("/api/generate/ws/invalid-task-id") as websocket:
                pass

    async def test_websocket_receives_progress_messages(self, mock_openai):
        """Test that WebSocket receives progress updates"""
        client = TestClient(app)

        # Start generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Connect WebSocket
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Wait for and receive progress messages
            messages_received = []
            timeout_counter = 0

            while timeout_counter < 50:  # 5 seconds timeout
                try:
                    data = websocket.receive_json(timeout=0.1)
                    messages_received.append(data)

                    # Break if we got completion or error
                    if data.get("type") == "result":
                        break

                except Exception:
                    timeout_counter += 1

            # Should have received at least some messages
            assert len(messages_received) > 0

            # Check that at least one progress message was received
            progress_messages = [m for m in messages_received if m.get("type") == "progress"]
            assert len(progress_messages) > 0

            # Verify progress message structure
            progress_msg = progress_messages[0]
            assert "type" in progress_msg
            assert "task_id" in progress_msg
            assert "stage" in progress_msg
            assert "stage_index" in progress_msg
            assert "total_stages" in progress_msg
            assert "status" in progress_msg

    async def test_websocket_sends_result_on_completion(self, mock_openai):
        """Test that WebSocket sends final result when task completes"""
        client = TestClient(app)

        # Start generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Connect WebSocket and wait for result
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            result_message = None
            timeout_counter = 0

            while timeout_counter < 100:  # 10 seconds timeout
                try:
                    data = websocket.receive_json(timeout=0.1)

                    if data.get("type") == "result":
                        result_message = data
                        break

                except Exception:
                    timeout_counter += 1

            # Should have received result
            assert result_message is not None

            # Verify result structure
            assert result_message["type"] == "result"
            assert result_message["task_id"] == task_id
            assert result_message["status"] in ["completed", "failed"]

            if result_message["status"] == "completed":
                assert "generation_id" in result_message
                assert "markdown" in result_message
                assert result_message["markdown"] is not None
            elif result_message["status"] == "failed":
                assert "error" in result_message

    async def test_websocket_handles_disconnect(self):
        """Test that WebSocket handles client disconnect gracefully"""
        client = TestClient(app)

        # Start generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Connect and immediately disconnect
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Connection should be active
            assert websocket is not None
            # Disconnect happens when exiting context
            pass

        # Connection should be cleaned up
        assert task_id not in manager.active_connections


@pytest.mark.asyncio
class TestWebSocketMessageFormat:
    """Test WebSocket message format and structure"""

    async def test_progress_message_format(self, mock_openai):
        """Test that progress messages have correct format"""
        client = TestClient(app)

        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Receive first progress message
            timeout_counter = 0
            while timeout_counter < 50:
                try:
                    data = websocket.receive_json(timeout=0.1)
                    if data.get("type") == "progress":
                        break
                except Exception:
                    timeout_counter += 1

            # Validate message schema
            assert isinstance(data, dict)
            assert data["type"] == "progress"
            assert data["task_id"] == task_id
            assert isinstance(data["stage"], str)
            assert isinstance(data["stage_index"], int)
            assert isinstance(data["total_stages"], int)
            assert data["stage_index"] >= 0
            assert data["total_stages"] > 0
            assert data["stage_index"] <= data["total_stages"]
            assert data["status"] in ["running", "completed", "failed"]
            assert data.get("message") is None or isinstance(data.get("message"), str)
            assert data.get("error") is None or isinstance(data.get("error"), str)

    async def test_result_message_format(self, mock_openai):
        """Test that result messages have correct format"""
        client = TestClient(app)

        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Wait for result
            result_message = None
            timeout_counter = 0

            while timeout_counter < 100:
                try:
                    data = websocket.receive_json(timeout=0.1)
                    if data.get("type") == "result":
                        result_message = data
                        break
                except Exception:
                    timeout_counter += 1

            assert result_message is not None

            # Validate result schema
            assert isinstance(result_message, dict)
            assert result_message["type"] == "result"
            assert result_message["task_id"] == task_id
            assert result_message["status"] in ["completed", "failed"]

            if result_message["status"] == "completed":
                assert "generation_id" in result_message
                assert isinstance(result_message["generation_id"], int)
                assert "markdown" in result_message
                assert isinstance(result_message["markdown"], str)
                assert len(result_message["markdown"]) > 0
                # Markdown should contain headings
                assert "#" in result_message["markdown"]
            elif result_message["status"] == "failed":
                assert "error" in result_message
                assert isinstance(result_message["error"], str)
                assert len(result_message["error"]) > 0


@pytest.mark.asyncio
class TestWebSocketErrorHandling:
    """Test WebSocket error handling"""

    async def test_websocket_error_broadcast(self):
        """Test that errors are broadcast to WebSocket clients"""
        client = TestClient(app)

        # Try to generate with invalid content type
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "invalid_type", "client": "default"},
        )
        task_id = response.json()["task_id"]

        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            # Wait for error message
            timeout_counter = 0
            error_message = None

            while timeout_counter < 50:
                try:
                    data = websocket.receive_json(timeout=0.1)
                    if data.get("status") == "failed":
                        error_message = data
                        break
                except Exception:
                    timeout_counter += 1

            assert error_message is not None
            assert error_message["status"] == "failed"
            assert "error" in error_message


@pytest.mark.asyncio
class TestWebSocketConcurrency:
    """Test WebSocket with multiple concurrent connections"""

    async def test_multiple_clients_same_task(self, mock_openai):
        """Test that multiple clients can connect to same task"""
        client = TestClient(app)

        # Start generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Connect two WebSocket clients to same task
        received_messages = []

        def client_handler(messages_list):
            with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
                timeout_counter = 0
                while timeout_counter < 50:
                    try:
                        data = websocket.receive_json(timeout=0.1)
                        messages_list.append(data)
                    except Exception:
                        timeout_counter += 1

        # Run both clients concurrently
        client1_messages = []
        client2_messages = []

        # In a real scenario, we'd use asyncio.gather, but TestClient is synchronous
        # So we'll just connect one after another and verify both can connect
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as ws1:
            with client.websocket_connect(f"/api/generate/ws/{task_id}") as ws2:
                # Both connections should be established
                assert ws1 is not None
                assert ws2 is not None


@pytest.mark.asyncio
class TestTaskResultEndpoint:
    """Test task result REST endpoint for WebSocket tasks"""

    async def test_get_task_result_pending(self):
        """Test getting result for pending task"""
        client = TestClient(app)

        # Start generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Get result immediately (should be pending)
        result_response = client.get(f"/api/generate/{task_id}")
        assert result_response.status_code == 200

        result = result_response.json()
        assert result["task_id"] == task_id
        assert result["status"] in ["pending", "running", "completed", "failed"]

    async def test_get_task_result_not_found(self):
        """Test getting result for non-existent task"""
        client = TestClient(app)

        response = client.get("/api/generate/non-existent-task-id")
        assert response.status_code == 200

        result = response.json()
        assert result["status"] == "not_found"

    async def test_get_task_result_completed(self, mock_openai):
        """Test getting result for completed task"""
        client = TestClient(app)

        # Start and wait for generation
        response = client.post(
            "/api/generate",
            json={"keyword": "test keyword", "content_type": "blog", "client": "default"},
        )
        task_id = response.json()["task_id"]

        # Wait for completion via WebSocket
        with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
            timeout_counter = 0
            while timeout_counter < 100:
                try:
                    data = websocket.receive_json(timeout=0.1)
                    if data.get("type") == "result":
                        break
                except Exception:
                    timeout_counter += 1

        # Get result via REST
        result_response = client.get(f"/api/generate/{task_id}")
        assert result_response.status_code == 200

        result = result_response.json()
        assert result["task_id"] == task_id
        assert result["status"] == "completed"
        assert "generation_id" in result
        assert "markdown" in result
        assert result["markdown"] is not None
