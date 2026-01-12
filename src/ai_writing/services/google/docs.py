"""Google Docs API service wrapper"""

import time
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ai_writing.core.exceptions import GoogleDocsError


class RateLimiter:
    """Rate limiter for Google Docs API (50 requests/minute safe limit)"""

    def __init__(self, max_calls: int = 50, period_seconds: int = 60):
        """Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the period
            period_seconds: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls: list[float] = []

    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded.

        This method removes expired calls from the tracking list and
        waits if the number of recent calls exceeds the limit.
        """
        now = time.time()

        # Remove calls outside the current period window
        self.calls = [t for t in self.calls if now - t < self.period]

        # If at limit, wait until oldest call expires
        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            wait_time = self.period - (now - oldest_call)
            if wait_time > 0:
                time.sleep(wait_time)
                # Clean up again after waiting
                now = time.time()
                self.calls = [t for t in self.calls if now - t < self.period]

        # Record this call
        self.calls.append(time.time())

    def reset(self) -> None:
        """Reset the rate limiter."""
        self.calls = []

    @property
    def remaining_calls(self) -> int:
        """Get the number of remaining calls in the current period."""
        now = time.time()
        recent_calls = [t for t in self.calls if now - t < self.period]
        return max(0, self.max_calls - len(recent_calls))


class GoogleDocsService:
    """Service for interacting with Google Docs API"""

    def __init__(self, credentials: Credentials):
        """Initialize the Google Docs service.

        Args:
            credentials: Valid Google OAuth2 credentials
        """
        self.credentials = credentials
        # Use Any type to avoid type checking issues with dynamic API methods
        self.service: Any = build("docs", "v1", credentials=credentials)
        self.drive_service: Any = build("drive", "v3", credentials=credentials)
        self.rate_limiter = RateLimiter()

    def create_document(self, title: str) -> str:
        """Create a new Google Document.

        Args:
            title: Title of the new document

        Returns:
            Document ID of the created document

        Raises:
            GoogleDocsError: If document creation fails
        """
        try:
            return self._create_document_with_retry(title)
        except HttpError as e:
            raise GoogleDocsError(f"Failed to create document: {e}") from e
        except Exception as e:
            if isinstance(e, GoogleDocsError):
                raise
            raise GoogleDocsError(f"Unexpected error creating document: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(HttpError),
        reraise=True,
    )
    def _create_document_with_retry(self, title: str) -> str:
        """Internal method with retry logic for document creation."""
        self.rate_limiter.wait_if_needed()

        body = {"title": title}
        doc = self.service.documents().create(body=body).execute()

        doc_id = doc.get("documentId")
        if not doc_id:
            raise GoogleDocsError("Failed to get document ID from response")

        return doc_id

    def batch_update(self, doc_id: str, requests: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute a batch update on a document.

        Args:
            doc_id: Document ID to update
            requests: List of update requests

        Returns:
            Response from the batch update API

        Raises:
            GoogleDocsError: If batch update fails
        """
        if not requests:
            return {"replies": []}

        try:
            return self._batch_update_with_retry(doc_id, requests)
        except HttpError as e:
            raise GoogleDocsError(f"Batch update failed: {e}") from e
        except Exception as e:
            if isinstance(e, GoogleDocsError):
                raise
            raise GoogleDocsError(f"Unexpected error in batch update: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(HttpError),
        reraise=True,
    )
    def _batch_update_with_retry(
        self, doc_id: str, requests: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Internal method with retry logic for batch update."""
        self.rate_limiter.wait_if_needed()

        body = {"requests": requests}
        response = (
            self.service.documents()
            .batchUpdate(documentId=doc_id, body=body)
            .execute()
        )

        return response

    def insert_text(self, doc_id: str, text: str, index: int = 1) -> int:
        """Insert text at the specified index in a document.

        Args:
            doc_id: Document ID
            text: Text to insert
            index: Position to insert at (1-based, default is start of document)

        Returns:
            New index after text insertion

        Raises:
            GoogleDocsError: If text insertion fails
        """
        if not text:
            return index

        requests = [
            {
                "insertText": {
                    "location": {"index": index},
                    "text": text,
                }
            }
        ]

        self.batch_update(doc_id, requests)
        # Return new index after insertion (text length + newline)
        return index + len(text)

    def insert_heading(
        self, doc_id: str, text: str, level: int, index: int
    ) -> int:
        """Insert a heading at the specified index.

        Args:
            doc_id: Document ID
            text: Heading text
            level: Heading level (1-6)
            index: Position to insert at

        Returns:
            New index after heading insertion

        Raises:
            GoogleDocsError: If insertion fails
        """
        if not text:
            return index

        # Add newline after heading text
        heading_text = text + "\n"
        end_index = index + len(heading_text)

        requests = [
            {
                "insertText": {
                    "location": {"index": index},
                    "text": heading_text,
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": end_index - 1},
                    "paragraphStyle": {"namedStyleType": f"HEADING_{level}"},
                    "fields": "namedStyleType",
                }
            },
        ]

        self.batch_update(doc_id, requests)
        return end_index

    def insert_image(
        self,
        doc_id: str,
        image_path: str | Path,
        index: int,
        width: int = 400,
        height: int = 300,
    ) -> int:
        """Insert an image into a document.

        The image is first uploaded to Google Drive, then inserted into the document.

        Args:
            doc_id: Document ID
            image_path: Path to the image file
            index: Position to insert the image
            width: Width of the image in points (default 400)
            height: Height of the image in points (default 300)

        Returns:
            New index after image insertion

        Raises:
            GoogleDocsError: If image insertion fails
        """
        try:
            image_path = Path(image_path)

            if not image_path.exists():
                raise GoogleDocsError(f"Image file not found: {image_path}")

            # Determine MIME type based on extension
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            ext = image_path.suffix.lower()
            mime_type = mime_types.get(ext, "image/png")

            # Upload image to Drive
            self.rate_limiter.wait_if_needed()

            file_metadata: dict[str, str] = {
                "name": image_path.name,
                "mimeType": mime_type,
            }
            media = MediaFileUpload(str(image_path), mimetype=mime_type)

            uploaded_file = (
                self.drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id,webContentLink")
                .execute()
            )

            file_id = uploaded_file.get("id")
            if not file_id:
                raise GoogleDocsError("Failed to get file ID after upload")

            # Make the file publicly accessible for embedding
            self.rate_limiter.wait_if_needed()
            self.drive_service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()

            # Get direct link for the image
            image_url = f"https://drive.google.com/uc?id={file_id}"

            # Insert image into document
            requests = [
                {
                    "insertInlineImage": {
                        "location": {"index": index},
                        "uri": image_url,
                        "objectSize": {
                            "width": {"magnitude": width, "unit": "PT"},
                            "height": {"magnitude": height, "unit": "PT"},
                        },
                    }
                }
            ]

            self.batch_update(doc_id, requests)
            # Image takes 1 index position + newline
            return index + 1

        except GoogleDocsError:
            raise
        except HttpError as e:
            raise GoogleDocsError(f"Failed to insert image: {e}") from e
        except Exception as e:
            raise GoogleDocsError(f"Unexpected error inserting image: {e}") from e

    def apply_heading_style(
        self, doc_id: str, start: int, end: int, level: int
    ) -> dict[str, Any]:
        """Apply a heading style to a range of text.

        Args:
            doc_id: Document ID
            start: Start index of the range
            end: End index of the range
            level: Heading level (1-6)

        Returns:
            Response from the batch update

        Raises:
            GoogleDocsError: If applying style fails
            ValueError: If level is not between 1 and 6
        """
        if not 1 <= level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {level}")

        heading_types = {
            1: "HEADING_1",
            2: "HEADING_2",
            3: "HEADING_3",
            4: "HEADING_4",
            5: "HEADING_5",
            6: "HEADING_6",
        }

        requests = [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": heading_types[level]},
                    "fields": "namedStyleType",
                }
            }
        ]

        return self.batch_update(doc_id, requests)

    def apply_bold_style(
        self, doc_id: str, start: int, end: int
    ) -> dict[str, Any]:
        """Apply bold style to a range of text.

        Args:
            doc_id: Document ID
            start: Start index of the range
            end: End index of the range

        Returns:
            Response from the batch update
        """
        requests = [
            {
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {"bold": True},
                    "fields": "bold",
                }
            }
        ]

        return self.batch_update(doc_id, requests)

    def get_document(self, doc_id: str) -> dict[str, Any]:
        """Get the full document content.

        Args:
            doc_id: Document ID

        Returns:
            Document content as a dictionary

        Raises:
            GoogleDocsError: If fetching document fails
        """
        try:
            self.rate_limiter.wait_if_needed()

            doc = self.service.documents().get(documentId=doc_id).execute()
            return doc

        except HttpError as e:
            raise GoogleDocsError(f"Failed to get document: {e}") from e
        except Exception as e:
            if isinstance(e, GoogleDocsError):
                raise
            raise GoogleDocsError(f"Unexpected error getting document: {e}") from e

    def get_document_url(self, doc_id: str) -> str:
        """Get the URL for a document.

        Args:
            doc_id: Document ID

        Returns:
            URL to edit the document
        """
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    def share_document(
        self,
        doc_id: str,
        email: str,
        role: str = "writer",
        send_notification: bool = True,
    ) -> None:
        """Share a document with a user.

        Args:
            doc_id: Document ID
            email: Email address to share with
            role: Permission role ('reader', 'writer', 'commenter')
            send_notification: Whether to send email notification

        Raises:
            GoogleDocsError: If sharing fails
        """
        try:
            self.rate_limiter.wait_if_needed()

            permission = {
                "type": "user",
                "role": role,
                "emailAddress": email,
            }

            self.drive_service.permissions().create(
                fileId=doc_id,
                body=permission,
                sendNotificationEmail=send_notification,
            ).execute()

        except HttpError as e:
            raise GoogleDocsError(f"Failed to share document: {e}") from e
        except Exception as e:
            if isinstance(e, GoogleDocsError):
                raise
            raise GoogleDocsError(f"Unexpected error sharing document: {e}") from e

    def delete_document(self, doc_id: str) -> None:
        """Delete a document (move to trash).

        Args:
            doc_id: Document ID

        Raises:
            GoogleDocsError: If deletion fails
        """
        try:
            self.rate_limiter.wait_if_needed()

            self.drive_service.files().delete(fileId=doc_id).execute()

        except HttpError as e:
            raise GoogleDocsError(f"Failed to delete document: {e}") from e
        except Exception as e:
            if isinstance(e, GoogleDocsError):
                raise
            raise GoogleDocsError(f"Unexpected error deleting document: {e}") from e
