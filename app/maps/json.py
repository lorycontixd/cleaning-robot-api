import json

import pydantic
from pydantic import BaseModel, Field, model_validator

from app.core.exceptions import InvalidMapContent
from app.core.map import Coordinate, Map, Tile

__all__ = ["parse_json"]


class JsonTile(BaseModel):
    # walkable + dirty omitted -> starts dirty (True)
    # non-walkable + dirty omitted -> starts clean (False)
    # non-walkable + dirty=True -> invalid
    x: int = Field(..., ge=0, description="The x-coordinate of the tile")
    y: int = Field(..., ge=0, description="The y-coordinate of the tile")
    walkable: bool = Field(..., description="Indicates if the tile is walkable")
    dirty: bool | None = Field(None, description="Indicates if the tile is dirty")

    @model_validator(mode="after")
    def check_valid_tile(self) -> "JsonTile":
        if not self.walkable and self.dirty:
            raise InvalidMapContent("Non-walkable tiles cannot be dirty")
        if self.dirty is None:  # omitted
            self.dirty = self.walkable
        return self


class JsonMap(BaseModel):
    rows: int = Field(..., ge=0, description="The number of rows in the map")
    cols: int = Field(..., ge=0, description="The number of columns in the map")
    tiles: list[JsonTile] = Field(..., description="The list of tiles in the map")

    @model_validator(mode="after")
    def check_valid_map(self) -> "JsonMap":
        if self.rows == 0 or self.cols == 0:
            raise InvalidMapContent("Map must have at least one row and one column")
        if len(self.tiles) != self.rows * self.cols:
            raise InvalidMapContent("The number of tiles does not match the expected count")
        seen = {(tile.x, tile.y) for tile in self.tiles}
        if len(seen) != len(self.tiles):
            raise InvalidMapContent("Duplicate tile coordinates found")
        if any(tile.x >= self.cols or tile.y >= self.rows for tile in self.tiles):
            raise InvalidMapContent("Tile coordinates are out of map bounds")
        return self


def parse_json(content: bytes) -> Map:
    if not content:
        raise InvalidMapContent("Map cannot be empty")
    try:
        data = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as ex:
        raise InvalidMapContent("Map must be valid JSON encoded text") from ex

    if not isinstance(data, dict):
        raise InvalidMapContent("Map content must be a JSON object")

    try:
        json_map = JsonMap(**data)
    except InvalidMapContent:
        raise
    except pydantic.ValidationError as ex:
        raise InvalidMapContent(f"Map content validation error: {ex.errors()}") from ex
    except TypeError as ex:
        raise InvalidMapContent(f"Map content type error: {ex}") from ex
    except Exception as ex:
        raise InvalidMapContent("Map content is invalid") from ex

    coordinates: dict[Coordinate, Tile] = {}
    for tile in json_map.tiles:
        coord = Coordinate(x=tile.x, y=tile.y)
        assert tile.dirty is not None
        coordinates[coord] = Tile(is_walkable=tile.walkable, is_dirty=tile.dirty)

    return Map(rows=json_map.rows, cols=json_map.cols, tiles=coordinates)
