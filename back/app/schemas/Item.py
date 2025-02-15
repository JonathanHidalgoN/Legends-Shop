from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Optional, Set, Union

class Gold(BaseModel):
    base: int
    purchasable: bool
    total: int
    sell: int


class Stats(RootModel):
    root: Dict[str, Union[int, float]]


class Effects(RootModel):
    root: Dict[str, Union[int, float]]

class Item(BaseModel):
    name: str
    colloq: str
    plaintext: str
    image: str 
    imageUrl: str
    gold: Gold
    tags: Set[str] 
    stats: Stats
    effect: Effects
    id: int
    description: str
