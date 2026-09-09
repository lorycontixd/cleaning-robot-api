from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

    def moved(self, dx: int, dy: int, steps: int = 1) -> "Coordinate":
        return Coordinate(x=self.x + dx * steps, y=self.y + dy * steps)

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y}
