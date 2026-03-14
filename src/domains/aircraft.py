from pydantic import BaseModel


class Aircraft(BaseModel):
    code_iata: str
    code_icao: str
    full_name: str
    category: str = ""
    average_speed_mph: float = 0.0
    volume: float = 0.0
    payload: float = 0.0
