from typing import List

from sqlalchemy.exc import SQLAlchemyError
from app.logger import logger
from app.data.models.CartTable import CartTable
from app.schemas.Order import CartItem, CartStatus
from app.customExceptions import CartProcessorException


class CartProceesor:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    async def addItemToCar(self, carItem:CartItem, userId:int) -> CartItem:
        try:
            logger.debug(f"Adding a new record to car, userId {userId}")
            cartTable:CartTable = self.createCartTableWithItemIdUserId(carItem.itemId, userId) 
            self.dbSession.add(cartTable)
            await self.dbSession.flush()
            carItem.id = cartTable.id
            logger.debug(
                f"Added a new record to order cart table userId:{userId}, orderId:{cartTable.id}"
            )
            await self.dbSession.commit()
            return carItem 
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            logger.error(f"Error adding car item {e}")
            raise CartProcessorException(f"Error adding items to car") from e

    def createCartTableWithItemIdUserId(self, itemId:int, userId:int)->CartTable:
        cartTable:CartTable = CartTable()
        cartTable.item_id = itemId
        cartTable.user_id = userId
        cartTable.status = CartStatus.ADDED
        return cartTable

    async def addItemsToCar(self, carItems:List[CartItem], userId:int) -> List[CartItem]:
        try:
            returnCarItems: List[CartItem] = []
            for carItem in carItems:
                logger.debug(f"Adding a new record to car, userId {userId}")
                cartTable:CartTable = self.createCartTableWithItemIdUserId(carItem.itemId, userId) 
                self.dbSession.add(cartTable)
                await self.dbSession.flush()
                carItem.id = cartTable.id
                returnCarItems.append(carItem)
                logger.debug(
                    f"Added a new record to order cart table userId:{userId}, orderId:{cartTable.id}"
                )
            await self.dbSession.commit()
            return returnCarItems 
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            logger.error(f"Error adding car item {e}")
            raise CartProcessorException(f"Error adding items to car") from e


