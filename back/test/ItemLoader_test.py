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
    loader.version = "test"
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

# @patch.object(ItemsLoader, 'updateDbVersion', return_value=None)
# @patch.object(ItemsLoader, 'createMappingStatsDict', return_value=None)
# def test_parseItemsJsonIntoItemList(loader):

@pytest.mark.asyncio
async def test_parseDataNodeIntoItem(loader):
    itemsData = STATIC_DATA_ITEMS_JSON.get("data")
    if itemsData is None:
        #To make the linter happy
        return
    itemNames = set()
    statMapping = {"FlatMovementSpeedMod": "FlatMovementSpeedMod"}
    itemData = itemsData["1001"]
    item = await loader.parseDataNodeIntoItem(1001, itemData, itemNames, statMapping)
    assert item is not None
    assert item.name == "Boots"
    assert item.id == 1001
    assert item.plaintext == "Slightly increases Move Speed"
    assert item.gold.base == 300
    assert item.imageUrl == "https://ddragon.leagueoflegends.com/cdn/test/img/item/1001.png"
    expected_stat = Stat(name="FlatMovementSpeedMod", kind="flat", value=25)
    assert expected_stat in item.stats
    assert item.effect.root == {}

@pytest.mark.asyncio
async def test_parseDataNodeIntoItem_no_name(loader, caplog):
    itemData = {}
    itemId = 123
    itemNames = set()
    statMapping = {"FlatStat": "flat"}
    with caplog.at_level("WARNING"):
        result = await loader.parseDataNodeIntoItem(itemId, itemData, itemNames, statMapping)
    assert result is None

# def test_parseStatsNodeIntoStats(loader):
#     statsNode = {
#         "FlatMovementSpeedMod": 25,
#         "PercentBonusDamage": 15,
#     }
#     statMappingDict = {
#         "FlatMovementSpeedMod": "MovementSpeed",
#         "PercentBonusDamage": "BonusDamage",
#     }
#     stats = loader.parseStatsNodeIntoStats(statsNode, statMappingDict)
#     expected_stats = {
#         Stat(name="MovementSpeed", value=25, kind="flat"),
#         Stat(name="BonusDamage", value=15, kind="percentage"),
#     }
#     assert stats == expected_stats

def test_addTagInDataBaseIfNew_new_tag(loader):
    tag = "new-tag"
    existingTagNames = {"existing1", "existing2"}
    result = loader.addTagInDataBaseIfNew(tag, existingTagNames)
    assert result is True
    loader.dbSession.add.assert_called_once()
    added_tag = loader.dbSession.add.call_args[0][0]
    assert added_tag.name == tag

def test_addTagInDataBaseIfNew_existing_tag(loader):
    tag = "existing-tag"
    existingTagNames = {"existing-tag", "another-tag"}
    result = loader.addTagInDataBaseIfNew(tag, existingTagNames)
    assert result is False
    loader.dbSession.add.assert_not_called()
