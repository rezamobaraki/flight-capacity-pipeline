from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Protocol

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity, CapacitySummary
from src.domains.flight import Flight
from src.domains.flight_event import FlightEvent


class RepositoryProtocol(Protocol):
    def initialize(self) -> None: ...

    def is_exists(self) -> bool: ...

    def bulk_insert_aircraft(self, aircraft: Iterable[Aircraft]) -> int: ...

    def bulk_insert_flights(self, flights: Iterable[Flight]) -> int: ...

    def bulk_insert_capacity(self, capacities: Iterable[Capacity]) -> int: ...

    def bulk_insert_events(self, events: Iterable[FlightEvent]) -> int: ...

    def aggregate_flights(self) -> int: ...

    def get_all_flights(self) -> Iterator[Flight]: ...

    def get_all_capacities(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: str | None = None,
    ) -> Iterator[Capacity]: ...

    def get_capacity_summary(
        self,
        origin: str,
        destination: str,
        date: str | None = None
    ) -> Iterator[CapacitySummary]: ...

    def get_aircraft_map(self) -> dict[str, Aircraft]: ...

    def close(self) -> None: ...


AbstractRepository = RepositoryProtocol
