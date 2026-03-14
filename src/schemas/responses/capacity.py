from pydantic import BaseModel


class CapacityResponse(BaseModel):
    flight_id: str
    flight_number: str
    date: str
    origin_iata: str
    destination_iata: str
    equipment: str
    aircraft_name: str
    category: str
    volume_m3: float
    payload_kg: float
    operator: str


class DailySummaryResponse(BaseModel):
    date: str
    origin_iata: str
    destination_iata: str
    total_flights: int
    total_volume_m3: float
    total_payload_kg: float


class CapacityListResponse(BaseModel):
    count: int
    capacities: list[CapacityResponse]


class DailySummaryListResponse(BaseModel):
    count: int
    summaries: list[DailySummaryResponse]
