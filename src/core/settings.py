from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR.parent / "data"
    
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    WAREHOUSE_DIR: Path = DATA_DIR / "warehouse"

    FLIGHT_EVENTS_DIR: Path = RAW_DIR / "flight_events"
    AIRCRAFT_FILE: Path = RAW_DIR / "airplane_details.json"
    DATABASE_PATH: Path = WAREHOUSE_DIR / "flight_capacity.db"
    CAPACITY_OUTPUT_FILE: Path = WAREHOUSE_DIR / "capacity_table.csv"

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
