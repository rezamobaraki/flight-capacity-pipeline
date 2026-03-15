from pydantic import BaseModel


class Capacity(BaseModel):
    flight_id: str
    flight_number: str = ""
    date: str
    origin_iata: str = ""
    origin_icao: str = ""
    destination_iata: str = ""
    destination_icao: str = ""
    equipment: str = ""
    aircraft_name: str = ""
    category: str = ""
    volume_m3: float | None = None
    payload_kg: float | None = None
    operator: str = ""


class CapacitySummary(BaseModel):
    date: str
    origin_iata: str
    destination_iata: str
    total_flights: int
    total_volume_m3: float
    total_payload_kg: float
