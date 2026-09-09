import uuid
from datetime import UTC, datetime

from app.core.exceptions import InvalidStartPositionError, MapNotLoadedError
from app.core.map import Map
from app.core.models.action import Action
from app.core.models.coordinate import Coordinate
from app.core.models.robot import RobotModel
from app.core.models.session_report import Error, SessionReport
from app.storage.map_store import MapStore
from app.storage.session_history import SessionHistory


class CleaningService:
    """Service for orchestrating the cleaning process of the robot.
    Long-running service that persists through the lifetime of the process.
    """

    def __init__(self, map_store: MapStore, history: SessionHistory):
        self._map_store = map_store
        self._history = history

    @property
    def history(self) -> SessionHistory:
        return self._history

    def clean(
        self,
        start: Coordinate,
        robot_model: RobotModel,
        actions: list[Action],
    ) -> SessionReport:
        map: Map | None = self._map_store.current()
        if not map:
            raise MapNotLoadedError("No map is currently loaded. Call PUT /map first.")
        if not map.is_valid(start):
            raise InvalidStartPositionError(f"Invalid start position: {start}")
        report = self._run(map=map, robot=robot_model, start=start, actions=actions)
        self._history.record(report)
        return report

    def _run(
        self,
        map: Map,
        robot: RobotModel,
        start: Coordinate,
        actions: list[Action],
    ) -> SessionReport:
        id = uuid.uuid4()
        start_ts = datetime.now(UTC)

        current = start
        total_steps: int = 0
        cleaned_tiles: list[Coordinate] = []
        state: str = "completed"
        error_reason: str = ""
        error_position: Coordinate = start
        self._clean_tile(
            map, robot, start, cleaned_tiles
        )  # clean initial tile, check is done in method

        for action in actions:
            dx, dy = action.direction.get_unit_delta()

            for _ in range(action.steps):
                target = current.moved(dx, dy, steps=1)

                if not (map.in_bounds(target)):
                    # Collision - out of bounds
                    state = "error"
                    error_reason = "out_of_bounds"
                    error_position = target
                    break
                if not map.is_walkable(target):
                    # Collision - not walkable
                    state = "error"
                    error_reason = "obstacle"
                    error_position = target
                    break
                current = target
                total_steps += 1

                # Check if the robot should clean the current tile
                self._clean_tile(map, robot, current, cleaned_tiles)

            if state == "error":
                break

        end_ts = datetime.now(UTC)
        return SessionReport(
            id=str(id),
            started_at=start_ts.isoformat().replace("+00:00", "Z"),
            finished_at=end_ts.isoformat().replace("+00:00", "Z"),
            state=state,
            robot_model=robot,
            submitted_actions=len(actions),
            successful_steps=total_steps,
            cleaned_tiles=[{"x": coord.x, "y": coord.y} for coord in cleaned_tiles],
            final_position=current.to_dict(),
            duration_ms=int((end_ts - start_ts).total_seconds() * 1000),
            error=Error(
                code="collision",
                message=self._build_error_message(error_reason),
                position=error_position,
            )
            if state == "error"
            else None,
        )

    def _clean_tile(
        self, map: Map, robot: RobotModel, current: Coordinate, cleaned_tiles: list[Coordinate]
    ):
        if robot.should_clean(dirty=map.is_dirty(current)):
            map.clean(current)
            cleaned_tiles.append(current)  # no guard - basic robot operates on clean tiles too

    def _build_error_message(self, error_reason: str) -> str:
        if error_reason == "out_of_bounds":
            return "Collision with the boundary of the map"
        if error_reason == "obstacle":
            return "Collision with an obstacle"
        return "Unknown error"
