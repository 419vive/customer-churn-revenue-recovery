"""Custom exception classes for Olist Analytics"""

from typing import Dict, Any, Optional

class OlistAnalyticsError(Exception):
    """Base exception for Olist Analytics application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'exception_type': self.__class__.__name__
        }

class DataValidationError(OlistAnalyticsError):
    """Raised when data validation fails"""
    pass

class ConfigurationError(OlistAnalyticsError):
    """Raised when configuration is invalid"""
    pass

class AnalysisError(OlistAnalyticsError):
    """Raised when analysis computation fails"""
    pass

class DataIntegrityError(OlistAnalyticsError):
    """Raised when data integrity checks fail"""
    pass

class CacheError(OlistAnalyticsError):
    """Raised when cache operations fail"""
    pass

class DatabaseError(OlistAnalyticsError):
    """Raised when database operations fail"""
    pass

class AuthenticationError(OlistAnalyticsError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(OlistAnalyticsError):
    """Raised when authorization fails"""
    pass