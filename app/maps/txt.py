from app.core.exceptions import InvalidMapContent
from app.core.map import Coordinate, Map, Tile


def parse_txt(content: bytes) -> Map:
    if not content:
        raise InvalidMapContent("Map cannot be empty")
    try:
        text = content.replace(b"\r\n", b"\n").decode("utf-8")  # Windows and Unix endings
    except UnicodeDecodeError as ex:
        raise InvalidMapContent("Map must be valid UTF-8 encoded text") from ex

    lines = text.split("\n")

    if not lines:
        raise InvalidMapContent("Map cannot be empty")
    if lines[-1] == "":
        lines.pop()  # allow trailing newline, but remove it

    last_row_length: int | None = None
    tiles = {}
    for i, line in enumerate(lines):
        if not line:
            raise InvalidMapContent(f"Empty row at row {i}")
        if last_row_length is None:
            last_row_length = len(line)
        elif len(line) != last_row_length:
            raise InvalidMapContent(f"Inconsistent row length at row {i}")
        for j, char in enumerate(line):
            if char not in ("o", "x"):
                raise InvalidMapContent(f"Invalid character in map: {char}. Position ({i}, {j})")
            coord = Coordinate(x=j, y=i)  # i = rows (y), j = columns (x)
            tile = {coord: Tile(is_walkable=(char == "o"), is_dirty=char == "o")}
            tiles.update(tile)
    rows = len(lines)
    cols = max((len(line) for line in lines), default=0)
    return Map(rows, cols, tiles)
