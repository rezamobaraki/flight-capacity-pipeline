from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    FLIGHT_EVENTS_DIR: Path = DATA_DIR / "flight_events"
    AIRCRAFT_FILE: Path = DATA_DIR / "airplane_details_original.json"
    DATABASE_PATH: Path = DATA_DIR / "rotate.db"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
