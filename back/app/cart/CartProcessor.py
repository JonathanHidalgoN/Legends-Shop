from typing import List

from sqlalchemy.exc import SQLAlchemyError
from app.data.models.CartTable import CartTable
from app.schemas.Order import CartItem, CartStatus
from app.customExceptions import CartProcessorException
from app.data.queries.cartQueries import getAddedCartItemsWithUserId
from app.data.mappers import mapCartTableToCartItem
from app.data.queries.cartQueries import changeCartItemStatusToDeleted
from app.logger import logMethod


class CartProceesor:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    @logMethod
    async def addItemToCar(self, carItem: CartItem, userId: int) -> CartItem:
        try:
            cartTable: CartTable = self.createCartTableWithItemIdUserId(
                carItem.itemId, userId
            )
            self.dbSession.add(cartTable)
            await self.dbSession.flush()
            carItem.id = cartTable.id
            carItem.status = cartTable.status
            await self.dbSession.commit()
            return carItem
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise CartProcessorException(f"Error adding items to car") from e

    @logMethod
    def createCartTableWithItemIdUserId(self, itemId: int, userId: int) -> CartTable:
        cartTable: CartTable = CartTable()
        cartTable.item_id = itemId
        cartTable.user_id = userId
        cartTable.status = CartStatus.ADDED
        return cartTable

    @logMethod
    async def addItemsToCar(
        self, carItems: List[CartItem], userId: int
    ) -> List[CartItem]:
        try:
            returnCarItems: List[CartItem] = []
            for carItem in carItems:
                cartTable: CartTable = self.createCartTableWithItemIdUserId(
                    carItem.itemId, userId
                )
                self.dbSession.add(cartTable)
                await self.dbSession.flush()
                carItem.id = cartTable.id
                returnCarItems.append(carItem)
            await self.dbSession.commit()
            return returnCarItems
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise CartProcessorException(f"Error adding items to cart") from e

    @logMethod
    async def getAddedUserCart(self, userId: int) -> List[CartItem]:
        try:
            userCartTables: List[CartTable] = await getAddedCartItemsWithUserId(
                self.dbSession, userId
            )
            userCart: List[CartItem] = [
                mapCartTableToCartItem(cartTable) for cartTable in userCartTables
            ]
            return userCart
        except SQLAlchemyError as e:
            raise CartProcessorException(f"Error getting cart added cart items") from e

    @logMethod
    async def deleteCartItem(self, userId: int, cartId: int) -> None:
        try:
            await changeCartItemStatusToDeleted(self.dbSession, userId, cartId)
        except SQLAlchemyError as e:
            raise CartProcessorException(
                f"Error chaning cart item status to deleted"
            ) from e
