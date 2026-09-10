from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from app.api.dependencies import get_map_store
from app.api.schemas.upload_map_response import UploadMapResponse
from app.core.map import Map
from app.maps.map_loader import load_map
from app.storage.map_store import MapStore

router = APIRouter(prefix="/map")


@router.put(
    "",
    response_model=UploadMapResponse,
    responses={415: {"description": "The filename extension is not .txt or .json."}},
)
def get_maps(
    file: UploadFile = File(...),  # noqa: B008
    map_store: MapStore = Depends(get_map_store),  # noqa: B008
):
    if not file.filename:
        return JSONResponse(content={"detail": "No file uploaded"}, status_code=422)

    contents: bytes = file.file.read()
    # don't check empty content -> done in load_map and raise exception
    # Don't handle load_map in try/except because exceptions are caught by FastAPI automatically
    map_data: Map = load_map(file.filename, contents)
    map_store.load(map_data)

    return UploadMapResponse(
        rows=map_data.rows,
        cols=map_data.cols,
        walkable_tiles=map_data.walkable_tiles,
    )
