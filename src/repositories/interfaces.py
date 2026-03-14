from abc import ABC, abstractmethod
from typing import Protocol

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight


class RepositoryProtocol(Protocol):
    def initialize(self) -> None: ...

    def is_empty(self) -> bool: ...

    def save_aircraft_batch(self, aircraft: list[Aircraft]) -> int: ...

    def save_flights_batch(self, flights: list[Flight]) -> int: ...

    def save_capacity_batch(self, capacities: list[Capacity]) -> int: ...

    def get_capacity(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: str | None = None,
    ) -> list[Capacity]: ...

    def get_aircraft_map(self) -> dict[str, Aircraft]: ...

    def close(self) -> None: ...


AbstractRepository = RepositoryProtocol
