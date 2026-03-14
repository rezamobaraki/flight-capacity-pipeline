import logging
from pathlib import Path

from src.domains.capacity import Capacity
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
        processed_dir: Path,
        capacity_output_path: Path,
    ):
        self._file_service = file_service
        self._repository = repository
        self._aircraft_path = aircraft_path
        self._events_dir = events_dir
        self._processed_dir = processed_dir
        self._capacity_output_path = capacity_output_path

    def run(self) -> None:
        logger.info("Starting data pipeline")

        aircraft_list = self._file_service.load_aircraft(self._aircraft_path)
        self._repository.bulk_insert_aircraft(aircraft_list)
        logger.info("Loaded %d aircraft", len(aircraft_list))
        
        self._file_service.copy_to_processed(self._aircraft_path, self._processed_dir)

        events_files = self._file_service.list_files(self._events_dir, "*.csv")
        total_events = 0

        for file_path in events_files:
            logger.info("Processing flight events file: %s", file_path.name)
            events = self._file_service.stream_events_from_file(file_path)
            count = self._repository.bulk_insert_events(events)
            total_events += count

            self._file_service.copy_to_processed(file_path, self._processed_dir)

        logger.info("Inserted %d total raw flight events", total_events)

        aggregated_count = self._repository.aggregate_flights()
        logger.info("Aggregated %d flights via SQL", aggregated_count)

        capacity_count = self._repository.calculate_capacity()
        logger.info("Calculated capacity for %d flights via SQL", capacity_count)

        self._export_capacity_to_csv()

        logger.info("Pipeline complete")

    def _export_capacity_to_csv(self) -> None:
        logger.info("Exporting capacity table to %s", self._capacity_output_path)
        capacities = self._repository.stream_capacities()
        data_iter = (c.model_dump() for c in capacities)
        
        fieldnames = list(Capacity.model_fields.keys())
        self._file_service.write_csv(
            path=self._capacity_output_path,
            rows=data_iter,
            fieldnames=fieldnames,
        )
