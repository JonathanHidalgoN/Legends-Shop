import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.OrderProcessor import OrderProcessor
from app.schemas.Order import OrderDataPerItem, OrderStatus
from app.customExceptions import ProcessOrderException
from staticData import STATIC_DATA_ORDER1, STATIC_DATA_ORDER2


@pytest.fixture
def processor() -> OrderProcessor:
    mockSession = MagicMock(spec=AsyncSession)
    processor = OrderProcessor(mockSession)
    return processor

@pytest.mark.asyncio
async def test_addOrder_success(processor):
    dummyOrder = STATIC_DATA_ORDER1
    userId = 123
    expectedOrderId = 456

    deliveryDate = datetime(2025, 1, 2)
    processor.creteaRandomDate = MagicMock(return_value=deliveryDate)

    addMock = AsyncMock(return_value=None)
    flushMock = AsyncMock(return_value=None)
    flushMock.side_effect = lambda: setattr(addMock.call_args[0][0], "id", expectedOrderId)

    with patch.object(processor.dbSession, "add", new=addMock):
        with patch.object(processor.dbSession, "flush", new=flushMock):
            result = await processor.addOrder(dummyOrder, userId)
            assert dummyOrder.status == OrderStatus.PENDING
            assert dummyOrder.deliveryDate == deliveryDate
            assert result == expectedOrderId

@pytest.mark.asyncio
async def test_addOrder_failure(processor):
    dummyOrder = STATIC_DATA_ORDER1
    userId = 123
    fixed_delivery_date = datetime(2023, 1, 2)
    processor.creteaRandomDate = MagicMock(return_value=fixed_delivery_date)
    flushMock = AsyncMock(return_value=None)
    addMock = AsyncMock(return_value=None)
    flushMock = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with patch.object(processor.dbSession, "add", new=addMock):
        with patch.object(processor.dbSession, "flush", new=flushMock):
            with pytest.raises(ProcessOrderException):
                await processor.addOrder(dummyOrder, userId)


@pytest.mark.asyncio
async def test_insertItemOrderData_success(processor):
    orderId = 101
    orderDataPerItem = [
        OrderDataPerItem(itemId=1, quantity=2, total=100, orderId=1),
        OrderDataPerItem(itemId=2, quantity=3, total=200, orderId=2)
    ]
    with patch.object(processor.dbSession, "execute", return_value=None):
        await processor.insertItemOrderData(orderId, orderDataPerItem)
        assert processor.dbSession.execute.call_count == len(orderDataPerItem)

@pytest.mark.asyncio
async def test_insertItemOrderData_failure(processor):
    orderId = 101
    orderDataPerItem = [
        OrderDataPerItem(itemId=1, quantity=2, total=100, orderId=1),
    ]
    processor.dbSession.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    with patch.object(processor.dbSession, "execute", autospec=True,
                      side_effect = SQLAlchemyError("DB error")):
        with pytest.raises(ProcessOrderException, match="Internal server error"):
            await processor.insertItemOrderData(orderId, orderDataPerItem)

@pytest.mark.asyncio
async def test_getOrderDataPerItem_success(processor):
    dummyOrder = STATIC_DATA_ORDER2     
    orderTableId = 101
    expecteItemId1 = 1
    expecteItemId2 = 2
    expectedPriceItem1 = dummyOrder.total - 1
    expectedPriceItem2 = 1
    
    #This functions need to have same args as the ones they are mocking
    def getItemIdFunctionMock(dbSession, itemName):
        if itemName == "item1":
            return expecteItemId1 
        else:
            return expecteItemId2 
    def getBaseGoldFunctionMock(dbSession, itemId):
        if itemId == 1:
            return expectedPriceItem1
        else:
            return expectedPriceItem2 
    with patch("app.orders.OrderProcessor.getItemIdByItemName", autospec=True, 
                side_effect = getItemIdFunctionMock), \
        patch("app.orders.OrderProcessor.getGoldBaseWithItemId", autospec=True, 
              side_effect=getBaseGoldFunctionMock):
        result = await processor.getOrderDataPerItem(dummyOrder, orderTableId)
        assert len(result) == 2
        item1Data = next((data for data in result if data.itemId == expecteItemId1), None)
        item2Data = next((data for data in result if data.itemId == expecteItemId2), None)
        assert item1Data is not None, "Item1 data should be present"
        assert item2Data is not None, "Item2 data should be present"
        assert item1Data.quantity == 2 
        assert item1Data.total == expectedPriceItem1 * 2
        assert item2Data.quantity == 1
        assert item2Data.total == expectedPriceItem2 
        for data in result:
            assert data.orderId == orderTableId

@pytest.mark.asyncio
async def test_getOrderDataPerItem_itemIdNone(processor: OrderProcessor):
    dummyOrder = STATIC_DATA_ORDER2     
    orderTableId = 101
    itemIdMock = AsyncMock(return_value=None)
    with patch("app.orders.OrderProcessor.getItemIdByItemName", new=itemIdMock):
        with pytest.raises(ProcessOrderException):
            await processor.getOrderDataPerItem(dummyOrder, orderTableId)
