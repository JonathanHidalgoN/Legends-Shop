import random
from datetime import datetime, timedelta
from typing import List, Set
from sqlalchemy import insert
from app.data.mappers import mapOrderToOrderTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.logger import logger
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    ProcessOrderException,
)
from app.data.queries.itemQueries import getGoldBaseWithItemId, getItemIdByItemName
from app.schemas.Order import Order, OrderDataPerItem, OrderStatus
from sqlalchemy.exc import SQLAlchemyError


class OrderProcessor:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

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
            logger.debug(f"Making order userId:{userId}")
            orderId:int = await self.addOrder(order,userId)
            orderDataPerItem: List[OrderDataPerItem] = await self.getOrderDataPerItem(
                order,orderId 
            )
            self.comparePrices(orderDataPerItem, order.total)
            await self.insertItemOrderData(orderId, orderDataPerItem)
            logger.debug(f"Orded processed successfully{userId}")
            return orderId
        except ProcessOrderException as e:
            raise e
        except SQLAlchemyError as e:
            logger.error(f"Error in database processing order {e}")
            await self.dbSession.rollback()
            raise ProcessOrderException("Internal server error") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ProcessOrderException("Internal server error") from e

    def creteaRandomDate(self, ref:datetime)->datetime:
        days = random.randint(1,14)
        return ref + timedelta(days=days) 

    async def addOrder(self, order:Order, userId:int)->int:
        try:
            order.status = OrderStatus.PENDING
            order.deliveryDate = self.creteaRandomDate(order.orderDate)
            orderTable: OrderTable = mapOrderToOrderTable(order, userId)
            self.dbSession.add(orderTable)
            await self.dbSession.flush()
            logger.debug(f"Added a new record to order table userId:{userId}, orderId:{orderTable.id}")
            return orderTable.id
        except SQLAlchemyError as e:
            logger.error(f"Error adding order table {e}")
            raise ProcessOrderException(f"Internal server error")

    async def insertItemOrderData(
        self, orderId: int, orderDataPerItem: List[OrderDataPerItem]
    ):
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
        logger.debug(f"Inseting order item relations")
        for data in orderDataPerItem:
            val: dict = {
                "order_id": orderId,
                "item_id": data.itemId,
                "quantity": data.quantity,
            }
            try:
                ins = insert(OrderItemAssociation).values(**val)
                await self.dbSession.execute(ins)
            except SQLAlchemyError as e:
                logger.error(f"Error adding order item association data: {val}, {e}")
                raise ProcessOrderException("Internal server error")
        logger.debug(f"Inserted {len(orderDataPerItem)} order item relations")

    async def getOrderDataPerItem(
        self, order: Order, orderTableId
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
            itemId: int | None = await getItemIdByItemName(self.dbSession, itemName)
            if itemId is None:
                logger.error(f"Error getting the id item {itemName}, id is None")
                raise InvalidItemException(f"Item {itemName} is not in the database")
            amountOfItemInOrder: int = len(
                [e for e in order.itemNames if e == itemName]
            )
            baseCostOfItem: int | None = await getGoldBaseWithItemId(
                self.dbSession, itemId
            )
            if baseCostOfItem is None:
                logger.error(f"Error getting the base cost of item {itemName}, is None")
                raise InvalidItemException(
                    f"Could not find the base cost of item {itemName}"
                )
            total = int(amountOfItemInOrder * baseCostOfItem)
            data: OrderDataPerItem = OrderDataPerItem(
                itemId=itemId,
                orderId=orderTableId,
                quantity=amountOfItemInOrder,
                total=total,
            )
            orderDataPerItem.append(data)
        return orderDataPerItem

    def comparePrices(
        self, orderDataPerItem: List[OrderDataPerItem], orderPrice
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
            logger.error(
                f"Total sent by the client is different than computed on the server, total on server {totalPrice}, on client {orderPrice}"
            )
            raise DifferentTotal(
                orderPrice, totalPrice, "Total in order is not correct"
            )
