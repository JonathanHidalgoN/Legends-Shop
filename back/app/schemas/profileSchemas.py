from pydantic import BaseModel


class UserGoldResponse(BaseModel):
    userGold: int
