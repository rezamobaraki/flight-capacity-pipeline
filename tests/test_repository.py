from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity
from src.domains.flight import Flight


class TestSQLiteRepository:
    def test_save_and_retrieve_aircraft(self, container):
        repo = container.repository
        aircraft = [
            Aircraft(
                code_iata="388",
                code_icao="A388",
                full_name="Airbus A380-800",
                category="A380",
                average_speed_mph=550.0,
                volume=86.74,
                payload=83417.60,
            ),
        ]
        count = repo.save_aircraft_batch(aircraft)
        assert count == 1
        amap = repo.get_aircraft_map()
        assert "A388" in amap
        assert amap["A388"].full_name == "Airbus A380-800"

    def test_save_and_retrieve_capacity(self, container):
        repo = container.repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                aircraft_name="Boeing 787-9",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-03",
                origin_iata="PER",
                destination_iata="LHR",
                equipment="A388",
                aircraft_name="Airbus A380-800",
                volume_m3=86.74,
                payload_kg=83417.60,
            ),
        ]
        repo.save_capacity_batch(caps)
        assert not repo.is_empty()

    def test_get_capacity_filters_by_origin(self, container):
        repo = container.repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-03",
                origin_iata="PER",
                destination_iata="LHR",
                equipment="A388",
                volume_m3=86.74,
                payload_kg=83417.60,
            ),
        ]
        repo.save_capacity_batch(caps)
        result = repo.get_capacity(origin="MEM")
        assert len(result) == 1
        assert result[0].flight_id == "1"

    def test_get_capacity_filters_by_date(self, container):
        repo = container.repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-04",
                origin_iata="MEM",
                destination_iata="HNL",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
        ]
        repo.save_capacity_batch(caps)
        result = repo.get_capacity(date="2022-10-03")
        assert len(result) == 1

    def test_is_empty_on_fresh_db(self, container):
        assert container.repository.is_empty()
