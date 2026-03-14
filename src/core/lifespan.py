import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.container import container
from src.core.exceptions import DataFileNotFoundError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application lifespan events (startup and shutdown).
    """
    logger.info("Initializing application resources...")
    container.repository.initialize()

    if container.repository.is_empty():
        logger.info("Database is empty. Starting initial data pipeline...")
        try:
            container.pipeline.run()
            logger.info("Data pipeline completed.")
        except DataFileNotFoundError as e:
            logger.error(f"Failed to run initial data pipeline: {e}. Starting with empty database.")
        except Exception as e:
            logger.error(f"Unexpected error running data pipeline: {e}", exc_info=True)
    else:
        logger.info("Database is already initialized.")

    yield

    logger.info("Shutting down application resources...")
