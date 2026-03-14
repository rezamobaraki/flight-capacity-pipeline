import logging
from pathlib import Path

from src.repositories.interfaces import AbstractRepository
from src.services.capacity_service import CapacityService
from src.services.file_service import FileService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(
        self,
        file_service: FileService,
        capacity_service: CapacityService,
        repository: AbstractRepository,
        aircraft_path: Path,
        events_dir: Path,
    ):
        self._file_service = file_service
        self._capacity_service = capacity_service
        self._repository = repository
        self._aircraft_path = aircraft_path
        self._events_dir = events_dir

    def run(self) -> None:
        logger.info("Starting data pipeline")


        aircraft_list = self._file_service.load_aircraft(self._aircraft_path)
        self._repository.bulk_insert_aircraft(aircraft_list)
        aircraft_map = {aircraft.code_icao: aircraft for aircraft in aircraft_list}
        logger.info("Loaded %d aircraft", len(aircraft_list))

        events = self._file_service.stream_events(self._events_dir)
        count = self._repository.bulk_insert_events(events)
        logger.info("Inserted %d raw flight events", count)

        aggregated_count = self._repository.aggregate_flights()
        logger.info("Aggregated %d flights via SQL", aggregated_count)

        # 4. Calculate Capacity
        flights_iter = self._repository.get_all_flights()
        capacities = self._capacity_service.calculate(flights_iter, aircraft_map)
        self._repository.bulk_insert_capacity(capacities)

        logger.info("Pipeline complete")
