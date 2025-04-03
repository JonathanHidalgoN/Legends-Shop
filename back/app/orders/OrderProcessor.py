import random
from datetime import date, datetime, timedelta
from typing import List, Set, Optional
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.mappers import mapOrderToOrderTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.data.queries.orderQueries import getOrderHistoryByUserId, getOrderWithId
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    NotEnoughGoldException,
    OrderNotFoundException,
    ProcessOrderException,
)
from app.data.queries.itemQueries import getGoldBaseWithItemId, getItemIdByItemName
from app.schemas.Order import Order, OrderDataPerItem, OrderStatus
from sqlalchemy.exc import SQLAlchemyError

from app.data.queries.profileQueries import (
    getCurrentUserGoldWithUserId,
    getTotalSpendUserGoldWithUserId,
    updateUserGoldWithUserId,
    updateUserSpendGoldWithUserId,
)
from app.auth.functions import logMethod
from app.data.queries.deliveryDatesQueries import getDeliveryDateForItemAndLocation


class OrderProcessor:

    def __init__(self, dbSession: AsyncSession) -> None:
        self.dbSession = dbSession
        pass

    @logMethod
    async def makeOrder(self, order: Order, userId: int) -> int:
        """
        Processes an order for a given user.

        This function maps the provided order to an order table record, retrieves order item data,
        compares the computed total cost with the provided order total, and registers the order and
        its associated items in the database.

        Args:
            order (Order): The order details.
            userId (int): The ID of the user placing the order.

        Raises:
            ProcessOrderException: If the order cannot be processed or if there is a database error.
        """
        try:
            orderId: int = await self.addOrder(order, userId)
            orderDataPerItem: List[OrderDataPerItem] = await self.getOrderDataPerItem(
                order, orderId
            )
            self.comparePrices(orderDataPerItem, order.total)
            leftGold: int = await self.computeUserChange(userId, order.total)
            await self.insertItemOrderData(orderId, orderDataPerItem)
            # If an user send a lot of orders does this async job run and make the gold negative?
            await self.updateUserGold(userId, leftGold)
            await self.updateTotalUserSpendGold(userId, order.total)
            await self.dbSession.commit()
            return orderId
        except ProcessOrderException as e:
            await self.dbSession.rollback()
            raise e
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise ProcessOrderException("Internal server error") from e
        except Exception as e:
            await self.dbSession.rollback()
            raise ProcessOrderException("Internal server error") from e

    @logMethod
    def createRandomDate(self, ref: datetime) -> datetime:
        days = random.randint(1, 14)
        return ref + timedelta(days=days)

    @logMethod
    async def determineDeliveryDate(self, order: Order) -> date:
        furthestDeliveryDate: Optional[date] = None
        for itemName in order.itemNames:
            itemId: Optional[int] = await getItemIdByItemName(self.dbSession, itemName)
            if itemId is None:
                raise InvalidItemException(f"Item {itemName} is not in the database")
            deliveryDate: Optional[date] = await getDeliveryDateForItemAndLocation(
                self.dbSession, itemId, order.location_id, order.orderDate
            )
            if deliveryDate is None:
                raise ProcessOrderException(
                    f"No delivery date found for item {itemName} at location {order.location_id}"
                )
            if furthestDeliveryDate is None or deliveryDate > furthestDeliveryDate:
                furthestDeliveryDate = deliveryDate
        if furthestDeliveryDate is None:
            raise ProcessOrderException("Could not determine delivery date for order")
        return furthestDeliveryDate

    @logMethod
    async def addOrder(self, order: Order, userId: int) -> int:
        try:
            order.status = OrderStatus.PENDING
            order.deliveryDate = datetime.combine(
                (await self.determineDeliveryDate(order)), datetime.min.time()
            )
            orderTable: OrderTable = mapOrderToOrderTable(order, userId)
            self.dbSession.add(orderTable)
            await self.dbSession.flush()
            return orderTable.id
        except SQLAlchemyError as e:
            raise ProcessOrderException(f"Internal server error")

    @logMethod
    async def insertItemOrderData(
        self, orderId: int, orderDataPerItem: List[OrderDataPerItem]
    ) -> None:
        """
        Registersassociated items in the database.

        This function iteratively inserts
        order item associations for each item in the order. If any database error occurs,
        the function logs the error and raises a ProcessOrderException.

        Args:
            orderTable (OrderTable): The order table record.
            orderDataPerItem (List[OrderDataPerItem]): A list containing data for each order item.

        Raises:
            ProcessOrderException: If a database error occurs when adding the order or its items.
        """
        for data in orderDataPerItem:
            val: dict[str, int] = {
                "order_id": orderId,
                "item_id": data.itemId,
                "quantity": data.quantity,
            }
            try:
                ins = insert(OrderItemAssociation).values(**val)
                await self.dbSession.execute(ins)
            except SQLAlchemyError as e:
                raise ProcessOrderException("Internal server error")

    @logMethod
    async def getOrderDataPerItem(
        self, order: Order, orderTableId: int
    ) -> List[OrderDataPerItem]:
        """
        Retrieves order data for each unique item in the order.

        For every unique item name provided in the order, this function:
        - Retrieves the corresponding item ID from the database.
        - Calculates the quantity of the item in the order.
        - Retrieves the base cost of the item.
        - Computes the total cost for the item.
        It then creates and returns a list of OrderDataPerItem objects containing these details.

        Args:
            order (Order): The order details, including a list of item names.
            orderTableId: The ID of the associated order record in the order table.

        Returns:
            List[OrderDataPerItem]: A list of data objects for each order item.

        Raises:
            InvalidItemException: If an item does not exist in the database or if its base cost cannot be found.
        """
        orderDataPerItem: List[OrderDataPerItem] = []
        uniqueItemNames: Set[str] = set(order.itemNames)
        for itemName in uniqueItemNames:
            itemId: Optional[int] = await getItemIdByItemName(self.dbSession, itemName)
            if itemId is None:
                raise InvalidItemException(f"Item {itemName} is not in the database")
            amountOfItemInOrder: int = len(
                [e for e in order.itemNames if e == itemName]
            )
            baseCostOfItem: Optional[int] = await getGoldBaseWithItemId(
                self.dbSession, itemId
            )
            if baseCostOfItem is None:
                raise InvalidItemException(
                    f"Could not find the base cost of item {itemName}"
                )
            total: int = int(amountOfItemInOrder * baseCostOfItem)
            data: OrderDataPerItem = OrderDataPerItem(
                itemId=itemId,
                orderId=orderTableId,
                quantity=amountOfItemInOrder,
                total=total,
            )
            orderDataPerItem.append(data)
        return orderDataPerItem

    @logMethod
    def comparePrices(
        self, orderDataPerItem: List[OrderDataPerItem], orderPrice: int
    ) -> None:
        """
        Compares the computed total cost of the order items with the provided order total.

        This function sums the total cost from each order item and checks if it matches the
        total price provided in the order. If there is a discrepancy, it logs an error and raises
        a DifferentTotal exception.

        Args:
            orderDataPerItem (List[OrderDataPerItem]): A list of data objects for each order item.
            orderPrice: The total price provided in the order.

        Raises:
            DifferentTotal: If the computed total cost does not equal the provided order total.
        """
        totalPrice: int = 0
        for data in orderDataPerItem:
            totalPrice += data.total
        if totalPrice != orderPrice:
            raise DifferentTotal(
                orderPrice, totalPrice, "Total in order is not correct"
            )

    @logMethod
    async def cancelOrder(self, userId: int, orderId: int) -> None:
        orderTable: Optional[OrderTable] = await getOrderWithId(self.dbSession, orderId)
        if orderTable is None:
            raise OrderNotFoundException("Order not found")
        if orderTable.user_id != userId:
            raise ProcessOrderException("The user can't edit this order")
        if orderTable.status not in (OrderStatus.PENDING, OrderStatus.SHIPPED):
            raise ProcessOrderException(
                f"An order with status {orderTable.status} can't be cancelled"
            )
        orderTable.status = OrderStatus.CANCELED
        try:
            await self.dbSession.commit()
        except SQLAlchemyError as e:
            raise ProcessOrderException("Internal server error") from e
        except Exception as e:
            raise ProcessOrderException("Internal server error") from e

    @logMethod
    async def computeUserChange(self, userId: int, total: int) -> int:
        userCurrentGold: Optional[int] = await getCurrentUserGoldWithUserId(
            self.dbSession, userId
        )
        if userCurrentGold is None:
            raise ProcessOrderException("Internal server error")
        if userCurrentGold < 0:
            raise ProcessOrderException("Internal server error")
        leftGold: int = userCurrentGold - total
        if leftGold < 0:
            raise NotEnoughGoldException("Not enough gold")
        return leftGold

    @logMethod
    async def updateUserGold(self, userId: int, newGold: int) -> None:
        try:
            await updateUserGoldWithUserId(self.dbSession, userId, newGold)
        except SQLAlchemyError as e:
            raise ProcessOrderException("Internal server error")

    @logMethod
    async def updateTotalUserSpendGold(self, userId: int, toAdd: int) -> None:
        try:
            userSpendGold: Optional[int] = await getTotalSpendUserGoldWithUserId(
                self.dbSession, userId
            )
        except SQLAlchemyError as e:
            raise ProcessOrderException("Internal server error")
        if userSpendGold is None:
            raise ProcessOrderException("Interanl server error")
        newSpend: int = userSpendGold + toAdd
        try:
            await updateUserSpendGoldWithUserId(self.dbSession, userId, newSpend)
        except SQLAlchemyError as e:
            raise ProcessOrderException("Internal server error")

    @logMethod
    async def getOrderHistory(self, userId: int) -> List[Order]:
        try:
            orderHistory: List[Order] = await getOrderHistoryByUserId(
                self.dbSession, userId
            )
            return orderHistory
        except SQLAlchemyError as e:
            raise ProcessOrderException("Internal server error")
