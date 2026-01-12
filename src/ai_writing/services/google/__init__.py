"""Google services"""

from ai_writing.services.google.auth import GoogleAuthManager, SCOPES
from ai_writing.services.google.docs import GoogleDocsService, RateLimiter

__all__ = ["GoogleAuthManager", "GoogleDocsService", "RateLimiter", "SCOPES"]
