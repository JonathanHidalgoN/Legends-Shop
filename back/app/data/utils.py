from typing import Dict, List, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.mappers import mapGoldTableToGold, mapItemTableToItem
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import (
    getAllEffectNamesAndValueAssociatedByItemId,
    getAllStatNamesAndValueAssociatedByItemId,
    getAllTagNamesAssociatedByItemId,
    getGoldTableWithId,
    getItems,
)
from app.schemas.Item import Effects, Gold, Item, Stats


async def getAllItemTableRowsAnMapToItems(asyncSession: AsyncSession) -> List[Item]:
    """
    Get all itemTable rows and map to Item objects
    """
    items: List[Item] = []
    itemTableRows: List[ItemTable] = await getItems(asyncSession)
    for itemTable in itemTableRows:
        item: Item = await convertItemTableIntoItem(asyncSession, itemTable)
        items.append(item)
    return items


async def convertItemTableIntoItem(
    asyncSession: AsyncSession, itemTable: ItemTable
) -> Item:
    """
    This function takes an itemTable and get all the relations wiht gold,effects,stats and tags.
    Then creates an Item object
    """
    goldTable: GoldTable | None = await getGoldTableWithId(
        asyncSession, itemTable.gold_id
    )
    gold: Gold = mapGoldTableToGold(goldTable)
    tags: Set[str] = await getAllTagNamesAssociatedByItemId(asyncSession, itemTable.id)
    statsData: Dict[str, int | float] = await getAllStatNamesAndValueAssociatedByItemId(
        asyncSession, itemTable.id
    )
    effectsData: Dict[str, int | float] = (
        await getAllEffectNamesAndValueAssociatedByItemId(asyncSession, itemTable.id)
    )
    stats: Stats = Stats(root=statsData)
    effects: Effects = Effects(root=effectsData)
    return mapItemTableToItem(itemTable, gold, tags, stats, effects)
