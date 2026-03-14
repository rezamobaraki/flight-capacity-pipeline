import logging

from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight

logger = logging.getLogger(__name__)


class CapacityService:
    def calculate(
        self,
        flights: list[Flight],
        aircraft_map: dict[str, Aircraft],
    ) -> list[Capacity]:
        capacities: list[Capacity] = []
        unmatched: set[str] = set()

        for flight in flights:
            aircraft = aircraft_map.get(flight.equipment)
            if not aircraft:
                unmatched.add(flight.equipment)
                continue

            capacities.append(
                Capacity(
                    flight_id=flight.flight_id,
                    flight_number=flight.flight_number,
                    date=flight.date,
                    origin_iata=flight.origin_iata,
                    origin_icao=flight.origin_icao,
                    destination_iata=flight.destination_iata,
                    destination_icao=flight.destination_icao,
                    equipment=flight.equipment,
                    aircraft_name=aircraft.full_name,
                    category=aircraft.category,
                    volume_m3=aircraft.volume,
                    payload_kg=aircraft.payload,
                    operator=flight.operator,
                )
            )

        if unmatched:
            logger.warning("Unmatched equipment codes: %s", sorted(unmatched))

        logger.info(
            "Calculated capacity for %d flights, %d equipment codes unmatched",
            len(capacities),
            len(unmatched),
        )
        return capacities
