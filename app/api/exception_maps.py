from app.core.exceptions import (
    InvalidMapContent,
    InvalidStartPositionError,
    MapNotLoadedError,
    UnsupportedMapFormat,
)

_EXCEPTION_MAPPING = {
    UnsupportedMapFormat: 415,
    InvalidMapContent: 422,
    InvalidStartPositionError: 422,
    MapNotLoadedError: 409,
}
