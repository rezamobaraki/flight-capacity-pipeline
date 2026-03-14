import logging
from pathlib import Path

from src.repositories.interfaces import AbstractRepository
from src.services.file_service import FileService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(
        self,
        file_service: FileService,
        repository: AbstractRepository,
        aircraft_path: Path,
        events_dir: Path,
    ):
        self._file_service = file_service
        self._repository = repository
        self._aircraft_path = aircraft_path
        self._events_dir = events_dir

    def run(self) -> None:
        logger.info("Starting data pipeline")

        aircraft_list = self._file_service.load_aircraft(self._aircraft_path)
        self._repository.bulk_insert_aircraft(aircraft_list)
        logger.info("Loaded %d aircraft", len(aircraft_list))

        events = self._file_service.stream_events(self._events_dir)
        count = self._repository.bulk_insert_events(events)
        logger.info("Inserted %d raw flight events", count)

        aggregated_count = self._repository.aggregate_flights()
        logger.info("Aggregated %d flights via SQL", aggregated_count)

        capacity_count = self._repository.calculate_capacity()
        logger.info("Calculated capacity for %d flights via SQL", capacity_count)

        logger.info("Pipeline complete")
