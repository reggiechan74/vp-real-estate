"""
Error Handling Module

Custom exceptions and error handling utilities for Location Overview.
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorSeverity(Enum):
    """Severity level of errors."""

    INFO = "info"  # Informational, no action needed
    WARNING = "warning"  # Data missing but report can continue
    ERROR = "error"  # Provider failed but fallback available
    CRITICAL = "critical"  # Cannot generate report


class ErrorCode(Enum):
    """User-facing error codes for the slash command."""

    INVALID_INPUT = "INVALID_INPUT"
    GEOCODE_FAIL = "GEOCODE_FAIL"
    NO_DATA_MUNICIPALITY = "NO_DATA_MUNICIPALITY"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TIMEOUT = "TIMEOUT"
    NOT_IN_ONTARIO = "NOT_IN_ONTARIO"
    PIN_NOT_SUPPORTED = "PIN_NOT_SUPPORTED"


# User-friendly error messages and retry guidance
ERROR_MESSAGES = {
    ErrorCode.INVALID_INPUT: {
        "message": "Invalid input format",
        "guidance": "Please provide a valid Ontario address or 9-digit PIN.",
    },
    ErrorCode.GEOCODE_FAIL: {
        "message": "Could not locate address",
        "guidance": "Please check the address spelling and include the city name (e.g., '100 Queen Street West, Toronto').",
    },
    ErrorCode.NO_DATA_MUNICIPALITY: {
        "message": "No data available for this municipality",
        "guidance": "This municipality may not be supported in the current version. Toronto and GTA municipalities have the best coverage.",
    },
    ErrorCode.RATE_LIMITED: {
        "message": "Too many requests",
        "guidance": "Please wait a moment and try again.",
    },
    ErrorCode.INTERNAL_ERROR: {
        "message": "An internal error occurred",
        "guidance": "Please try again. If the problem persists, contact support.",
    },
    ErrorCode.TIMEOUT: {
        "message": "Request timed out",
        "guidance": "The data sources are taking too long to respond. Please try again later.",
    },
    ErrorCode.NOT_IN_ONTARIO: {
        "message": "Location is not in Ontario",
        "guidance": "This tool only supports Ontario properties. Please provide an Ontario address.",
    },
    ErrorCode.PIN_NOT_SUPPORTED: {
        "message": "PIN lookup not yet supported",
        "guidance": "PIN lookup requires OnLand/Teranet integration (Phase 3). Please provide a municipal address instead.",
    },
}


class LocationOverviewError(Exception):
    """Base exception for Location Overview errors."""

    severity: ErrorSeverity = ErrorSeverity.ERROR
    code: ErrorCode = ErrorCode.INTERNAL_ERROR

    def __init__(
        self,
        message: str,
        code: Optional[ErrorCode] = None,
        severity: Optional[ErrorSeverity] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize error.

        Args:
            message: Error message
            code: Error code for user-facing display
            severity: Error severity
            details: Additional error details
        """
        super().__init__(message)
        if code:
            self.code = code
        if severity:
            self.severity = severity
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        error_info = ERROR_MESSAGES.get(self.code, {})
        return {
            "error": True,
            "code": self.code.value,
            "message": str(self),
            "user_message": error_info.get("message", str(self)),
            "guidance": error_info.get("guidance", ""),
            "severity": self.severity.value,
            "details": self.details,
        }


class GeocodingError(LocationOverviewError):
    """Failed to geocode input."""

    severity = ErrorSeverity.CRITICAL
    code = ErrorCode.GEOCODE_FAIL


class ValidationError(LocationOverviewError):
    """Input validation failed."""

    severity = ErrorSeverity.CRITICAL
    code = ErrorCode.INVALID_INPUT


class ProviderError(LocationOverviewError):
    """Data provider failed."""

    severity = ErrorSeverity.WARNING
    code = ErrorCode.INTERNAL_ERROR

    def __init__(
        self,
        message: str,
        provider_name: str,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.provider_name = provider_name
        self.details["provider"] = provider_name


class RateLimitError(LocationOverviewError):
    """Rate limit exceeded."""

    severity = ErrorSeverity.WARNING
    code = ErrorCode.RATE_LIMITED


class TimeoutError(LocationOverviewError):
    """Request timed out."""

    severity = ErrorSeverity.WARNING
    code = ErrorCode.TIMEOUT


class NotInOntarioError(LocationOverviewError):
    """Location is not in Ontario."""

    severity = ErrorSeverity.CRITICAL
    code = ErrorCode.NOT_IN_ONTARIO


def format_user_error(error: Exception) -> str:
    """
    Format an error for user display.

    Args:
        error: Exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, LocationOverviewError):
        error_info = ERROR_MESSAGES.get(error.code, {})
        message = error_info.get("message", str(error))
        guidance = error_info.get("guidance", "")
        return f"{message}. {guidance}" if guidance else message

    return f"An error occurred: {str(error)}"


def is_retryable(error: Exception) -> bool:
    """
    Check if an error is retryable.

    Args:
        error: Exception to check

    Returns:
        True if the operation can be retried
    """
    if isinstance(error, LocationOverviewError):
        return error.code in [
            ErrorCode.RATE_LIMITED,
            ErrorCode.TIMEOUT,
            ErrorCode.INTERNAL_ERROR,
        ]
    return False
