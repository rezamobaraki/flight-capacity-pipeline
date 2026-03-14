import argparse
import logging

from src.handlers.cli.ingest import run_ingestion

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flight Capacity Data Pipeline CLI")
    parser.add_argument("command", choices=["ingest"], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        run_ingestion()
