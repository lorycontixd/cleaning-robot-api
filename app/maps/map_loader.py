from app.core.map import Map
from app.maps.json import parse_json
from app.maps.txt import parse_txt

PARSERS = {".txt": parse_txt, ".json": parse_json}


def load_map(filename: str, content: bytes) -> Map:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    parser = PARSERS.get(f".{suffix}")

    # format first (415), then empty content (422)
    if not parser:
        from app.core.exceptions import UnsupportedMapFormat

        raise UnsupportedMapFormat(f"Unsupported map format: .{suffix}")
    if not content:
        from app.core.exceptions import InvalidMapContent

        raise InvalidMapContent("Map content is empty")

    return parser(content)
