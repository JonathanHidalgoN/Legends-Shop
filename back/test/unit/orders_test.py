import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    NotEnoughGoldException,
    ProcessOrderException,
    UserIdNotFound,
)
from app.routes.auth import getUserIdFromName
from staticData import STATIC_DATA_ORDER1, STATIC_DATA_ORDER2, STATIC_ORDER_DATA_DICT


client = TestClient(app)


async def fake_getUserIdFromName() -> int:
    return 1


app.dependency_overrides[getUserIdFromName] = fake_getUserIdFromName


@pytest.mark.asyncio
async def test_order_success():
    """Test successful order creation."""

    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(return_value=STATIC_ORDER_DATA_DICT["id"]),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)
        assert response.status_code == 200
        assert response.json() == STATIC_ORDER_DATA_DICT["id"]


@pytest.mark.asyncio
async def test_order_invalid_item():
    """Test order with invalid item."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(side_effect=InvalidItemException("Invalid item: invalid_item")),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_order_different_total():
    """Test order with different total than expected."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(
            side_effect=DifferentTotal(
                150, 200, "Total mismatch: expected 200, got 150"
            )
        ),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_order_not_enough_gold():
    """Test order with not enough gold."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(
            side_effect=NotEnoughGoldException("Not enough gold: 100, required 200")
        ),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_order_user_not_found():
    """Test order with user not found."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(
            side_effect=UserIdNotFound(
                STATIC_ORDER_DATA_DICT["userName"], "User not found: 1"
            )
        ),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_order_process_error():
    """Test order with process error."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.makeOrder",
        new=AsyncMock(side_effect=ProcessOrderException("Error processing order")),
    ):
        response = client.post("/orders/order", json=STATIC_ORDER_DATA_DICT)

        assert response.status_code == 500
        assert "Error processing order" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_order_history_success():
    """Test successful retrieval of order history."""
    mock_orders = [STATIC_DATA_ORDER1, STATIC_DATA_ORDER2]

    with patch(
        "app.orders.OrderProcessor.OrderProcessor.getOrderHistory",
        new=AsyncMock(return_value=mock_orders),
    ):
        response = client.get("/orders/order_history")

        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 2
        assert orders[0]["id"] == STATIC_DATA_ORDER1.id
        assert orders[1]["id"] == STATIC_DATA_ORDER2.id


@pytest.mark.asyncio
async def test_get_order_history_error():
    """Test error handling when retrieving order history fails."""
    with patch(
        "app.orders.OrderProcessor.OrderProcessor.getOrderHistory",
        new=AsyncMock(
            side_effect=ProcessOrderException("Error retrieving order history")
        ),
    ):
        response = client.get("/orders/order_history")

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_cancel_order_success():
    """Test successful order cancellation."""
    order_id = 1

    with patch(
        "app.orders.OrderProcessor.OrderProcessor.cancelOrder",
        new=AsyncMock(return_value=None),
    ):
        response = client.put(f"/orders/cancel_order/{order_id}")

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_order_process_error():
    """Test error handling when canceling order fails."""
    order_id = 1

    with patch(
        "app.orders.OrderProcessor.OrderProcessor.cancelOrder",
        new=AsyncMock(
            side_effect=ProcessOrderException("Cannot cancel order: already delivered")
        ),
    ):
        response = client.put(f"/orders/cancel_order/{order_id}")

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_order_unexpected_error():
    """Test handling of unexpected errors when canceling order."""
    order_id = 1

    with patch(
        "app.orders.OrderProcessor.OrderProcessor.cancelOrder",
        new=AsyncMock(side_effect=Exception("Unexpected database error")),
    ):
        response = client.put(f"/orders/cancel_order/{order_id}")

        assert response.status_code == 500
