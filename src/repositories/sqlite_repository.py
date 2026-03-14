import logging
import sqlite3
from pathlib import Path
from typing import Optional

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight
from src.errors.database import DatabaseNotInitializedError
from src.repositories.interfaces import AbstractRepository

logger = logging.getLogger(__name__)



class SQLiteRepository(AbstractRepository):
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def _conn(self) -> sqlite3.Connection:
        if self._connection is None:
            raise DatabaseNotInitializedError()
        return self._connection

    def initialize(self) -> None:
        if self._connection is not None:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self._db_path))
        self._connection.row_factory = sqlite3.Row
        self._create_tables()
        logger.info("Database initialized at %s", self._db_path)

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS aircraft (
                code_icao TEXT PRIMARY KEY,
                code_iata TEXT NOT NULL,
                full_name TEXT NOT NULL,
                category TEXT NOT NULL,
                average_speed_mph REAL NOT NULL,
                volume REAL NOT NULL,
                payload REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS flights (
                flight_id TEXT PRIMARY KEY,
                flight_number TEXT,
                date TEXT NOT NULL,
                origin_iata TEXT,
                origin_icao TEXT,
                destination_iata TEXT,
                destination_icao TEXT,
                equipment TEXT,
                operator TEXT,
                registration TEXT
            );

            CREATE TABLE IF NOT EXISTS capacity (
                flight_id TEXT PRIMARY KEY,
                flight_number TEXT,
                date TEXT NOT NULL,
                origin_iata TEXT,
                origin_icao TEXT,
                destination_iata TEXT,
                destination_icao TEXT,
                equipment TEXT,
                aircraft_name TEXT,
                category TEXT,
                volume_m3 REAL,
                payload_kg REAL,
                operator TEXT,
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
                FOREIGN KEY (equipment) REFERENCES aircraft(code_icao)
            );

            CREATE INDEX IF NOT EXISTS idx_capacity_route
                ON capacity(origin_iata, destination_iata);
            CREATE INDEX IF NOT EXISTS idx_capacity_date
                ON capacity(date);
        """)
        self._conn.commit()

    def is_empty(self) -> bool:
        cursor = self._conn.execute("SELECT COUNT(*) FROM capacity")
        return cursor.fetchone()[0] == 0

    def save_aircraft_batch(self, aircraft: list[Aircraft]) -> int:
        data = [
            (
                a.code_icao,
                a.code_iata,
                a.full_name,
                a.category,
                a.average_speed_mph,
                a.volume,
                a.payload,
            )
            for a in aircraft
        ]
        self._conn.executemany(
            "INSERT OR REPLACE INTO aircraft VALUES (?, ?, ?, ?, ?, ?, ?)", data
        )
        self._conn.commit()
        logger.info("Saved %d aircraft records", len(data))
        return len(data)

    def save_flights_batch(self, flights: list[Flight]) -> int:
        data = [
            (
                f.flight_id,
                f.flight_number,
                f.date,
                f.origin_iata,
                f.origin_icao,
                f.destination_iata,
                f.destination_icao,
                f.equipment,
                f.operator,
                f.registration,
            )
            for f in flights
        ]
        self._conn.executemany(
            "INSERT OR REPLACE INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            data,
        )
        self._conn.commit()
        logger.info("Saved %d flight records", len(data))
        return len(data)

    def save_capacity_batch(self, capacities: list[Capacity]) -> int:
        data = [
            (
                c.flight_id,
                c.flight_number,
                c.date,
                c.origin_iata,
                c.origin_icao,
                c.destination_iata,
                c.destination_icao,
                c.equipment,
                c.aircraft_name,
                c.category,
                c.volume_m3,
                c.payload_kg,
                c.operator,
            )
            for c in capacities
        ]
        self._conn.executemany(
            "INSERT OR REPLACE INTO capacity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            data,
        )
        self._conn.commit()
        logger.info("Saved %d capacity records", len(data))
        return len(data)

    def get_capacity(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
    ) -> list[Capacity]:
        query = "SELECT * FROM capacity WHERE 1=1"
        params: list[str] = []

        if origin:
            query += " AND origin_iata = ?"
            params.append(origin.upper())
        if destination:
            query += " AND destination_iata = ?"
            params.append(destination.upper())
        if date:
            query += " AND date = ?"
            params.append(date)

        query += " ORDER BY date, origin_iata, destination_iata"
        cursor = self._conn.execute(query, params)
        return [self._row_to_capacity(row) for row in cursor.fetchall()]

    def get_aircraft_map(self) -> dict[str, Aircraft]:
        cursor = self._conn.execute("SELECT * FROM aircraft")
        return {
            row["code_icao"]: Aircraft(
                code_icao=row["code_icao"],
                code_iata=row["code_iata"],
                full_name=row["full_name"],
                category=row["category"],
                average_speed_mph=row["average_speed_mph"],
                volume=row["volume"],
                payload=row["payload"],
            )
            for row in cursor.fetchall()
        }

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    @staticmethod
    def _row_to_capacity(row: sqlite3.Row) -> Capacity:
        return Capacity(
            flight_id=row["flight_id"],
            flight_number=row["flight_number"] or "",
            date=row["date"],
            origin_iata=row["origin_iata"] or "",
            origin_icao=row["origin_icao"] or "",
            destination_iata=row["destination_iata"] or "",
            destination_icao=row["destination_icao"] or "",
            equipment=row["equipment"] or "",
            aircraft_name=row["aircraft_name"] or "",
            category=row["category"] or "",
            volume_m3=row["volume_m3"] or 0.0,
            payload_kg=row["payload_kg"] or 0.0,
            operator=row["operator"] or "",
        )
