from pydantic import BaseModel
from typing import List


class Image(BaseModel):
    full: str
    sprite: str
    group: str


class Gold(BaseModel):
    base: int
    purchasable: bool
    total: int
    sell: int


class Stats(BaseModel):
    FlatHPPoolMod: int


class Item(BaseModel):
    name: str
    colloq: str
    plaintext: str
    image: Image
    gold: Gold
    tags: List[str]
    maps: dict
    stats: Stats
    depth: int
