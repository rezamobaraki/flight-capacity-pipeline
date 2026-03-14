from typing import Optional, Union

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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    operator: str = ""
    origin_iata: str = ""
    origin_icao: str = ""
    registration: str = ""
    time: str

    @field_validator("altitude", mode="before")
    @classmethod
    def coerce_altitude(cls, v: Union[str, int]) -> int:
        if not v and v != 0:
            return 0
        return int(v)

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def coerce_coordinate(cls, v: Union[str, float, None]) -> Optional[float]:
        if not v and v != 0:
            return None
        return float(v)
