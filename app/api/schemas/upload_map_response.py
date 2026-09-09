from pydantic import BaseModel, Field


class UploadMapResponse(BaseModel):
    rows: int = Field(..., ge=0)
    cols: int = Field(..., ge=0)
    walkable_tiles: int = Field(..., ge=0)
