from dataclasses import dataclass

from app.core.map import Coordinate
from app.core.models.robot import RobotModel


@dataclass
class Error:
    code: str
    message: str
    position: Coordinate


@dataclass
class SessionReport:
    id: str
    started_at: str
    finished_at: str
    state: str
    robot_model: RobotModel
    submitted_actions: int
    successful_steps: int
    cleaned_tiles: list[dict[str, int]]
    final_position: dict[str, int]
    duration_ms: int
    error: Error | None = None
