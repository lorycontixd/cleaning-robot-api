from pydantic import BaseModel

from app.core.models.action import Action
from app.core.models.robot import RobotModel


# Defined to keep Coordinate layer-agnostic
class StartPosition(BaseModel):
    x: int
    y: int


class CleanRequest(BaseModel):
    start: StartPosition
    robot_model: RobotModel
    actions: list[Action]
