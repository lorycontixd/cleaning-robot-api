from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.exception_maps import _EXCEPTION_MAPPING
from app.api.routes import cleaning, health, history, maps
from app.core.exceptions import DomainError

app = FastAPI(title="Cleaning Robot API")


@app.exception_handler(DomainError)
def handle_domain_exception(request: Request, exc: DomainError):
    exc_type = type(exc)
    status_code = _EXCEPTION_MAPPING.get(exc_type, 500)
    return JSONResponse(content={"detail": str(exc)}, status_code=status_code)


app.include_router(health.router)
app.include_router(cleaning.router)
app.include_router(history.router)
app.include_router(maps.router)
