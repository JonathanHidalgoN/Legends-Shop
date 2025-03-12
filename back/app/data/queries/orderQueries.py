from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.schemas.Order import Order


async def getOrderHistoryQuery(asyncSession: AsyncSession, userId: int,
    orderStatus: str = "ALL",
    minOrderDate: Optional[date] = None,
    maxOrderDate: Optional[date] = None,
    minDeliveryDate: Optional[date] = None,
    maxDeliveryDate: Optional[date] = None,
    sortField: Optional[str] = None,
    sortOrder: Optional[str] = None,
    filterItemNames: Optional[List[str]] = None 

                               ) -> List[Order]:
    """
        Retrieves a filtered and sorted list of orders for a given user.

        This function dynamically builds and executes a SQL query using the provided asynchronous
        session. It filters the order history based on the user's ID and optional criteria such as 
        order status, order date range, delivery date range, sorting preferences, and a list of item 
        names to filter by. The query joins multiple tables to retrieve relevant order details.

        Args:
            asyncSession (AsyncSession): The SQLAlchemy asynchronous session to execute the query.
            userId (int): The ID of the user whose order history is being queried.
            orderStatus (str, optional): The order status filter. Defaults to "ALL" for no filtering.
            minOrderDate (Optional[date], optional): The earliest order date (inclusive) to include.
            maxOrderDate (Optional[date], optional): The latest order date (inclusive) to include.
            minDeliveryDate (Optional[date], optional): The earliest delivery date (inclusive) to include.
            maxDeliveryDate (Optional[date], optional): The latest delivery date (inclusive) to include.
            sortField (Optional[str], optional): The field by which to sort the orders. For example, 'price',
                'orderDate', 'deliveryDate', or 'quantity'. If not provided, a default sort may be applied.
            sortOrder (Optional[str], optional): The sort order; typically "asc" for ascending or "desc" 
                for descending. Defaults to ascending if not provided.
            filterItemNames (Optional[List[str]], optional): A list of item names to filter orders by.
                Only orders containing these items will be returned. If omitted, no filtering on item names occurs.

        Returns:
            List[Order]: A list of Order objects matching the specified filters and sorting criteria.

        Raises:
            SQLAlchemyError: If an error occurs while executing the database query.
            Exception: For any other errors encountered during query construction or execution.
        """
    query = (
        select(
            OrderTable.id,
            OrderTable.total,
            OrderTable.order_date,
            OrderTable.delivery_date,
            OrderTable.status,
            ItemTable.name,
            UserTable.userName,
            OrderItemAssociation.c.quantity,
        )
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(UserTable, UserTable.id == userId)
        .where(OrderTable.user_id == userId)
    )

    filters = []
    
    if orderStatus != "ALL":
        filters.append(OrderTable.status == orderStatus)
    if minOrderDate:
        filters.append(OrderTable.order_date >= minOrderDate)
    if maxOrderDate:
        filters.append(OrderTable.order_date <= maxOrderDate)
    if minDeliveryDate:
        filters.append(OrderTable.delivery_date >= minDeliveryDate)
    if maxDeliveryDate:
        filters.append(OrderTable.delivery_date <= maxDeliveryDate)
    if filterItemNames:
        filters.append(ItemTable.name.in_(filterItemNames))

    if filters:
        query = query.where(*filters)

    if sortField:
        if sortField == "price":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.total.desc())
            else:
                query = query.order_by(OrderTable.total.asc())
        elif sortField == "orderDate":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.order_date.desc())
            else:
                query = query.order_by(OrderTable.order_date.asc())
        elif sortField == "deliveryDate":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.delivery_date.desc())
            else:
                query = query.order_by(OrderTable.delivery_date.asc())
        elif sortField == "quantity":
            if sortOrder == "desc":
                query = query.order_by(OrderItemAssociation.c.quantity.desc())
            else:
                query = query.order_by(OrderItemAssociation.c.quantity.asc())

    result = await asyncSession.execute(query)

    rows = result.all()
    orders_dict = {}
    for (
        order_id,
        total,
        order_date,
        delivery_date,
        status,
        item_name,
        user_name,
        quantity
    ) in rows:
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "id": order_id,
                "itemNames": [item_name for _ in range(quantity)],
                "userName": user_name,
                "total": total,
                "orderDate": order_date,
                "deliveryDate": delivery_date,
                "status": status,
            }
        else:
            orders_dict[order_id]["itemNames"].append(item_name)
    return [Order(**order_data) for order_data in orders_dict.values()]


async def getOrderWithId(asyncSession: AsyncSession, orderId: int) -> None:
    """
    Retrieve a single order record by its ID.

    This asynchronous function executes a database query using the provided 
    asynchronous session to fetch an order record from the OrderTable that 
    matches the specified orderId. It returns the first matching order record, 
    or None if no such record exists.

    Args:
        asyncSession (AsyncSession): The asynchronous SQLAlchemy session to execute the query.
        orderId (int): The unique identifier of the order to be retrieved.

    Returns:
        Optional[OrderTable]: The first OrderTable record that matches the orderId, 
        or None if no record is found.
    """
    result = await asyncSession.execute(
        select(OrderTable).where(OrderTable.id == orderId)
    )
    return result.scalars().first()
