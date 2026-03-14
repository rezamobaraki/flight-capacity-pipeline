import logging

import uvicorn
from fastapi import FastAPI

from src.core.container import container
from src.core.exception_handlers import setup_exception_handlers
from src.handlers import capacity, commands, health


def create_app() -> FastAPI:
    logging.basicConfig(level=container.settings.LOG_LEVEL, format=container.settings.LOG_FORMAT)

    app = FastAPI(title="Rotate Cargo Capacity API", version="0.1.0")
    app.include_router(health.router)
    app.include_router(capacity.router)
    app.include_router(commands.router)

    setup_exception_handlers(app)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
