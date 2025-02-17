from pydantic import BaseModel, RootModel
from typing import Dict, Literal, Set, Union

class Gold(BaseModel):
    base: int
    purchasable: bool
    total: int
    sell: int


class Stat(BaseModel):
    name: str
    kind : Literal["flat", "percentage"] 
    value : float | int
    #Makes hashable to use in the set
    class Config:
        frozen = True

class Effects(RootModel):
    root: Dict[str, Union[int, float]]

class Item(BaseModel):
    name: str
    plaintext: str
    image: str 
    imageUrl: str
    gold: Gold
    tags: Set[str] 
    stats: Set[Stat] 
    effect: Effects
    id: int
    description: str
