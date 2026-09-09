from app.core.models.coordinate import Coordinate


class TestCoordinates:
    def test_moved(self):
        coord = Coordinate(x=1, y=1)
        moved_coord = coord.moved(dx=1, dy=1)
        assert moved_coord.x == 2
        assert moved_coord.y == 2

    def test_moved_multistep(self):
        coord = Coordinate(x=1, y=1)
        moved_coord = coord.moved(dx=2, dy=3)
        assert moved_coord.x == 3
        assert moved_coord.y == 4

    def test_equality(self):
        # equality test
        coord1 = Coordinate(x=1, y=1)
        coord2 = Coordinate(x=1, y=1)
        coord3 = Coordinate(x=2, y=2)
        assert coord1 == coord2
        assert coord1 != coord3

        # hashability test - used in Map.tiles
        coord_set = {coord1, coord2, coord3}
        assert coord1 in coord_set
        assert coord2 in coord_set
        assert coord3 in coord_set

    def test_to_dict(self):
        coord = Coordinate(x=1, y=1)
        coord_dict = coord.to_dict()
        assert coord_dict == {"x": 1, "y": 1}
