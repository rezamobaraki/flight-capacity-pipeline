import logging
import threading

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.core.container import container
from src.core.exceptions import AppError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/commands", tags=["commands"])

_PIPELINE_LOCK = threading.Lock()

def _run_pipeline_background() -> None:
    if not _PIPELINE_LOCK.acquire(blocking=False):
        logger.warning("Pipeline is already running, skipping trigger.")
        return

    try:
        logger.info("Starting background pipeline execution...")
        container.pipeline.run()
        logger.info("Background pipeline execution finished.")
    except AppError as e:
        logger.error(f"Pipeline failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in background pipeline: {e}", exc_info=True)
    finally:
        _PIPELINE_LOCK.release()

@router.post("/ingest", status_code=202)
async def trigger_ingestion(background_tasks: BackgroundTasks):
    if not _PIPELINE_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Pipeline already running")

    _PIPELINE_LOCK.release()

    background_tasks.add_task(_run_pipeline_background)

    return {"status": "accepted", "message": "Ingestion pipeline triggered"}
