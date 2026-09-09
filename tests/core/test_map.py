import pytest

from app.core.exceptions import OutOfBoundsError
from app.core.models.coordinate import Coordinate


class TestMap:
    def test_walkable_tiles(self, sample_map):
        assert sample_map.walkable_tiles == 5

    def test_23_map(self, sample_23_map):
        assert sample_23_map.in_bounds(Coordinate(0, 0)) is True
        assert sample_23_map.in_bounds(Coordinate(1, 0)) is True
        assert sample_23_map.in_bounds(Coordinate(2, 0)) is True
        assert sample_23_map.in_bounds(Coordinate(0, 1)) is True
        assert sample_23_map.in_bounds(Coordinate(1, 1)) is True
        assert sample_23_map.in_bounds(Coordinate(2, 1)) is True
        assert sample_23_map.in_bounds(Coordinate(0, 2)) is False
        assert sample_23_map.in_bounds(Coordinate(1, 2)) is False
        assert sample_23_map.in_bounds(Coordinate(2, 2)) is False

    def test_in_bounds(self, sample_map):
        assert sample_map.in_bounds(Coordinate(0, 0)) is True
        assert sample_map.in_bounds(Coordinate(2, 2)) is True
        assert sample_map.in_bounds(Coordinate(3, 3)) is False
        assert sample_map.in_bounds(Coordinate(-1, 0)) is False
        assert sample_map.in_bounds(Coordinate(0, -1)) is False

    def test_is_walkable(self, sample_map):
        assert sample_map.is_walkable(Coordinate(0, 0)) is True
        assert sample_map.is_walkable(Coordinate(0, 1)) is False
        assert sample_map.is_walkable(Coordinate(1, 1)) is True
        assert sample_map.is_walkable(Coordinate(2, 2)) is True
        assert sample_map.is_walkable(Coordinate(3, 3)) is False

    def test_is_valid(self, sample_map):
        assert sample_map.is_valid(Coordinate(0, 0)) is True
        assert sample_map.is_valid(Coordinate(0, 1)) is False
        assert sample_map.is_valid(Coordinate(1, 1)) is True
        assert sample_map.is_valid(Coordinate(2, 2)) is True
        assert sample_map.is_valid(Coordinate(3, 3)) is False

    def test_clean(self, sample_map):
        # correctly flips the dirty status of a valid tile
        coordinate = Coordinate(0, 0)
        assert sample_map.is_dirty(coordinate) is True
        sample_map.clean(coordinate)
        assert sample_map.is_dirty(coordinate) is False

        coordinate = Coordinate(1, 1)
        assert sample_map.is_dirty(coordinate) is True
        sample_map.clean(coordinate)
        assert sample_map.is_dirty(coordinate) is False

        # a non-dirty tile remains non-dirty after cleaning
        coordinate = Coordinate(1, 0)
        assert sample_map.is_dirty(coordinate) is False
        sample_map.clean(coordinate)
        assert sample_map.is_dirty(coordinate) is False

        # cleaning an out-of-bounds coordinate should not raise an error
        coordinate = Coordinate(3, 3)

        with pytest.raises(OutOfBoundsError):
            sample_map.clean(coordinate)
