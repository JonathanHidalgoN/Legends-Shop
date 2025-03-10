import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.OrderProcessor import OrderProcessor
from app.schemas.Order import OrderDataPerItem, OrderStatus
from app.customExceptions import ProcessOrderException
from staticData import STATIC_DATA_ORDER1


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
    executeMock = AsyncMock(side_effect = SQLAlchemyError("DB error"))
    with patch.object(processor.dbSession, "execute", new = executeMock):
        with pytest.raises(ProcessOrderException, match="Internal server error"):
            await processor.insertItemOrderData(orderId, orderDataPerItem)
