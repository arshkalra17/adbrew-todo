from typing import Optional


class InvalidInputError(Exception):
    """The client sent data that breaks a business rule (maps to HTTP 400)."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field
