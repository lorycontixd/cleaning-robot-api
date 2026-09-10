import pytest

from app.core.exceptions import InvalidStartPositionError, MapNotLoadedError
from app.core.map import Map
from app.core.models.action import Action, Direction
from app.core.models.coordinate import Coordinate
from app.core.models.robot import RobotModel
from app.services.cleaning_service import CleaningService
from app.storage.map_store import MapStore


class TestPreconditionsCleaningService:
    def test_setup(self, cleaning_service: CleaningService):
        # makes sure cleaning_service fixture is properly set up
        assert cleaning_service is not None

    def test_preconditions(
        self, sample_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = []

        # test map not loaded scenario
        with pytest.raises(MapNotLoadedError):
            _ = cleaning_service.clean(
                start=start,
                robot_model=robot_model,
                actions=actions,
            )
        # test out-of-bounds start position
        map_store.load(sample_map)

        start = Coordinate(2, 3)
        with pytest.raises(InvalidStartPositionError):
            _ = cleaning_service.clean(
                start=start,
                robot_model=robot_model,
                actions=actions,
            )

        # find a non-walkable tile on the map - test invalid start position
        non_walkable_tile = next(
            coord for coord, tile in sample_map.tiles.items() if not tile.is_walkable
        )
        assert non_walkable_tile is not None

        with pytest.raises(InvalidStartPositionError):
            _ = cleaning_service.clean(
                start=non_walkable_tile,
                robot_model=robot_model,
                actions=actions,
            )


class TestStartingTile:
    def test_invalid_starting_tile(
        self, sample_map: Map, map_store, cleaning_service: CleaningService
    ):
        non_walkable_tile = Coordinate(0, 1)
        map_store.load(sample_map)
        with pytest.raises(InvalidStartPositionError):
            _ = cleaning_service.clean(
                start=non_walkable_tile,
                robot_model=RobotModel.BASIC,
                actions=[],
            )

    def test_empty_actions(self, sample_map: Map, map_store, cleaning_service: CleaningService):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = []

        map_store.load(sample_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )
        assert result is not None
        assert result.submitted_actions == 0
        assert result.successful_steps == 0
        assert len(result.cleaned_tiles) == 1
        assert result.cleaned_tiles[0] == {"x": 0, "y": 0}
        assert sample_map[0, 0].is_dirty is False
        assert result.final_position == {"x": 0, "y": 0}
        assert result.state == "completed"


class TestHappyPath:
    """Tests a robot walking and cleaning tiles on the map, never colliding."""

    def test_happy_path(
        self, sample_23_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = [
            Action(direction=Direction.SOUTH, steps=1),
            Action(direction=Direction.EAST, steps=2),
        ]

        map_store.load(sample_23_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is None
        assert result.state == "completed"
        assert len(result.cleaned_tiles) == 4
        assert result.cleaned_tiles == [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 1, "y": 1},
            {"x": 2, "y": 1},
        ]
        assert sample_23_map[0, 0].is_dirty is False
        assert sample_23_map[0, 1].is_dirty is False
        assert sample_23_map[1, 1].is_dirty is False
        assert sample_23_map[2, 1].is_dirty is False

    def test_repeated_actions(
        self, sample_23_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = [
            Action(direction=Direction.SOUTH, steps=1),
            Action(direction=Direction.NORTH, steps=1),
            Action(direction=Direction.SOUTH, steps=1),
            Action(direction=Direction.NORTH, steps=1),
            Action(direction=Direction.SOUTH, steps=1),
            Action(direction=Direction.NORTH, steps=1),
        ]

        map_store.load(sample_23_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is None
        assert result.state == "completed"
        assert len(result.cleaned_tiles) == 7
        assert result.cleaned_tiles == [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 0, "y": 0},
        ]
        assert sample_23_map[0, 0].is_dirty is False
        assert sample_23_map[0, 1].is_dirty is False


class TestCollision:
    def test_collision(self, sample_23_map, map_store, cleaning_service: CleaningService):
        """Tests a collision scenario where the robot encounters an obstacle."""
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = [
            Action(direction=Direction.EAST, steps=2),
            Action(direction=Direction.SOUTH, steps=1),
        ]

        map_store.load(sample_23_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is not None  # collision

        assert result.state == "error"
        assert result.error.code == "collision"
        assert result.final_position == {"x": 1, "y": 0}  # last known position, not target
        assert result.error.position == {"x": 2, "y": 0}  # desired position
        assert len(result.cleaned_tiles) == 2
        assert result.cleaned_tiles == [{"x": 0, "y": 0}, {"x": 1, "y": 0}]
        assert sample_23_map[0, 0].is_dirty is False
        assert sample_23_map[1, 0].is_dirty is False

    def test_out_of_bounds(self, sample_map: Map, map_store, cleaning_service: CleaningService):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = [
            Action(direction=Direction.NORTH, steps=1),  # assuming this goes out of bounds
        ]

        map_store.load(sample_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is not None  # out of bounds
        assert result.state == "error"
        assert result.error.code == "collision"
        assert result.final_position == {"x": 0, "y": 0}  # last known position, not target
        assert result.error.position == {"x": 0, "y": -1}  # desired position
        assert len(result.cleaned_tiles) == 1
        assert result.cleaned_tiles == [{"x": 0, "y": 0}]
        assert sample_map[0, 0].is_dirty is False


class TestRobotType:
    def test_basic_robot(
        self, sample_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.BASIC
        actions = [
            Action(direction=Direction.EAST, steps=2),
            Action(direction=Direction.WEST, steps=1),
            Action(direction=Direction.SOUTH, steps=1),
        ]
        map_store.load(sample_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is None
        assert result.state == "completed"

        assert result.submitted_actions == len(actions)
        assert len(result.cleaned_tiles) == 5
        assert result.cleaned_tiles == [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 2, "y": 0},
            {"x": 1, "y": 0},
            {"x": 1, "y": 1},
        ]
        assert result.successful_steps == sum(action.steps for action in actions)
        assert result.final_position == {"x": 1, "y": 1}

    def test_premium_robot(
        self, sample_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.PREMIUM
        actions = [
            Action(direction=Direction.EAST, steps=2),
            Action(direction=Direction.WEST, steps=1),
            Action(direction=Direction.SOUTH, steps=1),
        ]
        map_store.load(sample_map)

        result = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result is not None
        assert result.error is None
        assert result.state == "completed"

        assert result.submitted_actions == len(actions)
        assert len(result.cleaned_tiles) == 3
        assert result.cleaned_tiles == [
            {"x": 0, "y": 0},
            {"x": 2, "y": 0},
            {"x": 1, "y": 1},
        ]
        assert result.successful_steps == sum(action.steps for action in actions)
        assert result.final_position == {"x": 1, "y": 1}

    def test_premium_rerun_cleans_nothing(
        self, sample_map: Map, map_store: MapStore, cleaning_service: CleaningService
    ):
        start = Coordinate(0, 0)
        robot_model = RobotModel.PREMIUM
        actions = [
            Action(direction=Direction.EAST, steps=1),
        ]
        map_store.load(sample_map)

        # First run
        result_first = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result_first is not None
        assert result_first.error is None
        assert result_first.state == "completed"
        assert len(result_first.cleaned_tiles) == 1
        assert result_first.cleaned_tiles == [{"x": 0, "y": 0}]
        assert result_first.final_position == {"x": 1, "y": 0}

        # Second run without reloading the map
        result_second = cleaning_service.clean(
            start=start,
            robot_model=robot_model,
            actions=actions,
        )

        assert result_second is not None
        assert result_second.error is None
        assert result_second.state == "completed"
        assert len(result_second.cleaned_tiles) == 0
        assert result_second.cleaned_tiles == []
        assert result_second.final_position == {"x": 1, "y": 0}
