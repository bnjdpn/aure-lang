class AureError(Exception):
    """Base class for all Aure errors."""


class AureSyntaxError(AureError):
    """Raised when source text cannot be tokenized or parsed."""


class AureRuntimeError(AureError):
    """Raised when a program fails at runtime."""
