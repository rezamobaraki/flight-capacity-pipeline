import csv
import json
import logging
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from src.domains.aircraft import Aircraft
from src.domains.flight_event import FlightEvent
from src.core.exceptions import DataFileNotFoundError

logger = logging.getLogger(__name__)


class FileService:
    def read_csv(
        self, path: str | Path, delimiter: str = ";"
    ) -> Iterator[dict[str, str]]:
        path = Path(path)
        if not path.exists():
            raise DataFileNotFoundError(str(path))

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                if not reader.fieldnames:
                    raise DataFileNotFoundError(f"No header row found in {path}")

                for row in reader:
                    cleaned_row = {
                        k: v.strip() for k, v in row.items() if k and v is not None
                    }
                    if cleaned_row:
                        yield cleaned_row
        except UnicodeDecodeError as e:
            raise DataFileNotFoundError(
                f"Cannot decode {path}. Ensure it is UTF-8 encoded. Error: {e}"
            ) from e

    def read_ndjson(self, path: str | Path) -> Iterator[dict]:
        path = Path(path)
        if not path.exists():
            raise DataFileNotFoundError(str(path))

        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Skipped malformed JSON at line %d in %s: %s",
                        line_num,
                        path,
                        e,
                    )

    def list_files(
        self, directory: str | Path, pattern: str = "*.csv"
    ) -> list[Path]:
        directory = Path(directory)
        if not directory.exists():
            raise DataFileNotFoundError(str(directory))
        files = sorted(directory.glob(pattern))
        if not files:
            raise DataFileNotFoundError(f"No {pattern} files in {directory}")
        return files

    def load_aircraft(self, path: str | Path) -> list[Aircraft]:
        loaded = 0
        skipped = 0
        aircraft: list[Aircraft] = []
        for raw in self.read_ndjson(path):
            try:
                aircraft.append(Aircraft.model_validate(raw))
                loaded += 1
            except ValidationError as e:
                skipped += 1
                logger.warning("Skipped invalid aircraft record: %s", e)
        logger.info("Aircraft loading complete: %d loaded, %d skipped", loaded, skipped)
        return aircraft

    def stream_events(self, data_dir: str | Path) -> Iterator[FlightEvent]:
        csv_files = self.list_files(data_dir, "*.csv")
        for csv_file in csv_files:
            yield from self._stream_events_file(csv_file)

    def _stream_events_file(self, csv_file: Path) -> Iterator[FlightEvent]:
        loaded = 0
        skipped = 0
        for row in self.read_csv(csv_file):
            try:
                yield FlightEvent.model_validate(row)
                loaded += 1
            except ValidationError as e:
                skipped += 1
                logger.warning("Skipped invalid event in %s: %s", csv_file.name, e)
        logger.info("%s: %d events loaded, %d skipped", csv_file.name, loaded, skipped)
