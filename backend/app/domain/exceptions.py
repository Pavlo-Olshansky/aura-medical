class DomainError(Exception):
    """Base domain exception."""


class EntityNotFound(DomainError):
    """Entity not found."""


class AuthenticationError(DomainError):
    """Authentication failed."""


class ReferenceInUse(DomainError):
    """Cannot delete — entity is referenced by other records."""
