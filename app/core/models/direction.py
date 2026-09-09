from enum import StrEnum


class Direction(StrEnum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def get_unit_delta(self) -> tuple[int, int]:
        if self is Direction.NORTH:
            return (0, -1)
        elif self is Direction.SOUTH:
            return (0, 1)
        elif self is Direction.EAST:
            return (1, 0)
        elif self is Direction.WEST:
            return (-1, 0)
        else:
            raise ValueError(f"Unknown direction: {self}")
