class EnterpriseAgentLabError(Exception):
    """Base class for application errors."""


class ValidationError(EnterpriseAgentLabError):
    """Raised when request validation fails at the application boundary."""

