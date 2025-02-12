from pydantic import BaseModel, RootModel
from typing import List, Dict, Set, Union


class Image(BaseModel):
    full: str
    sprite: str
    group: str


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
    image: Image
    gold: Gold
    tags: Set[str]
    stats: Stats
    effect: Effects
    id: int
