from pydantic import BaseModel


class Location(BaseModel):
    id: int
    country_name: str
