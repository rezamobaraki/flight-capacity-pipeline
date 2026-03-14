from abc import ABC, abstractmethod
from typing import Protocol

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight


class RepositoryProtocol(Protocol):
    def initialize(self) -> None: ...

    def is_exists(self) -> bool: ...

    def bulk_create_aircraft(self, aircraft: list[Aircraft]) -> int: ...

    def bulk_create_flights(self, flights: list[Flight]) -> int: ...

    def bulk_create_capacity(self, capacities: list[Capacity]) -> int: ...

    def get_capacity_list(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: str | None = None,
    ) -> list[Capacity]: ...

    def get_aircraft_map(self) -> dict[str, Aircraft]: ...

    def close(self) -> None: ...


AbstractRepository = RepositoryProtocol
