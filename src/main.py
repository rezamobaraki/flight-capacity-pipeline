import logging

from src.core.settings import Settings
from src.core.app_container import AppContainer


def main() -> None:
    settings = Settings()
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    logger = logging.getLogger(__name__)

    logger.info("Starting data pipeline")
    container = AppContainer(settings)
    container.repository.initialize()
    container.pipeline.run()
    container.repository.close()
    logger.info("Data pipeline completed")


if __name__ == "__main__":
    main()
