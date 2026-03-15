import logging
import sqlite3
from pathlib import Path
from typing import Iterable, Iterator

from src.core.exceptions import DatabaseNotInitializedError
from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity, CapacitySummary
from src.domains.flight import Flight
from src.domains.flight_event import FlightEvent
from src.repositories import queries
from src.repositories.interfaces import RepositoryProtocol

logger = logging.getLogger(__name__)


class SQLiteRepository(RepositoryProtocol):
    __slots__ = ("_database_path", "_active_connection")

    def __init__(self, database_path: Path):
        self._database_path = database_path
        self._active_connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._active_connection is None:
            raise DatabaseNotInitializedError()
        return self._active_connection

    def initialize(self) -> None:
        if self._active_connection is not None:
            logger.debug("Database already initialized")
            return

        self._database_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._active_connection = sqlite3.connect(str(self._database_path), check_same_thread=False)
            self._active_connection.row_factory = sqlite3.Row

            self._create_schema()
            logger.info("Database initialized successfully at %s", self._database_path)

        except sqlite3.Error as error:
            logger.error(f"Failed to initialize database: {error}")
            raise

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.executescript(queries.CREATE_TABLES_SCRIPT)

    def is_exists(self) -> bool:
        cursor = self.connection.execute(queries.CHECK_IS_EXISTS)
        count = cursor.fetchone()[0]
        return count == 0

    def bulk_insert_aircraft(self, aircraft: Iterable[Aircraft]) -> int:
        return self._bulk_insert(aircraft, queries.INSERT_AIRCRAFT)

    def bulk_insert_flights(self, flights: Iterable[Flight]) -> int:
        return self._bulk_insert(flights, queries.INSERT_FLIGHT)

    def bulk_insert_capacity(self, capacities: Iterable[Capacity]) -> int:
        return self._bulk_insert(capacities, queries.INSERT_CAPACITY)

    def bulk_insert_events(self, events: Iterable[FlightEvent]) -> int:
        return self._bulk_insert(events, queries.INSERT_EVENT)

    def _bulk_insert(self, data: Iterable, sql: str) -> int:
        count = 0
        with self.connection as conn:
            for chunk in self._chunk_stream(data):
                conn.executemany(
                    sql,
                    [x.model_dump() for x in chunk],
                )
                count += len(chunk)
        return count

    def aggregate_flights(self) -> int:
        with self.connection as conn:
            cursor = conn.execute(queries.AGGREGATE_FLIGHTS)
            return cursor.rowcount

    def calculate_capacity(self) -> int:
        with self.connection as conn:
            cursor = conn.execute(queries.CALCULATE_CAPACITY)
            return cursor.rowcount

    def stream_flights(self) -> Iterator[Flight]:
        with self.connection as conn:
            cursor = conn.execute("SELECT * FROM flights")
            for row in cursor:
                yield Flight.model_validate(dict(row))

    def stream_capacities(
        self, origin: str | None = None, destination: str | None = None, date: str | None = None
    ) -> Iterator[Capacity]:
        query = queries.SELECT_CAPACITY_BASE
        parameters: dict[str, str] = {}

        if origin:
            query += " AND origin_iata = :origin"
            parameters["origin"] = origin.upper()
        if destination:
            query += " AND destination_iata = :destination"
            parameters["destination"] = destination.upper()
        if date:
            query += " AND date = :date"
            parameters["date"] = date

        query += " ORDER BY date, origin_iata, destination_iata"

        cursor = self.connection.execute(query, parameters)
        for row in cursor:
            yield Capacity.model_validate(dict(row))

    def stream_capacity_summary(
        self,
        origin: str,
        destination: str,
        date: str | None = None
    ) -> Iterator[CapacitySummary]:
        query = queries.SELECT_CAPACITY_SUMMARY
        parameters = {"origin": origin, "destination": destination}

        if date:
            query += " AND date = :date"
            parameters["date"] = date

        query += " GROUP BY date ORDER BY date"

        cursor = self.connection.execute(query, parameters)
        for row in cursor:
            yield CapacitySummary(
                origin_iata=origin,
                destination_iata=destination,
                **dict(row)
            )

    def stream_aircraft(self) -> Iterator[Aircraft]:
        cursor = self.connection.execute(queries.SELECT_ALL_AIRCRAFT)
        for row in cursor:
            yield Aircraft.model_validate(dict(row))

    def close(self) -> None:
        if self._active_connection:
            self._active_connection.close()
            self._active_connection = None
            logger.info("Database connection closed")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


    @staticmethod
    def _chunk_stream(iterator: Iterable, size: int = 1000) -> Iterator[list]:
        buffer = []
        for item in iterator:
            buffer.append(item)
            if len(buffer) >= size:
                yield buffer
                buffer = []
        if buffer:
            yield buffer
