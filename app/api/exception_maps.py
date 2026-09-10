from app.core.exceptions import (
    InvalidMapContent,
    InvalidStartPositionError,
    MapNotLoadedError,
    OutOfBoundsError,
    UnsupportedMapFormat,
)

_EXCEPTION_MAPPING = {
    UnsupportedMapFormat: 415,
    InvalidMapContent: 422,
    InvalidStartPositionError: 422,
    OutOfBoundsError: 422,
    MapNotLoadedError: 409,
}
