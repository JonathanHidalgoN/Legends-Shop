import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.OrderProcessor import OrderProcessor
from app.schemas.Order import OrderDataPerItem, OrderStatus
from app.customExceptions import (
    DifferentTotal,
    NotEnoughGoldException,
    ProcessOrderException,
)
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
    addMock = MagicMock(return_value=None)
    flushMock = AsyncMock(return_value=None)
    flushMock.side_effect = lambda: setattr(
        addMock.call_args[0][0], "id", expectedOrderId
    )

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
    with patch.object(processor.dbSession, "add", return_value=None):
        with patch.object(
            processor.dbSession, "flush", side_effect=SQLAlchemyError("DB error")
        ):
            with pytest.raises(ProcessOrderException):
                await processor.addOrder(dummyOrder, userId)


@pytest.mark.asyncio
async def test_insertItemOrderData_success(processor):
    orderId = 101
    orderDataPerItem = [
        OrderDataPerItem(itemId=1, quantity=2, total=100, orderId=1),
        OrderDataPerItem(itemId=2, quantity=3, total=200, orderId=2),
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
    with patch.object(
        processor.dbSession, "execute", side_effect=SQLAlchemyError("DB error")
    ):
        with pytest.raises(ProcessOrderException):
            await processor.insertItemOrderData(orderId, orderDataPerItem)


@pytest.mark.asyncio
async def test_getOrderDataPerItem_success(processor):
    dummyOrder = STATIC_DATA_ORDER2
    orderTableId = 101
    expecteItemId1 = 1
    expecteItemId2 = 2
    expectedPriceItem1 = dummyOrder.total - 1
    expectedPriceItem2 = 1

    # This functions need to have same args as the ones they are mocking
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

    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        autospec=True,
        side_effect=getItemIdFunctionMock,
    ), patch(
        "app.orders.OrderProcessor.getGoldBaseWithItemId",
        autospec=True,
        side_effect=getBaseGoldFunctionMock,
    ):
        result = await processor.getOrderDataPerItem(dummyOrder, orderTableId)
        assert len(result) == 2
        item1Data = next(
            (data for data in result if data.itemId == expecteItemId1), None
        )
        item2Data = next(
            (data for data in result if data.itemId == expecteItemId2), None
        )
        assert item1Data is not None, "Item1 data should be present"
        assert item2Data is not None, "Item2 data should be present"
        assert item1Data.quantity == 2
        assert item1Data.total == expectedPriceItem1 * 2
        assert item2Data.quantity == 1
        assert item2Data.total == expectedPriceItem2
        for data in result:
            assert data.orderId == orderTableId


@pytest.mark.asyncio
async def test_getOrderDataPerItem_failure_itemIdNone(processor: OrderProcessor):
    dummyOrder = STATIC_DATA_ORDER2
    orderTableId = 101
    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        autospec=True,
        return_value=None,
    ):
        with pytest.raises(ProcessOrderException):
            await processor.getOrderDataPerItem(dummyOrder, orderTableId)


@pytest.mark.asyncio
async def test_getOrderDataPerItem_failure_baseCostNone(processor: OrderProcessor):
    dummyOrder = STATIC_DATA_ORDER2
    orderTableId = 101
    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName", new=AsyncMock(return_value=1)
    ):
        with patch(
            "app.orders.OrderProcessor.getGoldBaseWithItemId",
            new=AsyncMock(return_value=None),
        ):
            with pytest.raises(ProcessOrderException):
                await processor.getOrderDataPerItem(dummyOrder, orderTableId)


@pytest.mark.parametrize(
    "orderData, providedTotal",
    [
        (
            [
                OrderDataPerItem(itemId=1, orderId=101, quantity=1, total=40),
                OrderDataPerItem(itemId=2, orderId=101, quantity=1, total=60),
            ],
            100,
        ),
        (
            [
                OrderDataPerItem(itemId=1, orderId=101, quantity=2, total=80),
                OrderDataPerItem(itemId=2, orderId=101, quantity=1, total=60),
            ],
            140,
        ),
        (
            [
                OrderDataPerItem(itemId=1, orderId=101, quantity=1, total=10),
                OrderDataPerItem(itemId=2, orderId=101, quantity=1, total=20),
                OrderDataPerItem(itemId=3, orderId=101, quantity=1, total=30),
            ],
            60,
        ),
    ],
)
def test_comparePrices_success(processor, orderData, providedTotal):
    processor.comparePrices(orderData, providedTotal)


def test_comparePrices_failure(processor):
    item1 = OrderDataPerItem(itemId=1, orderId=101, quantity=1, total=40)
    item2 = OrderDataPerItem(itemId=2, orderId=101, quantity=1, total=60)
    orderData = [item1, item2]
    with pytest.raises(DifferentTotal):
        processor.comparePrices(orderData, 110)


@pytest.mark.asyncio
async def test_computeUserChange_success(processor):
    userId = 1
    total = 500
    currentGold = 1000
    expectedLeft = currentGold - total

    with patch(
        "app.orders.OrderProcessor.getCurrentUserGoldWithUserId",
        new=AsyncMock(return_value=currentGold),
    ):
        left = await processor.computeUserChange(userId, total)
        assert left == expectedLeft


@pytest.mark.asyncio
async def test_computeUserChange_no_gold(processor):
    userId = 1
    total = 500

    with patch(
        "app.orders.OrderProcessor.getCurrentUserGoldWithUserId",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(ProcessOrderException):
            await processor.computeUserChange(userId, total)


@pytest.mark.asyncio
async def test_computeUserChange_negative_gold(processor):
    userId = 1
    total = 500
    negativeGold = -100

    with patch(
        "app.orders.OrderProcessor.getCurrentUserGoldWithUserId",
        new=AsyncMock(return_value=negativeGold),
    ):
        with pytest.raises(ProcessOrderException):
            await processor.computeUserChange(userId, total)


@pytest.mark.asyncio
async def test_computeUserChange_not_enough_gold(processor):
    userId = 1
    total = 500
    currentGold = 400

    with patch(
        "app.orders.OrderProcessor.getCurrentUserGoldWithUserId",
        new=AsyncMock(return_value=currentGold),
    ):
        with pytest.raises(NotEnoughGoldException):
            await processor.computeUserChange(userId, total)


@pytest.mark.asyncio
async def test_updateTotalUserSpendGold_success(processor):
    userId = 1
    toAdd = 100
    initialSpend = 500
    expectedNewSpend = initialSpend + toAdd

    with patch(
        "app.orders.OrderProcessor.getTotalSpendUserGoldWithUserId",
        new=AsyncMock(return_value=initialSpend),
    ):
        with patch(
            "app.orders.OrderProcessor.updateUserSpendGoldWithUserId",
            new=AsyncMock(return_value=None),
        ) as updateMock:
            await processor.updateTotalUserSpendGold(userId, toAdd)
            updateMock.assert_awaited_once_with(
                processor.dbSession, userId, expectedNewSpend
            )


@pytest.mark.asyncio
async def test_updateTotalUserSpendGold_no_spend_gold(processor):
    userId = 1
    toAdd = 100

    with patch(
        "app.orders.OrderProcessor.getTotalSpendUserGoldWithUserId",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(ProcessOrderException):
            await processor.updateTotalUserSpendGold(userId, toAdd)


@pytest.mark.asyncio
async def test_updateTotalUserSpendGold_sqlalchemy_error_on_get(processor):
    userId = 1
    toAdd = 100

    with patch(
        "app.orders.OrderProcessor.getTotalSpendUserGoldWithUserId",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ProcessOrderException):
            await processor.updateTotalUserSpendGold(userId, toAdd)


@pytest.mark.asyncio
async def test_updateTotalUserSpendGold_sqlalchemy_error_on_update(processor):
    userId = 1
    toAdd = 100
    initialSpend = 500

    with patch(
        "app.orders.OrderProcessor.getTotalSpendUserGoldWithUserId",
        new=AsyncMock(return_value=initialSpend),
    ):
        with patch(
            "app.orders.OrderProcessor.updateUserSpendGoldWithUserId",
            new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
        ):
            with pytest.raises(ProcessOrderException):
                await processor.updateTotalUserSpendGold(userId, toAdd)
