from functools import cache
from typing import Iterator

from src.repositories.interfaces import RepositoryProtocol
from src.repositories.sqlite_repository import SQLiteRepository
from src.core.settings import Settings
from src.services.file_service import FileService
from src.services.pipeline_service import PipelineService


class ContainerRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.repository = SQLiteRepository(self.settings.DATABASE_PATH)
        self.file_service = FileService()

        self.pipeline = PipelineService(
            file_service=self.file_service,
            repository=self.repository,
            aircraft_path=self.settings.AIRCRAFT_FILE,
            events_dir=self.settings.FLIGHT_EVENTS_DIR,
            processed_dir=self.settings.PROCESSED_DIR,
            capacity_output_path=self.settings.CAPACITY_OUTPUT_FILE,
        )


container = ContainerRegistry()


@cache
def get_pipeline():
    return container.pipeline


@cache
def get_settings():
    return container.settings


def get_repository() -> Iterator[RepositoryProtocol]:
    repository = SQLiteRepository(container.settings.DATABASE_PATH)
    repository.initialize()

    try:
        yield repository
    finally:
        repository.close()
