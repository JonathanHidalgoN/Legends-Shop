from typing import Set
from app.data.models.ItemTable import ItemTable
from app.data.models.GoldTable import GoldTable
from app.schemas.Item import Effects, Gold, Item, Stats

def mapGoldToGoldTable(gold: Gold) -> GoldTable:
    goldTable = GoldTable(
        base_cost=gold.base,
        total=gold.total,
        sell=gold.sell,
        purchaseable=gold.purchasable,
    )
    return goldTable


def mapGoldTableToGold(goldTable: GoldTable) -> Gold:
    gold = Gold(
        base=goldTable.base_cost,
        purchasable=goldTable.purchaseable,
        total=goldTable.total,
        sell=goldTable.sell,
    )
    return gold


def mapItemToItemTable(item: Item, goldId: int, updated: bool = True) -> ItemTable:
    itemTable: ItemTable = ItemTable(
        name=item.name,
        plain_text=item.plaintext,
        image=item.image,
        gold_id=goldId,
        updated=updated,
    )
    return itemTable


def mapItemTableToItem(
    itemTable: ItemTable,
    gold: Gold,
    tags: Set[str],
    stats: Stats,
    effects: Effects,
    image: str,
) -> Item:
    item: Item = Item(
        name=itemTable.name,
        colloq="",
        plaintext=itemTable.plain_text,
        gold=gold,
        tags=tags,
        stats=stats,
        effect=effects,
        id=0,
        image=image,
    )
    return item
