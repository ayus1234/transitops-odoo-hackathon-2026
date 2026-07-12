"""
Custom exception classes for the application.
"""
from typing import Optional, Any


class TransitOpsException(Exception):
    """Base exception for TransitOps application."""
    
    def __init__(
        self,
        message: str,
        code: str = "TRANSITOPS_ERROR",
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(TransitOpsException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="VAL_001", details=details)


class DuplicateEntryError(TransitOpsException):
    """Exception for duplicate entry errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="VAL_004", details=details)


class NotFoundError(TransitOpsException):
    """Exception for entity not found errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="VAL_005", details=details)


class BusinessLogicError(TransitOpsException):
    """Exception for business logic violations."""
    
    def __init__(self, message: str, code: str = "BIZ_001", details: Optional[dict[str, Any]] = None):
        super().__init__(message, code=code, details=details)


class AuthenticationError(TransitOpsException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="AUTH_001", details=details)


class AuthorizationError(TransitOpsException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="AUTH_004", details=details)
