import pytest
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.ItemsLoader import ItemsLoader
from unittest.mock import MagicMock
from staticData import STATIC_DATA_ITEMS_JSON,STATIC_DATA_ITEM2, STATIC_DATA_ITEM1 

from app.schemas.Item import Item, Stat

@pytest.fixture
def loader()-> ItemsLoader:
    mockSession = MagicMock(spec=AsyncSession)
    loader = ItemsLoader(mockSession)
    loader.VERSION_URL = "test_url"
    loader.itemsUrl="test_url"
    return loader

def test_makeItemsUrl(loader):
    version : str = "1.0.0"
    url : str = loader.makeItemsUlr(version)
    assert url == f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"

def test_getUniqueStatsNameAndKind(loader):
    items: List[Item] = [STATIC_DATA_ITEM1, STATIC_DATA_ITEM2]
    unique_stats = loader.getUniqueStats(items)
    assert isinstance(unique_stats, Set)
    assert len(unique_stats) == 3, "There should be four unique stats"
    stat1 : Stat = Stat(name="Damage", kind="flat", value=20)
    stat2 : Stat = Stat(name="Health", kind="percentage", value=10)
    stat3 : Stat = Stat(name="Armor", kind="percentage", value=5)
    expectedStats = set()
    expectedStats.add(stat1)
    expectedStats.add(stat2)
    expectedStats.add(stat3)
    assert unique_stats == expectedStats, "The sets of stats do not match"

