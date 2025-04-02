import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.OrderProcessor import OrderProcessor
from app.schemas.Order import OrderDataPerItem, OrderStatus
from app.customExceptions import (
    DifferentTotal,
    NotEnoughGoldException,
    ProcessOrderException,
    InvalidItemException,
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
    deliveryDate = date(2025, 1, 8)

    # Mock determineDeliveryDate
    processor.determineDeliveryDate = AsyncMock(return_value=deliveryDate)
    
    # Mock database operations
    addMock = MagicMock(return_value=None)
    flushMock = AsyncMock(return_value=None)
    flushMock.side_effect = lambda: setattr(
        addMock.call_args[0][0], "id", expectedOrderId
    )

    with patch.object(processor.dbSession, "add", new=addMock):
        with patch.object(processor.dbSession, "flush", new=flushMock):
            result = await processor.addOrder(dummyOrder, userId)
            assert dummyOrder.status == OrderStatus.PENDING
            assert dummyOrder.deliveryDate == datetime.combine(deliveryDate, datetime.min.time())
            assert result == expectedOrderId


@pytest.mark.asyncio
async def test_addOrder_failure(processor):
    dummyOrder = STATIC_DATA_ORDER1
    userId = 123
    deliveryDate = date(2025, 1, 8)

    # Mock determineDeliveryDate
    processor.determineDeliveryDate = AsyncMock(return_value=deliveryDate)

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
    expectedItemId1 = 1
    expectedItemId2 = 2
    expectedPriceItem1 = 100
    expectedPriceItem2 = 100

    # Mock the dependencies
    async def getItemIdMock(dbSession, itemName):
        if itemName == "item1":
            return expectedItemId1
        else:
            return expectedItemId2

    async def getBaseGoldMock(dbSession, itemId):
        if itemId == expectedItemId1:
            return expectedPriceItem1
        else:
            return expectedPriceItem2

    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        new=AsyncMock(side_effect=getItemIdMock),
    ), patch(
        "app.orders.OrderProcessor.getGoldBaseWithItemId",
        new=AsyncMock(side_effect=getBaseGoldMock),
    ):
        result = await processor.getOrderDataPerItem(dummyOrder, orderTableId)
        assert len(result) == 2
        item1Data = next(
            (data for data in result if data.itemId == expectedItemId1), None
        )
        item2Data = next(
            (data for data in result if data.itemId == expectedItemId2), None
        )
        assert item1Data is not None, "Item1 data should be present"
        assert item2Data is not None, "Item2 data should be present"
        assert item1Data.quantity == 1  # One item1 in the order
        assert item1Data.total == expectedPriceItem1
        assert item2Data.quantity == 1  # One item2 in the order
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


@pytest.mark.asyncio
async def test_getOrderHistory_success(processor):
    userId = 1
    fakeOrders = [STATIC_DATA_ORDER1, STATIC_DATA_ORDER2]

    with patch(
        "app.orders.OrderProcessor.getOrderHistoryByUserId",
        new=AsyncMock(return_value=fakeOrders),
    ):
        result = await processor.getOrderHistory(userId)
        assert result == fakeOrders


@pytest.mark.asyncio
async def test_getOrderHistory_sqlalchemy_error(processor):
    userId = 1

    with patch(
        "app.orders.OrderProcessor.getOrderHistoryByUserId",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ProcessOrderException):
            await processor.getOrderHistory(userId)


@pytest.mark.asyncio
async def test_determineDeliveryDate_success(processor):
    # Setup test data
    dummyOrder = STATIC_DATA_ORDER1
    itemId = 1
    locationId = 1
    orderDate = date(2025, 1, 1)
    expectedDeliveryDate = date(2025, 1, 8)  # 7 days after order date

    # Mock the dependencies
    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        new=AsyncMock(return_value=itemId),
    ), patch(
        "app.orders.OrderProcessor.getDeliveryDateForItemAndLocation",
        new=AsyncMock(return_value=expectedDeliveryDate),
    ):
        result = await processor.determineDeliveryDate(dummyOrder)
        assert result == expectedDeliveryDate


@pytest.mark.asyncio
async def test_determineDeliveryDate_multiple_items(processor):
    # Setup test data
    dummyOrder = STATIC_DATA_ORDER2  # Order with multiple items
    itemId1 = 1
    itemId2 = 2
    locationId = 1
    orderDate = date(2025, 1, 1)
    deliveryDate1 = date(2025, 1, 5)  # 4 days after order date
    deliveryDate2 = date(2025, 1, 8)  # 7 days after order date

    # Mock the dependencies
    def getItemIdMock(dbSession, itemName):
        if itemName == "item1":
            return itemId1
        else:
            return itemId2

    def getDeliveryDateMock(dbSession, itemId, locationId, orderDate):
        if itemId == itemId1:
            return deliveryDate1
        else:
            return deliveryDate2

    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        new=AsyncMock(side_effect=getItemIdMock),
    ), patch(
        "app.orders.OrderProcessor.getDeliveryDateForItemAndLocation",
        new=AsyncMock(side_effect=getDeliveryDateMock),
    ):
        result = await processor.determineDeliveryDate(dummyOrder)
        assert result == deliveryDate2  # Should return the latest delivery date


@pytest.mark.asyncio
async def test_determineDeliveryDate_item_not_found(processor):
    # Setup test data
    dummyOrder = STATIC_DATA_ORDER1
    itemId = None  # Item not found

    # Mock the dependencies
    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        new=AsyncMock(return_value=itemId),
    ):
        with pytest.raises(InvalidItemException) as exc_info:
            await processor.determineDeliveryDate(dummyOrder)
        assert "Item" in str(exc_info.value)


@pytest.mark.asyncio
async def test_determineDeliveryDate_no_delivery_date(processor):
    # Setup test data
    dummyOrder = STATIC_DATA_ORDER1
    itemId = 1
    locationId = 1
    deliveryDate = None  # No delivery date found

    # Mock the dependencies
    with patch(
        "app.orders.OrderProcessor.getItemIdByItemName",
        new=AsyncMock(return_value=itemId),
    ), patch(
        "app.orders.OrderProcessor.getDeliveryDateForItemAndLocation",
        new=AsyncMock(return_value=deliveryDate),
    ):
        with pytest.raises(ProcessOrderException) as exc_info:
            await processor.determineDeliveryDate(dummyOrder)
        assert "No delivery date found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_determineDeliveryDate_no_items(processor):
    # Setup test data
    dummyOrder = STATIC_DATA_ORDER1
    dummyOrder.itemNames = []  # Empty order

    # Test with empty order
    with pytest.raises(ProcessOrderException) as exc_info:
        await processor.determineDeliveryDate(dummyOrder)
    assert "Could not determine delivery date" in str(exc_info.value)
