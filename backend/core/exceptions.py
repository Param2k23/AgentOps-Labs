class EnterpriseAgentLabError(Exception):
    """Base class for application errors."""


class ValidationError(EnterpriseAgentLabError):
    """Raised when request validation fails at the application boundary."""


class NotFoundException(EnterpriseAgentLabError):
    """Raised when a requested resource is not found."""
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail
        super().__init__(self.detail)


