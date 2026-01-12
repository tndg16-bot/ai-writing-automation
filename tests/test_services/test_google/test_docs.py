"""Unit tests for Google Docs API service wrapper"""

import time
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock

from googleapiclient.errors import HttpError

from ai_writing.services.google.docs import GoogleDocsService, RateLimiter
from ai_writing.core.exceptions import GoogleDocsError


class TestRateLimiter:
    """Tests for RateLimiter class"""

    def test_init_default_values(self) -> None:
        """Test initialization with default values"""
        limiter = RateLimiter()

        assert limiter.max_calls == 50
        assert limiter.period == 60
        assert limiter.calls == []

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values"""
        limiter = RateLimiter(max_calls=100, period_seconds=120)

        assert limiter.max_calls == 100
        assert limiter.period == 120

    def test_wait_if_needed_under_limit(self) -> None:
        """Test that no waiting occurs when under limit"""
        limiter = RateLimiter(max_calls=10, period_seconds=60)

        start = time.time()
        for _ in range(5):
            limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should complete quickly without waiting
        assert elapsed < 0.5
        assert len(limiter.calls) == 5

    def test_wait_if_needed_at_limit(self) -> None:
        """Test that waiting occurs when at limit"""
        limiter = RateLimiter(max_calls=3, period_seconds=1)

        # Fill up the limit
        for _ in range(3):
            limiter.wait_if_needed()

        # This call should wait
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should have waited approximately 1 second
        assert elapsed >= 0.5  # Allow some tolerance

    def test_wait_if_needed_cleans_old_calls(self) -> None:
        """Test that old calls are cleaned up"""
        limiter = RateLimiter(max_calls=10, period_seconds=1)

        # Add some calls with old timestamps
        old_time = time.time() - 2  # 2 seconds ago
        limiter.calls = [old_time, old_time, old_time]

        limiter.wait_if_needed()

        # Old calls should be removed, only new call remains
        assert len(limiter.calls) == 1

    def test_reset(self) -> None:
        """Test reset clears all calls"""
        limiter = RateLimiter()
        limiter.calls = [time.time() for _ in range(10)]

        limiter.reset()

        assert limiter.calls == []

    def test_remaining_calls(self) -> None:
        """Test remaining_calls property"""
        limiter = RateLimiter(max_calls=10, period_seconds=60)

        # No calls made yet
        assert limiter.remaining_calls == 10

        # Make some calls
        for _ in range(3):
            limiter.wait_if_needed()

        assert limiter.remaining_calls == 7

    def test_remaining_calls_excludes_old(self) -> None:
        """Test remaining_calls excludes expired calls"""
        limiter = RateLimiter(max_calls=10, period_seconds=1)

        # Add old calls
        old_time = time.time() - 2
        limiter.calls = [old_time, old_time, old_time]

        # All old calls should be excluded
        assert limiter.remaining_calls == 10


class TestGoogleDocsService:
    """Tests for GoogleDocsService class"""

    @pytest.fixture
    def mock_credentials(self) -> Mock:
        """Create mock credentials"""
        return Mock()

    @pytest.fixture
    def mock_docs_service(self) -> Mock:
        """Create mock Google Docs service"""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def mock_drive_service(self) -> Mock:
        """Create mock Google Drive service"""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def docs_service(
        self, mock_credentials: Mock, mock_docs_service: Mock, mock_drive_service: Mock
    ) -> GoogleDocsService:
        """Create GoogleDocsService with mocked dependencies"""
        with patch(
            "ai_writing.services.google.docs.build"
        ) as mock_build:
            # Return different mocks for docs and drive
            def build_side_effect(service_name: str, version: str, **kwargs):
                if service_name == "docs":
                    return mock_docs_service
                elif service_name == "drive":
                    return mock_drive_service
                return Mock()

            mock_build.side_effect = build_side_effect

            service = GoogleDocsService(mock_credentials)
            service.service = mock_docs_service
            service.drive_service = mock_drive_service
            return service

    def test_init(self, mock_credentials: Mock) -> None:
        """Test service initialization"""
        with patch("ai_writing.services.google.docs.build") as mock_build:
            service = GoogleDocsService(mock_credentials)

            assert service.credentials == mock_credentials
            assert isinstance(service.rate_limiter, RateLimiter)
            assert mock_build.call_count == 2  # docs and drive

    def test_create_document_success(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test successful document creation"""
        mock_docs_service.documents().create().execute.return_value = {
            "documentId": "test_doc_id"
        }

        doc_id = docs_service.create_document("Test Document")

        assert doc_id == "test_doc_id"
        # Verify the create method was called with correct body
        mock_docs_service.documents().create.assert_called_with(body={"title": "Test Document"})

    def test_create_document_failure(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test document creation failure"""
        mock_docs_service.documents().create().execute.return_value = {}

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.create_document("Test Document")

        assert "Failed to get document ID" in str(exc_info.value)

    def test_create_document_http_error(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test document creation with HTTP error"""
        mock_resp = Mock()
        mock_resp.status = 500
        mock_resp.reason = "Internal Error"
        http_error = HttpError(resp=mock_resp, content=b"Error")

        mock_docs_service.documents().create().execute.side_effect = http_error

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.create_document("Test Document")

        assert "Failed to create document" in str(exc_info.value)

    def test_batch_update_success(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test successful batch update"""
        expected_response = {"replies": [{"insertText": {"location": {"index": 1}}}]}
        mock_docs_service.documents().batchUpdate().execute.return_value = (
            expected_response
        )

        requests = [{"insertText": {"location": {"index": 1}, "text": "Hello"}}]
        response = docs_service.batch_update("test_doc_id", requests)

        assert response == expected_response

    def test_batch_update_empty_requests(
        self, docs_service: GoogleDocsService
    ) -> None:
        """Test batch update with empty requests returns empty response"""
        response = docs_service.batch_update("test_doc_id", [])

        assert response == {"replies": []}

    def test_batch_update_http_error(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test batch update with HTTP error"""
        mock_resp = Mock()
        mock_resp.status = 400
        mock_resp.reason = "Bad Request"
        http_error = HttpError(resp=mock_resp, content=b"Error")

        mock_docs_service.documents().batchUpdate().execute.side_effect = http_error

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.batch_update("test_doc_id", [{"test": "request"}])

        assert "Batch update failed" in str(exc_info.value)

    def test_insert_text_success(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test successful text insertion"""
        mock_docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        new_index = docs_service.insert_text("test_doc_id", "Hello World", 1)

        # New index should be start index + text length
        assert new_index == 1 + len("Hello World")

    def test_insert_text_empty(self, docs_service: GoogleDocsService) -> None:
        """Test inserting empty text returns same index"""
        new_index = docs_service.insert_text("test_doc_id", "", 5)

        assert new_index == 5

    def test_insert_heading_success(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test successful heading insertion"""
        mock_docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        new_index = docs_service.insert_heading("test_doc_id", "My Heading", 1, 1)

        # New index should be start + text length + newline
        assert new_index == 1 + len("My Heading") + 1

    def test_insert_heading_empty(self, docs_service: GoogleDocsService) -> None:
        """Test inserting empty heading returns same index"""
        new_index = docs_service.insert_heading("test_doc_id", "", 1, 5)

        assert new_index == 5

    def test_insert_image_success(
        self,
        docs_service: GoogleDocsService,
        mock_docs_service: Mock,
        mock_drive_service: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful image insertion"""
        # Create a test image file
        image_file = tmp_path / "test.png"
        image_file.write_bytes(b"fake image data")

        # Mock drive upload
        mock_drive_service.files().create().execute.return_value = {
            "id": "uploaded_file_id"
        }
        mock_drive_service.permissions().create().execute.return_value = {}

        # Mock docs batch update
        mock_docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        new_index = docs_service.insert_image("test_doc_id", image_file, index=1)

        assert new_index == 2  # index + 1 for image

    def test_insert_image_file_not_found(
        self, docs_service: GoogleDocsService
    ) -> None:
        """Test image insertion with non-existent file"""
        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.insert_image("test_doc_id", Path("/nonexistent/image.png"), index=1)

        assert "Image file not found" in str(exc_info.value)

    def test_insert_image_upload_failure(
        self,
        docs_service: GoogleDocsService,
        mock_drive_service: Mock,
        tmp_path: Path,
    ) -> None:
        """Test image insertion with upload failure"""
        # Create a test image file
        image_file = tmp_path / "test.png"
        image_file.write_bytes(b"fake image data")

        # Mock drive upload to return no ID
        mock_drive_service.files().create().execute.return_value = {}

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.insert_image("test_doc_id", image_file, index=1)

        assert "Failed to get file ID" in str(exc_info.value)

    def test_apply_heading_style_valid_levels(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test applying heading styles for all valid levels"""
        mock_docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        for level in range(1, 7):
            response = docs_service.apply_heading_style("test_doc_id", 1, 10, level)
            assert response is not None

    def test_apply_heading_style_invalid_level(
        self, docs_service: GoogleDocsService
    ) -> None:
        """Test applying heading style with invalid level"""
        with pytest.raises(ValueError) as exc_info:
            docs_service.apply_heading_style("test_doc_id", 1, 10, 0)

        assert "Heading level must be between 1 and 6" in str(exc_info.value)

        with pytest.raises(ValueError):
            docs_service.apply_heading_style("test_doc_id", 1, 10, 7)

    def test_apply_bold_style(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test applying bold style"""
        mock_docs_service.documents().batchUpdate().execute.return_value = {
            "replies": []
        }

        response = docs_service.apply_bold_style("test_doc_id", 1, 10)

        assert response is not None

    def test_get_document_success(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test getting document content"""
        expected_doc = {
            "documentId": "test_doc_id",
            "title": "Test Document",
            "body": {"content": []},
        }
        mock_docs_service.documents().get().execute.return_value = expected_doc

        doc = docs_service.get_document("test_doc_id")

        assert doc == expected_doc

    def test_get_document_http_error(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test getting document with HTTP error"""
        mock_resp = Mock()
        mock_resp.status = 404
        mock_resp.reason = "Not Found"
        http_error = HttpError(resp=mock_resp, content=b"Not found")

        mock_docs_service.documents().get().execute.side_effect = http_error

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.get_document("nonexistent_id")

        assert "Failed to get document" in str(exc_info.value)

    def test_get_document_url(self, docs_service: GoogleDocsService) -> None:
        """Test getting document URL"""
        url = docs_service.get_document_url("test_doc_id")

        assert url == "https://docs.google.com/document/d/test_doc_id/edit"

    def test_share_document_success(
        self, docs_service: GoogleDocsService, mock_drive_service: Mock
    ) -> None:
        """Test sharing document"""
        mock_drive_service.permissions().create().execute.return_value = {}

        docs_service.share_document("test_doc_id", "user@example.com")

        # Verify the create method was called with correct parameters
        mock_drive_service.permissions().create.assert_called_with(
            fileId="test_doc_id",
            body={"type": "user", "role": "writer", "emailAddress": "user@example.com"},
            sendNotificationEmail=True,
        )

    def test_share_document_http_error(
        self, docs_service: GoogleDocsService, mock_drive_service: Mock
    ) -> None:
        """Test sharing document with HTTP error"""
        mock_resp = Mock()
        mock_resp.status = 403
        mock_resp.reason = "Forbidden"
        http_error = HttpError(resp=mock_resp, content=b"Forbidden")

        mock_drive_service.permissions().create().execute.side_effect = http_error

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.share_document("test_doc_id", "user@example.com")

        assert "Failed to share document" in str(exc_info.value)

    def test_delete_document_success(
        self, docs_service: GoogleDocsService, mock_drive_service: Mock
    ) -> None:
        """Test deleting document"""
        mock_drive_service.files().delete().execute.return_value = None

        docs_service.delete_document("test_doc_id")

        # Verify the delete method was called with correct fileId
        mock_drive_service.files().delete.assert_called_with(fileId="test_doc_id")

    def test_delete_document_http_error(
        self, docs_service: GoogleDocsService, mock_drive_service: Mock
    ) -> None:
        """Test deleting document with HTTP error"""
        mock_resp = Mock()
        mock_resp.status = 404
        mock_resp.reason = "Not Found"
        http_error = HttpError(resp=mock_resp, content=b"Not found")

        mock_drive_service.files().delete().execute.side_effect = http_error

        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.delete_document("nonexistent_id")

        assert "Failed to delete document" in str(exc_info.value)

    def test_rate_limiter_integration(
        self, docs_service: GoogleDocsService, mock_docs_service: Mock
    ) -> None:
        """Test that rate limiter is called during API operations"""
        mock_docs_service.documents().create().execute.return_value = {
            "documentId": "test_id"
        }

        # Spy on rate limiter
        original_wait = docs_service.rate_limiter.wait_if_needed
        call_count = 0

        def counting_wait():
            nonlocal call_count
            call_count += 1
            original_wait()

        docs_service.rate_limiter.wait_if_needed = counting_wait

        docs_service.create_document("Test")

        assert call_count >= 1


class TestGoogleDocsServiceRetry:
    """Tests for retry behavior in GoogleDocsService"""

    @pytest.fixture
    def docs_service(self) -> GoogleDocsService:
        """Create service with mocked dependencies"""
        with patch("ai_writing.services.google.docs.build"):
            service = GoogleDocsService(Mock())
            return service

    def test_create_document_retries_on_http_error(
        self, docs_service: GoogleDocsService
    ) -> None:
        """Test that create_document retries on HTTP errors"""
        mock_resp = Mock()
        mock_resp.status = 500
        mock_resp.reason = "Internal Error"
        http_error = HttpError(resp=mock_resp, content=b"Error")

        # Fail twice, then succeed
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise http_error
            return {"documentId": "test_id"}

        docs_service.service = MagicMock()
        docs_service.service.documents().create().execute.side_effect = side_effect

        # Should eventually succeed after retries
        doc_id = docs_service.create_document("Test")
        assert doc_id == "test_id"
        assert call_count == 3

    def test_create_document_fails_after_max_retries(
        self, docs_service: GoogleDocsService
    ) -> None:
        """Test that create_document raises error after max retries"""
        mock_resp = Mock()
        mock_resp.status = 500
        mock_resp.reason = "Internal Error"
        http_error = HttpError(resp=mock_resp, content=b"Error")

        docs_service.service = MagicMock()
        docs_service.service.documents().create().execute.side_effect = http_error

        # Should fail after 3 retries
        with pytest.raises(GoogleDocsError) as exc_info:
            docs_service.create_document("Test")

        assert "Failed to create document" in str(exc_info.value)
