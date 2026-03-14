from functools import cache

from repositories.sqlite_repository import SQLiteRepository
from src.core.settings import Settings
from src.services.capacity_service import CapacityService
from src.services.file_service import FileService
from src.services.pipeline_service import PipelineService


class ContainerRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.repository = SQLiteRepository(self.settings.DATABASE_PATH)
        self.file_service = FileService()
        self.capacity_service = CapacityService()

        self.pipeline = PipelineService(
            file_service=self.file_service,
            capacity_service=self.capacity_service,
            repository=self.repository,
            aircraft_path=self.settings.AIRCRAFT_FILE,
            events_dir=self.settings.FLIGHT_EVENTS_DIR,
        )


container = ContainerRegistry()


@cache
def get_pipeline():
    return container.pipeline


@cache
def get_settings():
    return container.settings


@cache
def get_repository():
    return container.repository
