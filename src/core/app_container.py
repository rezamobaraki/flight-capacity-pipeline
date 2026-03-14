from typing import Optional

from src.core.settings import Settings
from src.repositories.sqlite_repository import SQLiteRepository
from src.services.capacity_service import CapacityService
from src.services.file_service import FileService
from src.services.flight_aggregator import FlightAggregatorService
from src.services.pipeline_service import PipelineService


class AppContainer:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()

        self.repository = SQLiteRepository(self.settings.DATABASE_PATH)

        self.file_service = FileService()
        self.aggregator = FlightAggregatorService()
        self.capacity_service = CapacityService()

        self.pipeline = PipelineService(
            file_service=self.file_service,
            aggregator=self.aggregator,
            capacity_service=self.capacity_service,
            repository=self.repository,
            aircraft_path=self.settings.AIRCRAFT_FILE,
            events_dir=self.settings.FLIGHT_EVENTS_DIR,
        )
