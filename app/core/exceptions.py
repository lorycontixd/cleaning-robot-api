# Used in FastAPI main application for handling domain-specific errors
class DomainError(Exception):
    """Base class for all domain-specific errors."""

    pass


class UnsupportedMapFormat(DomainError):
    """Raised when an unsupported map format is encountered."""

    pass


class InvalidMapContent(DomainError):
    """Raised when the content of a map is invalid."""

    pass


class MapNotLoadedError(DomainError):
    """Raised when an operation requires a map, but no map is currently loaded."""

    pass


class OutOfBoundsError(DomainError):
    """Raised when a specified coordinate is out of the map bounds."""

    pass


class InvalidStartPositionError(DomainError):
    """Raised when the starting position of the robot is invalid."""

    pass
