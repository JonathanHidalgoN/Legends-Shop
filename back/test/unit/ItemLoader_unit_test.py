import pytest
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import UpdateItemsError
from app.data.ItemsLoader import ItemsLoader
from unittest.mock import AsyncMock, MagicMock, patch
from app.data.models.GoldTable import GoldTable
from staticData import *


from app.schemas.Item import Effects, Gold, Item, Stat

@pytest.fixture
def loader() -> ItemsLoader:
    mockSession = MagicMock(spec=AsyncSession)
    loader = ItemsLoader(mockSession)
    loader.VERSION_URL = "test_url"
    loader.itemsUrl = "test_url"
    loader.version = "test"
    return loader


def test_makeItemsUrl(loader):
    version: str = "1.0.0"
    url: str = loader.makeItemsUlr(version)
    assert (
        url == f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    )


def test_getUniqueStatsNameAndKind(loader):
    items: List[Item] = [STATIC_DATA_ITEM1, STATIC_DATA_ITEM2]
    unique_stats = loader.getUniqueStats(items)
    assert isinstance(unique_stats, Set)
    assert len(unique_stats) == 3, "There should be four unique stats"
    stat1: Stat = Stat(name="Damage", kind="flat", value=20)
    stat2: Stat = Stat(name="Health", kind="percentage", value=10)
    stat3: Stat = Stat(name="Armor", kind="percentage", value=5)
    expectedStats = set()
    expectedStats.add(stat1)
    expectedStats.add(stat2)
    expectedStats.add(stat3)
    assert unique_stats == expectedStats, "The sets of stats do not match"


@pytest.mark.asyncio
async def test_parseDataNodeIntoItem(loader):
    itemsData = STATIC_DATA_ITEMS_JSON.get("data")
    if itemsData is None:
        # To make the linter happy
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
    assert (
        item.imageUrl
        == "https://ddragon.leagueoflegends.com/cdn/test/img/item/1001.png"
    )
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
        result = await loader.parseDataNodeIntoItem(
            itemId, itemData, itemNames, statMapping
        )
    assert result is None


def test_parseStatsNodeIntoStats(loader):
    statsNode = {
        "FlatMovementSpeedMod": 25,
        "PercentBonusDamage": 15,
    }
    statMappingDict = {
        "FlatMovementSpeedMod": "MovementSpeed",
        "PercentBonusDamage": "BonusDamage",
    }
    stats = loader.parseStatsNodeIntoStats(statsNode, statMappingDict)
    expected_stats = {
        Stat(name="MovementSpeed", value=25, kind="flat"),
        Stat(name="BonusDamage", value=15, kind="percentage"),
    }
    assert stats == expected_stats


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


def test_addEffecctInDataBaseIfNew_new_effect(loader):
    effect = "new-effect"
    existingEffectNames = {"existing1", "existing2"}
    result = loader.addEffectInDataBaseIfNew(effect, existingEffectNames)
    assert result is True
    loader.dbSession.add.assert_called_once()
    added_tag = loader.dbSession.add.call_args[0][0]
    assert added_tag.name == effect


def test_addEffectInDataBaseIfNew_existing_effect(loader):
    effect = "existing-tag"
    existingEffectNames = {"existing-tag", "another-tag"}
    result = loader.addEffectInDataBaseIfNew(effect, existingEffectNames)
    assert result is False
    loader.dbSession.add.assert_not_called()


@pytest.mark.asyncio
async def test_updateItemsInDataBase_success(loader):
    items_list = [STATIC_DATA_ITEM1, STATIC_DATA_ITEM2]
    loader.insertOrUpdateItemTable = AsyncMock(return_value=None)
    # Patch will change the object method for a mock taht return None temporally
    # Second patch on the query function to return None, this means that the item is new
    with patch.object(
        loader, "insertOrUpdateItemTable", new=AsyncMock(return_value=None)
    ) as mockInsert, patch(
        "app.data.ItemsLoader.getItemTableGivenItemName",
        new=AsyncMock(return_value=None),
    ):
        await loader.updateItemsInDataBase(items_list)
        loader.dbSession.commit.assert_called_once()
        assert mockInsert.call_count == len(items_list)


@pytest.mark.asyncio
async def test_updateItemsInDataBase_failure(loader):
    items_list = [STATIC_DATA_ITEM1]
    # Patch will change the object method and raise an exception
    # Second patch on the query function to return None, this means that the item is new
    with patch.object(
        loader,
        "insertOrUpdateItemTable",
        new=AsyncMock(side_effect=Exception("Simulated error")),
    ) as mockInsert, patch(
        "app.data.ItemsLoader.getItemTableGivenItemName",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(UpdateItemsError):
            await loader.updateItemsInDataBase(items_list)


@pytest.mark.asyncio
async def test_insertOrUpdateGoldTable_insert_success(loader):
    itemId = None
    gold: Gold = Gold(base=0, purchasable=True, total=0, sell=0)
    createNewGoldTable = True
    expectedId: int = 0
    goldTable: GoldTable = GoldTable()
    goldTable.id = expectedId
    mergeMock: AsyncMock = AsyncMock(return_value=goldTable)
    with patch.object(loader.dbSession, "merge", new=mergeMock) as mockMege:
        itemId = await loader.insertOrUpdateGoldTable(createNewGoldTable, gold, itemId)
        assert itemId == expectedId


@pytest.mark.asyncio
async def test_insertOrUpdateGoldTable_error_NoneId_NoNewGoldTable(loader):
    itemId = None
    gold: Gold = Gold(base=0, purchasable=True, total=0, sell=0)
    createNewGoldTable = False
    with pytest.raises(UpdateItemsError):
        await loader.insertOrUpdateGoldTable(createNewGoldTable, gold, itemId)


@pytest.mark.asyncio
async def test_insertOrUpdateGoldTable_error_GoldTableDoesNotExist(loader):
    itemId = 1
    gold: Gold = Gold(base=0, purchasable=True, total=0, sell=0)
    createNewGoldTable = False
    idMock: AsyncMock = AsyncMock(return_value=None)
    with patch("app.data.ItemsLoader.getGoldIdWithItemId", new=idMock):
        with pytest.raises(UpdateItemsError):
            await loader.insertOrUpdateGoldTable(createNewGoldTable, gold, itemId)


@pytest.mark.asyncio
async def test_addItemTagsRelations_success(loader):
    itemId = 101
    tags = {"tag1", "tag2"}
    with patch("app.data.ItemsLoader.getTagIdWithtTagName", return_value=1):
        loader.dbSession.execute = AsyncMock(return_value=None)
        await loader.addItemTagsRelations(itemId, tags)
        assert loader.dbSession.execute.call_count == len(tags)


@pytest.mark.asyncio
async def test_addItemTagsRelations_missing_tag(loader):
    itemId = 101
    tags = {"tag1"}
    with patch(
        "app.data.ItemsLoader.getTagIdWithtTagName", new=AsyncMock(return_value=None)
    ):
        with pytest.raises(UpdateItemsError):
            await loader.addItemTagsRelations(itemId, tags)


@pytest.mark.asyncio
async def test_addItemTagsRelations_execute_failure(loader):
    itemId = 101
    tags = {"tag1"}
    with patch(
        "app.data.ItemsLoader.getTagIdWithtTagName", new=AsyncMock(return_value=201)
    ):
        loader.dbSession.execute = AsyncMock(side_effect=Exception("DB error"))
        with pytest.raises(UpdateItemsError):
            await loader.addItemTagsRelations(itemId, tags)


@pytest.mark.asyncio
async def test_addItemEffectsRelations_success(loader):
    itemId = 101
    effects = Effects(root={"effect1": 5, "effect2": 10})
    with patch(
        "app.data.ItemsLoader.getEffectIdWithEffectName", new=AsyncMock(return_value=1)
    ):
        loader.dbSession.execute = AsyncMock(return_value=None)
        await loader.addItemEffectsRelations(itemId, effects)
        assert loader.dbSession.execute.call_count == len(effects.root)


@pytest.mark.asyncio
async def test_addItemEffectsRelations_missing_effect(loader):
    itemId = 101
    effects = Effects(root={"effect1": 5})
    with patch(
        "app.data.ItemsLoader.getEffectIdWithEffectName",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(UpdateItemsError):
            await loader.addItemEffectsRelations(itemId, effects)


@pytest.mark.asyncio
async def test_addItemEffectsRelations_execute_failure(loader):
    itemId = 101
    effects = Effects(root={"effect1": 5})
    with patch(
        "app.data.ItemsLoader.getEffectIdWithEffectName",
        new=AsyncMock(return_value=201),
    ):
        loader.dbSession.execute = AsyncMock(side_effect=Exception("DB error"))
        with pytest.raises(UpdateItemsError):
            await loader.addItemEffectsRelations(itemId, effects)


@pytest.mark.asyncio
async def test_addItemStatsRelations_success(loader):
    itemId = 101
    stats = {
        Stat(name="Damage", kind="flat", value=20),
        Stat(name="Health", kind="percentage", value=10),
    }
    with patch("app.data.ItemsLoader.getStatIdWithStatName", return_value=1):
        loader.dbSession.execute = AsyncMock(return_value=None)
        await loader.addItemStatsRelations(itemId, stats)
        assert loader.dbSession.execute.call_count == len(stats)


@pytest.mark.asyncio
async def test_addItemStatsRelations_missing_stat(loader):
    itemId = 101
    stats = {Stat(name="Damage", kind="flat", value=20)}
    with patch("app.data.ItemsLoader.getStatIdWithStatName", return_value=None):
        with pytest.raises(
            UpdateItemsError, match="Stat was not found in the database"
        ):
            await loader.addItemStatsRelations(itemId, stats)


@pytest.mark.asyncio
async def test_addItemStatsRelations_execute_failure(loader):
    itemId = 101
    stats = {Stat(name="Damage", kind="flat", value=20)}
    with patch("app.data.ItemsLoader.getStatIdWithStatName", return_value=1):
        loader.dbSession.execute = AsyncMock(side_effect=Exception("DB error"))
        with pytest.raises(
            UpdateItemsError, match="Could not insert a relation item-stat"
        ):
            await loader.addItemStatsRelations(itemId, stats)
