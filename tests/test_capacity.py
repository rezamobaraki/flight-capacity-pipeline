from src.domains.aircraft import Aircraft
from src.domains.flight import Flight
from src.services.capacity_service import CapacityService


class TestCapacityService:
    def setup_method(self):
        self.service = CapacityService()
        self.aircraft_map = {
            "B789": Aircraft(
                code_iata="789",
                code_icao="B789",
                full_name="Boeing 787-9",
                category="B787",
                average_speed_mph=570.0,
                volume=74.78,
                payload=40610.85,
            ),
            "A388": Aircraft(
                code_iata="388",
                code_icao="A388",
                full_name="Airbus A380-800",
                category="A380",
                average_speed_mph=550.0,
                volume=86.74,
                payload=83417.60,
            ),
        }

    def test_calculate_matches_flights_to_aircraft(self):
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                destination_iata="HNL",
            ),
            Flight(
                flight_id="2",
                date="2022-10-03",
                equipment="A388",
                origin_iata="PER",
                destination_iata="LHR",
            ),
        ]
        caps = self.service.calculate(flights, self.aircraft_map)
        assert len(caps) == 2
        assert caps[0].volume_m3 == 74.78
        assert caps[1].payload_kg == 83417.60

    def test_calculate_skips_unmatched_equipment(self):
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="ZZZZ",
                origin_iata="AAA",
                destination_iata="BBB",
            ),
        ]
        caps = self.service.calculate(flights, self.aircraft_map)
        assert len(caps) == 0

    def test_calculate_preserves_flight_data(self):
        flights = [
            Flight(
                flight_id="1",
                flight_number="FX1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                destination_iata="HNL",
                operator="FDX",
            ),
        ]
        caps = self.service.calculate(flights, self.aircraft_map)
        assert caps[0].flight_number == "FX1"
        assert caps[0].operator == "FDX"
        assert caps[0].aircraft_name == "Boeing 787-9"
        assert caps[0].category == "B787"

    def test_calculate_empty_inputs(self):
        assert self.service.calculate([], self.aircraft_map) == []
        assert self.service.calculate([], {}) == []
