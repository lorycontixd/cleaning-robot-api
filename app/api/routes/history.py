import csv
from io import StringIO

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import get_session_history
from app.storage.session_history import SessionHistory

router = APIRouter(prefix="/history")

_CSV_HEADERS = [
    "id",
    "started_at",
    "state",
    "robot_model",
    "submitted_actions",
    "successful_steps",
    "cleaned_tiles",
    "duration_ms",
]


@router.get("")
def get_history(
    history: SessionHistory = Depends(get_session_history),  # noqa: B008
):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(_CSV_HEADERS)

    for report in history.get_history():
        writer.writerow(
            [
                report.id,
                report.started_at,
                report.state,
                report.robot_model.value,
                report.submitted_actions,
                report.successful_steps,
                len(report.cleaned_tiles),
                report.duration_ms,
            ]
        )

    return Response(content=output.getvalue(), media_type="text/csv")
