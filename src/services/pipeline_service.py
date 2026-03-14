import logging
from pathlib import Path

from src.repositories.interfaces import AbstractRepository
from src.services.capacity_service import CapacityService
from src.services.file_service import FileService
from src.services.flight_aggregator import FlightAggregatorService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(
        self,
        file_service: FileService,
        aggregator: FlightAggregatorService,
        capacity_service: CapacityService,
        repository: AbstractRepository,
        aircraft_path: Path,
        events_dir: Path,
    ):
        self._file_service = file_service
        self._aggregator = aggregator
        self._capacity_service = capacity_service
        self._repository = repository
        self._aircraft_path = aircraft_path
        self._events_dir = events_dir

    def run(self) -> None:
        logger.info("Starting data pipeline")

        aircraft_list = self._file_service.load_aircraft(self._aircraft_path)
        self._repository.bulk_create_aircraft(aircraft_list)
        aircraft_map = {a.code_icao: a for a in aircraft_list}

        events = self._file_service.stream_events(self._events_dir)
        flights = self._aggregator.aggregate(events)
        self._repository.bulk_create_flights(flights)

        capacities = self._capacity_service.calculate(flights, aircraft_map)
        self._repository.bulk_create_capacity(capacities)

        logger.info("Pipeline complete")
