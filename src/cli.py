import argparse
import logging
from src.core.container import container
from src.core.exceptions import AppError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def ingest_data() -> None:
    logger.info("Starting ingestion command...")
    container.repository.initialize()
    try:
        container.pipeline.run()
        logger.info("Ingestion complete.")
    except AppError as e:
        logger.error(f"Pipeline failed: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flight Capacity Data Pipeline CLI")
    parser.add_argument("command", choices=["ingest"], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_data()
