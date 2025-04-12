import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from staticData import (
    STATIC_DATA_ITEM1,
    STATIC_DATA_ITEM2,
    STATIC_DATA_TAGS,
    STATIC_DATA_EFFECTS,
)


client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_items_success():
    """Test successful retrieval of all items."""
    mock_items = [STATIC_DATA_ITEM1, STATIC_DATA_ITEM2]
    with patch(
        "app.routes.items.getAllItemTableRowsAnMapToItems",
        new=AsyncMock(return_value=mock_items),
    ):
        with patch(
            "app.routes.items.staticDataValidation",
            new=AsyncMock(return_value=True),
        ):
            response = client.get("/items/all")

            assert response.status_code == 200
            items = response.json()
            assert len(items) == 2
            assert items[0]["name"] == STATIC_DATA_ITEM1.name
            assert items[1]["name"] == STATIC_DATA_ITEM2.name


@pytest.mark.asyncio
async def test_get_all_items_error():
    """Test error handling when retrieving all items fails."""
    with patch(
        "app.routes.items.getAllItemTableRowsAnMapToItems",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        with patch(
            "app.routes.items.staticDataValidation",
            new=AsyncMock(return_value=True),
        ):
            response = client.get("/items/all")
            assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_some_items_success():
    """Test successful retrieval of some items."""
    mock_items = [STATIC_DATA_ITEM1]
    with patch(
        "app.routes.items.getSomeItemTableRowsAnMapToItems",
        new=AsyncMock(return_value=mock_items),
    ):
        with patch(
            "app.routes.items.staticDataValidation",
            new=AsyncMock(return_value=True),
        ):
            response = client.get("/items/some")

            assert response.status_code == 200
            items = response.json()
            assert len(items) == 1
            assert items[0]["name"] == STATIC_DATA_ITEM1.name


@pytest.mark.asyncio
async def test_get_some_items_error():
    """Test error handling when retrieving some items fails."""
    with patch(
        "app.routes.items.getSomeItemTableRowsAnMapToItems",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        with patch(
            "app.routes.items.staticDataValidation",
            new=AsyncMock(return_value=True),
        ):
            response = client.get("/items/some")

            assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_unique_tags_success():
    """Test successful retrieval of unique tags."""
    with patch(
        "app.routes.items.getAllTagsTableNames",
        new=AsyncMock(return_value=STATIC_DATA_TAGS),
    ):
        response = client.get("/items/uniqueTags")

        assert response.status_code == 200
        tags = response.json()
        assert len(tags) == len(STATIC_DATA_TAGS)
        assert all(tag in STATIC_DATA_TAGS for tag in tags)


@pytest.mark.asyncio
async def test_get_unique_tags_error():
    """Test error handling when retrieving unique tags fails."""
    with patch(
        "app.routes.items.getAllTagsTableNames",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        response = client.get("/items/uniqueTags")

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_item_names_success():
    """Test successful retrieval of item names."""
    mock_item_names = {STATIC_DATA_ITEM1.name, STATIC_DATA_ITEM2.name}
    with patch(
        "app.routes.items.getAllItemNames", new=AsyncMock(return_value=mock_item_names)
    ):
        response = client.get("/items/item_names")

        assert response.status_code == 200
        item_names = response.json()
        assert len(item_names) == len(mock_item_names)
        assert all(name in mock_item_names for name in item_names)


@pytest.mark.asyncio
async def test_get_item_names_error():
    """Test error handling when retrieving item names fails."""
    with patch(
        "app.routes.items.getAllItemNames",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        response = client.get("/items/item_names")

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_unique_effects_success():
    """Test successful retrieval of unique effects."""
    with patch(
        "app.routes.items.getAllEffectsTableName",
        new=AsyncMock(return_value=STATIC_DATA_EFFECTS),
    ):
        response = client.get("/items/unique_effects")

        assert response.status_code == 200
        effects = response.json()
        assert len(effects) == len(STATIC_DATA_EFFECTS)
        assert all(effect in STATIC_DATA_EFFECTS for effect in effects)


@pytest.mark.asyncio
async def test_get_unique_effects_error():
    """Test error handling when retrieving unique effects fails."""
    with patch(
        "app.routes.items.getAllEffectsTableName",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        response = client.get("/items/unique_effects")

        assert response.status_code == 500
