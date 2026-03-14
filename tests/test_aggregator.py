from src.domains.flight_event import FlightEvent
from src.services.flight_aggregator import FlightAggregatorService


class TestFlightAggregatorService:
    def setup_method(self):
        self.aggregator = FlightAggregatorService()

    def test_aggregate_groups_by_flight_id(self):
        events = [
            FlightEvent(
                address="A",
                date="2022-10-03",
                event="descent",
                flight_id="1",
                equipment="B789",
                flight="FX1",
                origin_iata="MEM",
                destination_iata="HNL",
                time="02:00:00",
            ),
            FlightEvent(
                address="A",
                date="2022-10-03",
                event="landed",
                flight_id="1",
                equipment="B789",
                flight="FX1",
                origin_iata="MEM",
                destination_iata="HNL",
                time="03:00:00",
            ),
            FlightEvent(
                address="B",
                date="2022-10-03",
                event="cruising",
                flight_id="2",
                equipment="A388",
                flight="QF7",
                origin_iata="PER",
                destination_iata="LHR",
                time="04:00:00",
            ),
        ]
        flights = self.aggregator.aggregate(iter(events))
        assert len(flights) == 2

    def test_aggregate_consolidates_fields(self):
        events = [
            FlightEvent(
                address="A",
                date="2022-10-03",
                event="descent",
                flight_id="1",
                equipment="B789",
                flight="",
                origin_iata="",
                destination_iata="HNL",
                time="02:00:00",
            ),
            FlightEvent(
                address="A",
                date="2022-10-03",
                event="landed",
                flight_id="1",
                equipment="B789",
                flight="FX1",
                origin_iata="MEM",
                destination_iata="HNL",
                time="03:00:00",
            ),
        ]
        flights = self.aggregator.aggregate(iter(events))
        assert len(flights) == 1
        assert flights[0].flight_number == "FX1"
        assert flights[0].origin_iata == "MEM"

    def test_aggregate_skips_no_equipment(self):
        events = [
            FlightEvent(
                address="A",
                date="2022-10-03",
                event="landed",
                flight_id="1",
                equipment="",
                flight="",
                time="02:00:00",
            ),
        ]
        flights = self.aggregator.aggregate(iter(events))
        assert len(flights) == 0

    def test_aggregate_empty_input(self):
        flights = self.aggregator.aggregate(iter([]))
        assert len(flights) == 0
