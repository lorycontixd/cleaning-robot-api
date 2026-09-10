from dataclasses import dataclass
from typing import TypedDict


# TypedDict for OpenAPI schema
class CoordinateDict(TypedDict):
    x: int
    y: int


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

    def moved(self, dx: int, dy: int, steps: int = 1) -> "Coordinate":
        return Coordinate(x=self.x + dx * steps, y=self.y + dy * steps)

    def to_dict(self) -> CoordinateDict:
        return {"x": self.x, "y": self.y}
