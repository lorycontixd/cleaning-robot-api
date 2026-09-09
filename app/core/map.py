from dataclasses import dataclass

from app.core.exceptions import OutOfBoundsError
from app.core.models.coordinate import Coordinate


@dataclass(frozen=True)
class Tile:
    is_walkable: bool
    is_dirty: bool


class Map:
    def __init__(self, rows: int, cols: int, tiles: dict[Coordinate, Tile]):
        self.rows = rows
        self.cols = cols
        self.tiles = tiles
        self._validate_map()

    def _validate_map(self):
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("Map must have positive number of rows and columns.")
        for y in range(self.rows):
            for x in range(self.cols):
                coordinate = Coordinate(x, y)
                if coordinate not in self.tiles:
                    raise ValueError(f"Missing tile at coordinate ({x}, {y}).")

    def __getitem__(self, key):
        i, j = key
        coordinate = Coordinate(i, j)
        if not self.in_bounds(coordinate):
            raise IndexError(f"Coordinate ({i}, {j}) is out of map bounds.")
        if coordinate in self.tiles:
            return self.tiles[coordinate]
        raise IndexError(f"Coordinate ({i}, {j}) is out of map bounds.")

    @staticmethod
    def generate_random(
        rows: int,
        cols: int,
        walkable_probability: float = 0.8,
        dirty_probability: float = 0.5,
    ) -> "Map":
        import random

        tiles = {}
        for y in range(rows):
            for x in range(cols):
                is_walkable = random.random() < walkable_probability
                is_dirty = random.random() < dirty_probability if is_walkable else False
                tiles[Coordinate(x, y)] = Tile(is_walkable=is_walkable, is_dirty=is_dirty)
        return Map(rows, cols, tiles)

    @property
    def walkable_tiles(self) -> int:
        return sum(1 for tile in self.tiles.values() if tile.is_walkable)

    def is_walkable(self, coordinate: Coordinate) -> bool:
        tile = self.tiles.get(coordinate)
        return tile.is_walkable if tile else False

    def is_dirty(self, coordinate: Coordinate) -> bool:
        tile = self.tiles.get(coordinate)
        return tile.is_dirty if tile else False

    def in_bounds(self, coordinate: Coordinate) -> bool:
        return 0 <= coordinate.x < self.cols and 0 <= coordinate.y < self.rows

    def is_valid(self, coordinate: Coordinate) -> bool:
        return self.in_bounds(coordinate) and self.is_walkable(coordinate)

    def clean(self, coordinate: Coordinate):
        if not self.in_bounds(coordinate):
            raise OutOfBoundsError(f"Coordinate {coordinate} is out of map bounds.")
        tile = self.tiles[coordinate]
        self.tiles[coordinate] = Tile(is_walkable=tile.is_walkable, is_dirty=False)

    def render(self):
        string = ""
        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tiles.get(Coordinate(x, y))
                if tile is None:
                    string += " "
                elif not tile.is_walkable:
                    string += "x"
                elif tile.is_walkable:
                    string += "o" if tile.is_dirty else "."
            string += "\n"
        return string
