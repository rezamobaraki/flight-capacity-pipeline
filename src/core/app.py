import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.app_container import AppContainer
from src.errors.app import AppError
from src.handlers.capacity import CapacityHandler
from src.handlers.health import HealthHandler
from src.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
	container = AppContainer()
	health_handler = HealthHandler()
	capacity_handler = CapacityHandler(container.repository)

	@asynccontextmanager
	async def lifespan(app: FastAPI):
		container.repository.initialize()
		if container.repository.is_empty():
			logger.info("Database is empty, running data pipeline")
			container.pipeline.run()
		logger.info("Application started")
		yield
		container.repository.close()
		logger.info("Application shutdown")

	app = FastAPI(
		title="Rotate Cargo Capacity API",
		version="0.1.0",
		lifespan=lifespan,
	)

	@app.exception_handler(AppError)
	async def handle_app_error(request: Request, exc: AppError):
		content = ErrorResponse(detail=str(exc), error_type=type(exc).__name__)
		return JSONResponse(
			status_code=exc.status_code,
			content=content.model_dump(),
		)

	app.include_router(health_handler.router)
	app.include_router(capacity_handler.router)

	return app
