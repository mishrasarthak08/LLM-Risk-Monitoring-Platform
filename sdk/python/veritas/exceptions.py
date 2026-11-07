"""
VERITAS AI — SDK Exceptions
"""

class VeritasException(Exception):
    """Base exception for all VERITAS SDK errors."""
    pass


class VeritasConfigurationError(VeritasException):
    """Raised when the client is misconfigured (e.g. missing API key)."""
    pass


class VeritasIngestionError(VeritasException):
    """Raised when trace delivery fails after retries."""
    pass

