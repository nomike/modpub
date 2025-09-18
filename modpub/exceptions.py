class ModpubError(Exception):
    """Base exception for modpub."""

class AuthenticationError(ModpubError):
    """Raised when a provider cannot authenticate."""

class NotFoundError(ModpubError):
    """Raised when an entity is not found remotely."""

class ValidationError(ModpubError):
    """Raised for invalid inputs."""
