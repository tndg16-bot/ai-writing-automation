"""Unit tests for Google OAuth2 authentication manager"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from google.oauth2.credentials import Credentials

from ai_writing.services.google.auth import GoogleAuthManager, SCOPES
from ai_writing.core.exceptions import GoogleDocsError


class TestGoogleAuthManager:
    """Tests for GoogleAuthManager class"""

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory for test files"""
        return tmp_path

    @pytest.fixture
    def token_file(self, temp_dir: Path) -> Path:
        """Path for token file"""
        return temp_dir / "token.json"

    @pytest.fixture
    def credentials_file(self, temp_dir: Path) -> Path:
        """Path for credentials file"""
        return temp_dir / "credentials.json"

    @pytest.fixture
    def auth_manager(self, token_file: Path) -> GoogleAuthManager:
        """Create an auth manager instance"""
        return GoogleAuthManager(token_file=token_file)

    @pytest.fixture
    def valid_token_data(self) -> dict:
        """Valid token data for testing"""
        return {
            "token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "scopes": SCOPES,
        }

    def test_init_with_token_file_only(self, token_file: Path) -> None:
        """Test initialization with just token file"""
        manager = GoogleAuthManager(token_file=token_file)

        assert manager.token_file == token_file
        assert manager.credentials_file is None
        assert manager.creds is None

    def test_init_with_credentials_file(
        self, token_file: Path, credentials_file: Path
    ) -> None:
        """Test initialization with both token and credentials files"""
        manager = GoogleAuthManager(
            token_file=token_file, credentials_file=credentials_file
        )

        assert manager.token_file == token_file
        assert manager.credentials_file == credentials_file

    def test_load_credentials_from_existing_valid_token(
        self, auth_manager: GoogleAuthManager, token_file: Path, valid_token_data: dict
    ) -> None:
        """Test loading credentials from existing valid token file"""
        # Write valid token file
        with open(token_file, "w") as f:
            json.dump(valid_token_data, f)

        # Mock the Credentials class to return valid credentials
        with patch.object(Credentials, "valid", True):
            with patch.object(Credentials, "expired", False):
                creds = auth_manager.load_credentials()

        assert creds is not None
        assert auth_manager.creds is not None

    def test_load_credentials_refresh_expired_token(
        self, auth_manager: GoogleAuthManager, token_file: Path, valid_token_data: dict
    ) -> None:
        """Test refreshing expired token"""
        # Write token file
        with open(token_file, "w") as f:
            json.dump(valid_token_data, f)

        # Create mock credentials
        mock_creds = Mock(spec=Credentials)
        mock_creds.expired = True
        mock_creds.valid = True
        mock_creds.refresh_token = "test_refresh_token"
        mock_creds.token = "new_access_token"
        mock_creds.client_id = "test_client_id"
        mock_creds.client_secret = "test_client_secret"
        mock_creds.scopes = SCOPES

        with patch.object(
            GoogleAuthManager, "_load_token_from_file", return_value=mock_creds
        ):
            with patch("ai_writing.services.google.auth.Request"):
                creds = auth_manager.load_credentials()

        assert creds is not None
        mock_creds.refresh.assert_called_once()

    def test_load_credentials_no_token_file_requires_flow(
        self, auth_manager: GoogleAuthManager
    ) -> None:
        """Test that missing token file triggers OAuth flow"""
        # Mock the OAuth flow
        mock_creds = Mock(spec=Credentials)
        mock_creds.token = "new_token"
        mock_creds.refresh_token = "new_refresh"
        mock_creds.client_id = "client_id"
        mock_creds.client_secret = "client_secret"
        mock_creds.scopes = SCOPES

        with patch.object(
            GoogleAuthManager, "_run_oauth_flow", return_value=mock_creds
        ) as mock_flow:
            creds = auth_manager.load_credentials(
                client_id="test_id", client_secret="test_secret"
            )

        assert creds is not None
        mock_flow.assert_called_once_with("test_id", "test_secret")

    def test_load_credentials_error_without_credentials(
        self, auth_manager: GoogleAuthManager
    ) -> None:
        """Test error when no credentials file or client_id/secret provided"""
        with pytest.raises(GoogleDocsError) as exc_info:
            auth_manager.load_credentials()

        assert "Either credentials_file or client_id/client_secret" in str(
            exc_info.value
        )

    def test_run_oauth_flow_with_credentials_file(
        self, token_file: Path, credentials_file: Path
    ) -> None:
        """Test OAuth flow with credentials file"""
        # Create a mock credentials file
        creds_data = {
            "installed": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        with open(credentials_file, "w") as f:
            json.dump(creds_data, f)

        manager = GoogleAuthManager(
            token_file=token_file, credentials_file=credentials_file
        )

        # Mock the flow
        mock_flow_instance = Mock()
        mock_creds = Mock()
        mock_creds.token = "new_token"
        mock_creds.refresh_token = "new_refresh"
        mock_creds.client_id = "client_id"
        mock_creds.client_secret = "client_secret"
        mock_creds.scopes = SCOPES
        mock_creds._token_uri = "https://oauth2.googleapis.com/token"
        mock_flow_instance.run_local_server.return_value = mock_creds

        with patch(
            "ai_writing.services.google.auth.InstalledAppFlow.from_client_secrets_file",
            return_value=mock_flow_instance,
        ):
            result = manager._run_oauth_flow()

        assert result is not None

    def test_run_oauth_flow_with_client_id_secret(
        self, auth_manager: GoogleAuthManager
    ) -> None:
        """Test OAuth flow with client_id and client_secret"""
        mock_flow_instance = Mock()
        mock_creds = Mock()
        mock_creds.token = "new_token"
        mock_creds.refresh_token = "new_refresh"
        mock_creds.client_id = "client_id"
        mock_creds.client_secret = "client_secret"
        mock_creds.scopes = SCOPES
        mock_creds._token_uri = "https://oauth2.googleapis.com/token"
        mock_flow_instance.run_local_server.return_value = mock_creds

        with patch(
            "ai_writing.services.google.auth.InstalledAppFlow.from_client_config",
            return_value=mock_flow_instance,
        ):
            result = auth_manager._run_oauth_flow(
                client_id="test_id", client_secret="test_secret"
            )

        assert result is not None

    def test_save_token(
        self, auth_manager: GoogleAuthManager, token_file: Path
    ) -> None:
        """Test saving token to file"""
        # Set up mock credentials
        mock_creds = Mock(spec=Credentials)
        mock_creds.token = "test_token"
        mock_creds.refresh_token = "test_refresh"
        mock_creds.client_id = "test_client_id"
        mock_creds.client_secret = "test_client_secret"
        mock_creds.scopes = SCOPES

        auth_manager._creds = mock_creds
        auth_manager._save_token()

        # Verify file was created
        assert token_file.exists()

        # Verify content
        with open(token_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data["token"] == "test_token"
        assert saved_data["refresh_token"] == "test_refresh"
        assert saved_data["client_id"] == "test_client_id"
        assert saved_data["client_secret"] == "test_client_secret"

    def test_save_token_creates_directory(
        self, temp_dir: Path
    ) -> None:
        """Test that save_token creates parent directory if needed"""
        nested_token_file = temp_dir / "nested" / "dir" / "token.json"
        manager = GoogleAuthManager(token_file=nested_token_file)

        mock_creds = Mock(spec=Credentials)
        mock_creds.token = "test_token"
        mock_creds.refresh_token = "test_refresh"
        mock_creds.client_id = "test_client_id"
        mock_creds.client_secret = "test_client_secret"
        mock_creds.scopes = SCOPES

        manager._creds = mock_creds
        manager._save_token()

        assert nested_token_file.exists()

    def test_revoke_credentials(
        self, auth_manager: GoogleAuthManager, token_file: Path, valid_token_data: dict
    ) -> None:
        """Test revoking credentials"""
        # Create token file
        with open(token_file, "w") as f:
            json.dump(valid_token_data, f)

        mock_creds = Mock(spec=Credentials)
        mock_creds.token = "test_token"
        auth_manager._creds = mock_creds

        with patch("urllib.request.urlopen"):
            auth_manager.revoke_credentials()

        assert auth_manager.creds is None
        assert not token_file.exists()

    def test_is_authenticated_true(self, auth_manager: GoogleAuthManager) -> None:
        """Test is_authenticated returns True for valid credentials"""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        auth_manager._creds = mock_creds

        assert auth_manager.is_authenticated is True

    def test_is_authenticated_false_no_creds(
        self, auth_manager: GoogleAuthManager
    ) -> None:
        """Test is_authenticated returns False when no credentials"""
        assert auth_manager.is_authenticated is False

    def test_is_authenticated_false_invalid_creds(
        self, auth_manager: GoogleAuthManager
    ) -> None:
        """Test is_authenticated returns False for invalid credentials"""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = False
        auth_manager._creds = mock_creds

        assert auth_manager.is_authenticated is False

    def test_scopes_constant(self) -> None:
        """Test that SCOPES contains expected values"""
        assert "https://www.googleapis.com/auth/documents" in SCOPES
        assert "https://www.googleapis.com/auth/drive" in SCOPES
