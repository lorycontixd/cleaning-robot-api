class TestDirection:
    def test_unit_delta(self):
        from app.core.models.direction import Direction

        assert Direction.NORTH.get_unit_delta() == (0, -1)
        assert Direction.SOUTH.get_unit_delta() == (0, 1)
        assert Direction.EAST.get_unit_delta() == (1, 0)
        assert Direction.WEST.get_unit_delta() == (-1, 0)
