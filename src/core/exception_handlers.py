from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError
from src.schemas.responses import ErrorResponse


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for the application.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        content = ErrorResponse(detail=str(exc), error_type=type(exc).__name__)
        return JSONResponse(
            status_code=exc.status_code,
            content=content.model_dump(),
        )

