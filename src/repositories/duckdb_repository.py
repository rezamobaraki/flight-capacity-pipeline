import logging
from pathlib import Path
from typing import Iterable, Iterator

import duckdb

from src.core.exceptions import DatabaseNotInitializedError
from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity, CapacitySummary
from src.domains.flight import Flight
from src.domains.flight_event import FlightEvent
from src.repositories.queries import duckdb as queries
from src.repositories.interfaces import RepositoryProtocol

logger = logging.getLogger(__name__)

# Column name lists mirror the table definitions in duckdb_queries.py.
# Used to reconstruct domain models from positional result rows.
_CAPACITY_COLS = [
    "flight_id", "flight_number", "date", "origin_iata", "origin_icao",
    "destination_iata", "destination_icao", "equipment", "aircraft_name",
    "category", "volume_m3", "payload_kg", "operator",
]
_FLIGHT_COLS = [
    "flight_id", "flight_number", "date", "origin_iata", "origin_icao",
    "destination_iata", "destination_icao", "equipment", "operator", "registration",
]
_AIRCRAFT_COLS = [
    "code_icao", "code_iata", "full_name", "category",
    "average_speed_mph", "volume", "payload",
]


class DuckDBRepository(RepositoryProtocol):
    __slots__ = ("_database_path", "_conn")

    def __init__(self, database_path: Path):
        self._database_path = database_path
        self._conn: duckdb.DuckDBPyConnection | None = None

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            raise DatabaseNotInitializedError()
        return self._conn

    def initialize(self) -> None:
        if self._conn is not None:
            logger.debug("DuckDB already initialized")
            return
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._conn = duckdb.connect(str(self._database_path))
            self._conn.executescript(queries.CREATE_TABLES_SCRIPT)
            logger.info("DuckDB initialized at %s", self._database_path)
        except duckdb.Error as e:
            logger.error("Failed to initialize DuckDB: %s", e)
            raise

    def is_exists(self) -> bool:
        return self.connection.execute(queries.CHECK_IS_EXISTS).fetchone()[0] == 0

    def is_file_processed(self, filename: str) -> bool:
        return self.connection.execute(
            queries.CHECK_FILE_PROCESSED, [filename]
        ).fetchone() is not None

    def mark_file_processed(self, filename: str) -> None:
        self.connection.execute(queries.MARK_FILE_PROCESSED, [filename])

    def bulk_insert_aircraft(self, aircraft: Iterable[Aircraft]) -> int:
        rows = [
            (a.code_icao, a.code_iata, a.full_name, a.category,
             a.average_speed_mph, a.volume, a.payload)
            for a in aircraft
        ]
        return self._bulk_insert(queries.INSERT_AIRCRAFT, rows)

    def bulk_insert_events(self, events: Iterable[FlightEvent]) -> int:
        rows = [
            (e.flight_id, e.date, e.time, e.equipment, e.flight,
             e.origin_iata, e.origin_icao, e.destination_iata,
             e.destination_icao, e.operator, e.registration)
            for e in events
        ]
        return self._bulk_insert(queries.INSERT_EVENT, rows)

    def bulk_insert_flights(self, flights: Iterable[Flight]) -> int:
        rows = [
            (f.flight_id, f.flight_number, f.date, f.origin_iata,
             f.origin_icao, f.destination_iata, f.destination_icao,
             f.equipment, f.operator, f.registration)
            for f in flights
        ]
        return self._bulk_insert(queries.INSERT_FLIGHT, rows)

    def bulk_insert_capacity(self, capacities: Iterable[Capacity]) -> int:
        rows = [
            (c.flight_id, c.flight_number, c.date, c.origin_iata,
             c.origin_icao, c.destination_iata, c.destination_icao,
             c.equipment, c.aircraft_name, c.category,
             c.volume_m3, c.payload_kg, c.operator)
            for c in capacities
        ]
        return self._bulk_insert(queries.INSERT_CAPACITY, rows)

    def _bulk_insert(self, sql: str, rows: list[tuple]) -> int:
        if not rows:
            return 0
        self.connection.executemany(sql, rows)
        return len(rows)

    def aggregate_flights(self) -> int:
        self.connection.execute(queries.AGGREGATE_FLIGHTS)
        return self.connection.execute("SELECT changes()").fetchone()[0]

    def calculate_capacity(self) -> int:
        self.connection.execute(queries.CALCULATE_CAPACITY)
        return self.connection.execute("SELECT changes()").fetchone()[0]

    def stream_flights(self) -> Iterator[Flight]:
        for row in self.connection.execute(queries.SELECT_ALL_FLIGHTS).fetchall():
            yield Flight.model_validate(dict(zip(_FLIGHT_COLS, row)))

    def stream_capacities(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Iterator[Capacity]:
        sql = queries.SELECT_CAPACITY_BASE
        params: list = []
        i = 2  # $1 reserved for LIMIT, $2 for OFFSET — build filters first

        # We collect filters then inject LIMIT/OFFSET at position 1 and 2
        # by reversing: build filter clauses with $1..$n, then
        # append limit/offset as the last two params.
        filter_clauses: list[str] = []
        filter_params: list = []
        p = 1

        if origin:
            col = "origin_iata" if len(origin) == 3 else "origin_icao"
            filter_clauses.append(f"{col} = ${p}")
            filter_params.append(origin.upper())
            p += 1

        if destination:
            col = "destination_iata" if len(destination) == 3 else "destination_icao"
            filter_clauses.append(f"{col} = ${p}")
            filter_params.append(destination.upper())
            p += 1

        if date:
            filter_clauses.append(f"date = ${p}")
            filter_params.append(date)
            p += 1

        if filter_clauses:
            sql += " AND " + " AND ".join(filter_clauses)

        sql += f" ORDER BY date, origin_iata, destination_iata LIMIT ${p} OFFSET ${p+1}"
        filter_params.extend([limit, offset])

        for row in self.connection.execute(sql, filter_params).fetchall():
            yield Capacity.model_validate(dict(zip(_CAPACITY_COLS, row)))

    def stream_capacity_summary(
        self,
        origin: str,
        destination: str,
        date: str | None = None,
    ) -> Iterator[CapacitySummary]:
        origin = origin.upper()
        destination = destination.upper()
        origin_col = "origin_iata" if len(origin) == 3 else "origin_icao"
        dest_col = "destination_iata" if len(destination) == 3 else "destination_icao"

        sql = queries.SELECT_CAPACITY_SUMMARY_BASE
        sql += f" AND {origin_col} = $1 AND {dest_col} = $2"
        params: list = [origin, destination]

        if date:
            sql += " AND date = $3"
            params.append(date)

        sql += " GROUP BY date ORDER BY date"

        for row in self.connection.execute(sql, params).fetchall():
            yield CapacitySummary(
                date=row[0], origin_iata=row[1], destination_iata=row[2],
                total_flights=row[3], total_volume_m3=row[4], total_payload_kg=row[5],
            )

    def stream_aircraft(self) -> Iterator[Aircraft]:
        for row in self.connection.execute(queries.SELECT_ALL_AIRCRAFT).fetchall():
            yield Aircraft.model_validate(dict(zip(_AIRCRAFT_COLS, row)))

    def ingest_csv_direct(self, csv_path: Path) -> int:
        """
        DuckDB-only fast path: reads the CSV file in parallel at the engine
        level, bypassing FileService and Pydantic validation entirely.
        Use for trusted/pre-validated sources only.
        """
        before = self.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.connection.execute(queries.INGEST_CSV_DIRECT, [str(csv_path)])
        after = self.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        return after - before

    def export_capacity_csv(self, output_path: Path) -> None:
        """DuckDB-only fast path: writes directly to disk without Python iteration."""
        self.connection.execute(queries.EXPORT_CAPACITY_CSV, [str(output_path)])

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed")