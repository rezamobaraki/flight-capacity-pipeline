import logging
import sqlite3
from pathlib import Path

from src.core.exceptions import DatabaseNotInitializedError
from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight
from src.repositories import queries
from src.repositories.interfaces import AbstractRepository

logger = logging.getLogger(__name__)


class SQLiteRepository(AbstractRepository):
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

    def bulk_create_aircraft(self, aircraft_list: list[Aircraft]) -> int:
        if not aircraft_list:
            return 0

        parameters = [
            (
                aircraft.code_icao,
                aircraft.code_iata,
                aircraft.full_name,
                aircraft.category,
                aircraft.average_speed_mph,
                aircraft.volume,
                aircraft.payload,
            )
            for aircraft in aircraft_list
        ]

        return self._bulk_create(sql=queries.INSERT_AIRCRAFT, parameters=parameters, record_type="aircraft")

    def bulk_create_flights(self, flights: list[Flight]) -> int:
        if not flights:
            return 0

        parameters = [
            (
                flight.flight_id,
                flight.flight_number,
                flight.date,
                flight.origin_iata,
                flight.origin_icao,
                flight.destination_iata,
                flight.destination_icao,
                flight.equipment,
                flight.operator,
                flight.registration,
            )
            for flight in flights
        ]

        return self._bulk_create(sql=queries.INSERT_FLIGHT, parameters=parameters, record_type="flights")

    def bulk_create_capacity(self, capacities: list[Capacity]) -> int:
        if not capacities:
            return 0

        parameters = [
            (
                capacity.flight_id,
                capacity.flight_number,
                capacity.date,
                capacity.origin_iata,
                capacity.origin_icao,
                capacity.destination_iata,
                capacity.destination_icao,
                capacity.equipment,
                capacity.aircraft_name,
                capacity.category,
                capacity.volume_m3,
                capacity.payload_kg,
                capacity.operator,
            )
            for capacity in capacities
        ]

        return self._bulk_create(sql=queries.INSERT_CAPACITY, parameters=parameters, record_type="capacity")

    def _bulk_create(self, sql: str, parameters: list[tuple], record_type: str) -> int:
        try:
            with self.connection:
                self.connection.executemany(sql, parameters)

            record_count = len(parameters)
            logger.info("Successfully saved %d %s records", record_count, record_type)
            return record_count

        except sqlite3.Error as error:
            logger.error(f"Failed to save {record_type} batch: {error}")
            raise

    def get_capacity(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: str | None = None,
    ) -> list[Capacity]:
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
        return [Capacity.model_validate(row) for row in cursor.fetchall()]

    def get_aircraft_map(self) -> dict[str, Aircraft]:
        cursor = self.connection.execute(queries.SELECT_ALL_AIRCRAFT)
        return {
            row["code_icao"]: Aircraft.model_validate(row)
            for row in cursor.fetchall()
        }

    def close(self) -> None:
        if self._active_connection:
            self._active_connection.close()
            self._active_connection = None
            logger.info("Database connection closed")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
