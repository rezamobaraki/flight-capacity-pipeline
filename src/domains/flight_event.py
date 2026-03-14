
from pydantic import BaseModel, field_validator


class FlightEvent(BaseModel):
    address: str
    altitude: int = 0
    callsign: str = ""
    date: str
    destination_iata: str = ""
    destination_icao: str = ""
    equipment: str = ""
    event: str
    flight: str = ""
    flight_id: str
    latitude: float | None = None
    longitude: float | None = None
    operator: str = ""
    origin_iata: str = ""
    origin_icao: str = ""
    registration: str = ""
    time: str

    @field_validator("altitude", mode="before")
    @classmethod
    def coerce_altitude(cls, value: str | int) -> int:
        if not value and value != 0:
            return 0
        return int(value)

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def coerce_coordinate(cls, value: str | float | None) -> float | None:
        if not value and value != 0:
            return None
        return float(value)
