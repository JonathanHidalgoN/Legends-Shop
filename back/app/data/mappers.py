from typing import Set
from app.data.models.OrderTable import OrderTable
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.LocationTable import LocationTable
from app.schemas.AuthSchemas import UserInDB
from app.schemas.Item import Effects, Gold, Item, Stat
from app.schemas.Order import CartItem, Order
from app.schemas.Location import Location
from app.data.models.CartTable import CartTable


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
        imageUrl=item.imageUrl,
        description=item.description,
    )
    return itemTable


def mapItemTableToItem(
    itemTable: ItemTable,
    gold: Gold,
    tags: Set[str],
    stats: Set[Stat],
    effects: Effects,
) -> Item:
    item: Item = Item(
        name=itemTable.name,
        plaintext=itemTable.plain_text,
        gold=gold,
        tags=tags,
        stats=stats,
        effect=effects,
        id=itemTable.id,
        image=itemTable.image,
        imageUrl=itemTable.imageUrl,
        description=itemTable.description,
    )
    return item


def mapUserInDBToUserTable(userInDB: UserInDB) -> UserTable:
    userTable: UserTable = UserTable(
        userName=userInDB.userName,
        password=userInDB.hashedPassword,
        created=userInDB.created,
        last_singn=userInDB.lastSingIn,
        gold_spend=userInDB.goldSpend,
        current_gold=userInDB.currentGold,
        email=userInDB.email,
        birthdate=userInDB.birthDate,
    )
    return userTable


def mapUserTableToUserInDB(userTable: UserTable) -> UserInDB:
    userInDB: UserInDB = UserInDB(
        userName=userTable.userName,
        hashedPassword=userTable.password,
        email=userTable.email,
        created=userTable.created,
        lastSingIn=userTable.last_singn,
        goldSpend=userTable.gold_spend,
        currentGold=userTable.current_gold,
        birthDate=userTable.birthdate,
        locationId=userTable.location_id,
    )
    return userInDB


def mapOrderToOrderTable(order: Order, userId: int) -> OrderTable:
    orderTable: OrderTable = OrderTable(
        user_id=userId,
        total=order.total,
        order_date=order.orderDate,
        delivery_date=order.deliveryDate,
        status=order.status,
        location_id=order.location_id,
        reviewed = order.reviewed
    )
    return orderTable


def mapCartTableToCartItem(cartTable: CartTable) -> CartItem:
    cartItem: CartItem = CartItem(
        id=cartTable.id, itemId=cartTable.item_id, status=cartTable.status
    )
    return cartItem


def mapLocationToLocationTable(location: Location) -> LocationTable:
    locationTable = LocationTable(id=location.id, country_name=location.country_name)
    return locationTable


def mapLocationTableToLocation(locationTable: LocationTable) -> Location:
    location = Location(id=locationTable.id, country_name=locationTable.country_name)
    return location
