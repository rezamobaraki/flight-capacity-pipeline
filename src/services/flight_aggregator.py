import logging
from collections import defaultdict
from collections.abc import Iterator

from src.domains.flight import Flight
from src.domains.flight_event import FlightEvent

logger = logging.getLogger(__name__)


class FlightAggregatorService:
    def aggregate(self, events: Iterator[FlightEvent]) -> list[Flight]:
        groups: dict[str, list[FlightEvent]] = defaultdict(list)
        total_events = 0

        for event in events:
            if not event.flight_id:
                continue
            groups[event.flight_id].append(event)
            total_events += 1

        flights = []
        for flight_id, group in groups.items():
            flight = self._build_flight(flight_id, group)
            if flight:
                flights.append(flight)

        logger.info(
            "Aggregated %d flights from %d events (%d groups)",
            len(flights),
            total_events,
            len(groups),
        )
        return flights

    def _build_flight(self, flight_id: str, events: list[FlightEvent]) -> Flight | None:
        equipment = self._first_nonempty(e.equipment for e in events)
        if not equipment:
            logger.debug("Flight %s has no equipment, skipping", flight_id)
            return None

        return Flight(
            flight_id=flight_id,
            flight_number=self._first_nonempty(e.flight for e in events),
            date=events[0].date,
            origin_iata=self._first_nonempty(e.origin_iata for e in events),
            origin_icao=self._first_nonempty(e.origin_icao for e in events),
            destination_iata=self._first_nonempty(e.destination_iata for e in events),
            destination_icao=self._first_nonempty(e.destination_icao for e in events),
            equipment=equipment,
            operator=self._first_nonempty(e.operator for e in events),
            registration=self._first_nonempty(e.registration for e in events),
        )

    @staticmethod
    def _first_nonempty(values: Iterator[str]) -> str:
        for v in values:
            if v:
                return v
        return ""
