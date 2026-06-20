"""
Custom exception hierarchy for the application.
"""

from typing import Any, Optional


class CafePOSException(Exception):
    """Base exception for the CafePOS application."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(CafePOSException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=msg, status_code=404)


class AlreadyExistsException(CafePOSException):
    """Resource already exists."""

    def __init__(self, resource: str = "Resource", field: str = "", value: Any = ""):
        msg = f"{resource} already exists"
        if field and value:
            msg = f"{resource} with {field} '{value}' already exists"
        super().__init__(message=msg, status_code=409)


class UnauthorizedException(CafePOSException):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(CafePOSException):
    """Access denied."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, status_code=403)


class BadRequestException(CafePOSException):
    """Invalid request data."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)


class InvalidStateTransitionException(CafePOSException):
    """Invalid order or session state transition."""

    def __init__(self, current_state: str, target_state: str):
        msg = f"Cannot transition from '{current_state}' to '{target_state}'"
        super().__init__(message=msg, status_code=422)


class SessionNotOpenException(CafePOSException):
    """POS session is not open."""

    def __init__(self):
        super().__init__(
            message="No active POS session found. Please open a session first.",
            status_code=422,
        )


class CouponValidationException(CafePOSException):
    """Coupon validation failed."""

    def __init__(self, message: str = "Invalid coupon"):
        super().__init__(message=message, status_code=422)


class PaymentException(CafePOSException):
    """Payment processing error."""

    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message=message, status_code=422)
