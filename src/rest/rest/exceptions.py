"""Application-level exceptions shared across apps.

Services raise these instead of building HTTP responses themselves, which
keeps business logic independent of the web framework. The mapping from
exception to HTTP status lives in one place: rest/exception_handler.py.
"""
from typing import Optional


class InvalidInputError(Exception):
    """The client sent data that breaks a business rule (maps to HTTP 400)."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field
