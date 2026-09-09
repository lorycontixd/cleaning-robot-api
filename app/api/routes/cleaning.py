from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_cleaning_service
from app.api.schemas.clean_request import CleanRequest
from app.core.map import Coordinate
from app.core.models.session_report import SessionReport
from app.services.cleaning_service import CleaningService

router = APIRouter(prefix="/clean")


# don't use Response object, it skips response_model
@router.post("", response_model=SessionReport)
def clean(
    request: CleanRequest,
    response: Response,
    service: CleaningService = Depends(get_cleaning_service),  # noqa: B008
):
    start = Coordinate(x=request.start.x, y=request.start.y)

    report = service.clean(
        start=start,
        robot_model=request.robot_model,
        actions=request.actions,
    )
    if report.error:
        response.status_code = status.HTTP_409_CONFLICT
    return report
