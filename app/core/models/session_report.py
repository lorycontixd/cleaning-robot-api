from dataclasses import dataclass

from app.core.models.coordinate import CoordinateDict
from app.core.models.robot import RobotModel


@dataclass
class Error:
    code: str
    message: str
    position: CoordinateDict


@dataclass
class SessionReport:
    id: str
    started_at: str
    finished_at: str
    state: str
    robot_model: RobotModel
    submitted_actions: int
    successful_steps: int
    cleaned_tiles: list[CoordinateDict]
    final_position: CoordinateDict
    duration_ms: int
    error: Error | None = None
