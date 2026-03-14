from abc import ABC, abstractmethod
from typing import Optional

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight


class AbstractRepository(ABC):
    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def is_empty(self) -> bool: ...

    @abstractmethod
    def save_aircraft_batch(self, aircraft: list[Aircraft]) -> int: ...

    @abstractmethod
    def save_flights_batch(self, flights: list[Flight]) -> int: ...

    @abstractmethod
    def save_capacity_batch(self, capacities: list[Capacity]) -> int: ...

    @abstractmethod
    def get_capacity(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
    ) -> list[Capacity]: ...

    @abstractmethod
    def get_aircraft_map(self) -> dict[str, Aircraft]: ...

    @abstractmethod
    def close(self) -> None: ...
