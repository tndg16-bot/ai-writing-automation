"""OAuth2 authentication for Google APIs"""

import json
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ai_writing.core.exceptions import GoogleDocsError

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


class GoogleAuthManager:
    """Manages OAuth2 authentication for Google APIs"""

    def __init__(self, token_file: Path, credentials_file: Path | None = None):
        """Initialize the auth manager.

        Args:
            token_file: Path to store/load the OAuth token
            credentials_file: Path to the OAuth credentials JSON file (optional)
        """
        self.token_file = Path(token_file)
        self.credentials_file = Path(credentials_file) if credentials_file else None
        self._creds: Credentials | None = None

    @property
    def creds(self) -> Credentials | None:
        """Get the current credentials."""
        return self._creds

    @creds.setter
    def creds(self, value: Credentials | None) -> None:
        """Set the credentials."""
        self._creds = value

    def load_credentials(
        self, client_id: str | None = None, client_secret: str | None = None
    ) -> Credentials:
        """Load or create OAuth2 credentials.

        Priority:
        1. Try loading from token_file
        2. If expired, refresh the token
        3. If no token, create new via OAuth flow
        4. Save token for reuse

        Args:
            client_id: OAuth client ID (used if no credentials_file)
            client_secret: OAuth client secret (used if no credentials_file)

        Returns:
            Valid Google OAuth2 credentials

        Raises:
            GoogleDocsError: If authentication fails
        """
        try:
            # Step 1: Try loading existing token
            if self.token_file.exists():
                self._creds = self._load_token_from_file()

            # Step 2: Refresh if expired
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    self._creds.refresh(Request())
                    self._save_token()
                    return self._creds
                except Exception:
                    # Token refresh failed, need to re-authenticate
                    self._creds = None

            # Step 3: Return valid credentials if available
            if self._creds and self._creds.valid:
                return self._creds

            # Step 4: Create new credentials via OAuth flow
            self._creds = self._run_oauth_flow(client_id, client_secret)

            # Step 5: Save token for reuse
            self._save_token()

            return self._creds

        except GoogleDocsError:
            raise
        except Exception as e:
            raise GoogleDocsError(f"Failed to load credentials: {e}") from e

    def _load_token_from_file(self) -> Credentials:
        """Load credentials from the token file.

        Returns:
            Credentials loaded from file

        Raises:
            GoogleDocsError: If loading fails
        """
        try:
            with open(self.token_file, "r") as f:
                token_data = json.load(f)

            return Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes", SCOPES),
            )
        except Exception as e:
            raise GoogleDocsError(f"Failed to load token from file: {e}") from e

    def _run_oauth_flow(
        self, client_id: str | None = None, client_secret: str | None = None
    ) -> Credentials:
        """Run the OAuth2 flow to get new credentials.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret

        Returns:
            New OAuth2 credentials

        Raises:
            GoogleDocsError: If OAuth flow fails
        """
        try:
            if self.credentials_file and self.credentials_file.exists():
                # Use credentials file
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
            elif client_id and client_secret:
                # Build client config from parameters
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost"],
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                raise GoogleDocsError(
                    "Either credentials_file or client_id/client_secret must be provided"
                )

            # Run local server flow for authentication
            creds = flow.run_local_server(port=0)

            # The flow returns google.oauth2.credentials.Credentials
            # Convert to ensure we have the right type with known token_uri
            token_uri = getattr(creds, "_token_uri", "https://oauth2.googleapis.com/token")
            return Credentials(
                token=creds.token,
                refresh_token=creds.refresh_token,
                token_uri=token_uri,
                client_id=creds.client_id,
                client_secret=creds.client_secret,
                scopes=list(creds.scopes) if creds.scopes else SCOPES,
            )

        except GoogleDocsError:
            raise
        except Exception as e:
            raise GoogleDocsError(f"OAuth flow failed: {e}") from e

    def _save_token(self) -> None:
        """Save the current credentials to the token file.

        Raises:
            GoogleDocsError: If saving fails
        """
        if not self._creds:
            return

        try:
            # Ensure parent directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)

            # Save credentials to JSON file
            token_data: dict[str, Any] = {
                "token": self._creds.token,
                "refresh_token": self._creds.refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": self._creds.client_id,
                "client_secret": self._creds.client_secret,
                "scopes": list(self._creds.scopes) if self._creds.scopes else SCOPES,
            }

            with open(self.token_file, "w") as f:
                json.dump(token_data, f, indent=2)

        except Exception as e:
            raise GoogleDocsError(f"Failed to save token: {e}") from e

    def revoke_credentials(self) -> None:
        """Revoke current credentials and delete token file."""
        try:
            if self._creds and self._creds.token:
                # Revoke token via HTTP request
                import urllib.request
                import urllib.error

                revoke_url = f"https://oauth2.googleapis.com/revoke?token={self._creds.token}"
                try:
                    urllib.request.urlopen(revoke_url)
                except urllib.error.HTTPError:
                    # Ignore revocation errors
                    pass
        except Exception:
            # Ignore revoke errors
            pass

        # Delete token file
        if self.token_file.exists():
            self.token_file.unlink()

        self._creds = None

    @property
    def is_authenticated(self) -> bool:
        """Check if valid credentials are available."""
        return self._creds is not None and self._creds.valid
