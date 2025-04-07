import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import CartProcessorException
from app.routes.auth import getUserIdFromName
from staticData import STATIC_CART_ITEM1, STATIC_CART_ITEM2

STATIC_CART_ITEMS = [STATIC_CART_ITEM1, STATIC_CART_ITEM2]

client = TestClient(app)


async def fake_getUserIdFromName() -> int:
    return 1


app.dependency_overrides[getUserIdFromName] = fake_getUserIdFromName


@pytest.mark.asyncio
async def test_add_item_success():
    """Test successful addition of a single item to cart."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.addItemToCar",
        new=AsyncMock(return_value=STATIC_CART_ITEM1),
    ):
        response = client.post("/cart/add_item", json=STATIC_CART_ITEM1.model_dump())
        assert response.status_code == 200
        assert response.json()["id"] == STATIC_CART_ITEM1.id
        assert response.json()["itemId"] == STATIC_CART_ITEM1.itemId
        assert response.json()["status"] == STATIC_CART_ITEM1.status


@pytest.mark.asyncio
async def test_add_item_error():
    """Test error handling when adding an item to cart fails."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.addItemToCar",
        new=AsyncMock(side_effect=CartProcessorException("Error adding item to cart")),
    ):
        response = client.post("/cart/add_item", json=STATIC_CART_ITEM1.model_dump())
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_add_items_success():
    """Test successful addition of multiple items to cart."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.addItemsToCar",
        new=AsyncMock(return_value=STATIC_CART_ITEMS),
    ):
        response = client.post(
            "/cart/add_items", json=[item.model_dump() for item in STATIC_CART_ITEMS]
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == STATIC_CART_ITEM1.id
        assert response.json()[1]["id"] == STATIC_CART_ITEM2.id


@pytest.mark.asyncio
async def test_add_items_error():
    """Test error handling when adding multiple items to cart fails."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.addItemsToCar",
        new=AsyncMock(side_effect=CartProcessorException("Error adding items to cart")),
    ):
        response = client.post(
            "/cart/add_items", json=[item.model_dump() for item in STATIC_CART_ITEMS]
        )
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_added_cart_items_success():
    """Test successful retrieval of user's cart items."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.getAddedUserCart",
        new=AsyncMock(return_value=STATIC_CART_ITEMS),
    ):
        response = client.get("/cart/added_cart_items")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == STATIC_CART_ITEM1.id
        assert response.json()[1]["id"] == STATIC_CART_ITEM2.id


@pytest.mark.asyncio
async def test_get_added_cart_items_error():
    """Test error handling when retrieving user's cart items fails."""
    with patch(
        "app.cart.CartProcessor.CartProceesor.getAddedUserCart",
        new=AsyncMock(side_effect=CartProcessorException("Error getting cart items")),
    ):
        response = client.get("/cart/added_cart_items")
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_delete_cart_item_success():
    """Test successful deletion of a cart item."""
    cart_item_id = 1
    with patch(
        "app.cart.CartProcessor.CartProceesor.deleteCartItem",
        new=AsyncMock(return_value=None),
    ):
        response = client.delete(f"/cart/delete_cart_item/{cart_item_id}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_cart_item_error():
    """Test error handling when deleting a cart item fails."""
    cart_item_id = 1
    with patch(
        "app.cart.CartProcessor.CartProceesor.deleteCartItem",
        new=AsyncMock(side_effect=CartProcessorException("Error deleting cart item")),
    ):
        response = client.delete(f"/cart/delete_cart_item/{cart_item_id}")
        assert response.status_code == 500
