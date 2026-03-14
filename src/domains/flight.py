from pydantic import BaseModel


class Flight(BaseModel):
    flight_id: str
    flight_number: str = ""
    date: str
    origin_iata: str = ""
    origin_icao: str = ""
    destination_iata: str = ""
    destination_icao: str = ""
    equipment: str = ""
    operator: str = ""
    registration: str = ""
