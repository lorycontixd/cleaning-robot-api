from pydantic import BaseModel, Field

from app.core.models.direction import Direction


class Action(BaseModel):
    direction: Direction
    steps: int = Field(..., ge=1)
