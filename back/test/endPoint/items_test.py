import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.schemas.Item import Item
from back.test.staticData import STATIC_DATA_ITEM1, STATIC_DATA_ITEM2


client = TestClient(app)


# Mock the database session
@pytest.fixture
def mock_db_session():
    with patch("app.routes.items.database.getDbSession") as mock:
        mock_session = MagicMock(spec=AsyncSession)
        mock.return_value = mock_session
        yield mock_session


# Test for the /all endpoint
def test_get_all_items_success(mock_db_session):
    # Mock the function that gets all items
    with patch(
        "app.routes.items.getAllItemTableRowsAnMapToItems", new_callable=AsyncMock
    ) as mock_get_all:
        mock_get_all.return_value = [STATIC_DATA_ITEM1, STATIC_DATA_ITEM2]

        # Make the request
        response = client.get("/items/all")

        # Assert response
        assert response.status_code == 200
        assert "items" in response.json()
        assert len(response.json()["items"]) == 2
        assert response.json()["items"][0]["name"] == "Test Item 1"
        assert response.json()["items"][1]["name"] == "Test Item 2"


def test_get_all_items_error(mock_db_session):
    # Mock the function to raise an exception
    with patch(
        "app.routes.items.getAllItemTableRowsAnMapToItems", new_callable=AsyncMock
    ) as mock_get_all:
        mock_get_all.side_effect = Exception("Database error")

        # Make the request
        response = client.get("/items/all")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()


# Test for the /some endpoint
def test_get_some_items_success(mock_db_session):
    # Mock the function that gets some items
    with patch(
        "app.routes.items.getSomeItemTableRowsAnMapToItems", new_callable=AsyncMock
    ) as mock_get_some:
        mock_get_some.return_value = MOCK_ITEMS[:1]  # Return only the first item

        # Make the request
        response = client.get("/items/some")

        # Assert response
        assert response.status_code == 200
        assert "items" in response.json()
        assert len(response.json()["items"]) == 1
        assert response.json()["items"][0]["name"] == "Test Item 1"


def test_get_some_items_error(mock_db_session):
    # Mock the function to raise an exception
    with patch(
        "app.routes.items.getSomeItemTableRowsAnMapToItems", new_callable=AsyncMock
    ) as mock_get_some:
        mock_get_some.side_effect = Exception("Database error")

        # Make the request
        response = client.get("/items/some")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()


# Test for the /uniqueTags endpoint
def test_get_unique_tags_success(mock_db_session):
    # Mock the function that gets all tags
    with patch(
        "app.routes.items.getAllTagsTableNames", new_callable=AsyncMock
    ) as mock_get_tags:
        mock_get_tags.return_value = STATIC_DATA_TAGS

        # Make the request
        response = client.get("/items/uniqueTags")

        # Assert response
        assert response.status_code == 200
        assert "tagNames" in response.json()
        assert len(response.json()["tagNames"]) == 3
        assert "tag1" in response.json()["tagNames"]
        assert "tag2" in response.json()["tagNames"]
        assert "tag3" in response.json()["tagNames"]


def test_get_unique_tags_error(mock_db_session):
    # Mock the function to raise an exception
    with patch(
        "app.routes.items.getAllTagsTableNames", new_callable=AsyncMock
    ) as mock_get_tags:
        mock_get_tags.side_effect = Exception("Database error")

        # Make the request
        response = client.get("/items/uniqueTags")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()


# Test for the /item_names endpoint
def test_get_item_names_success(mock_db_session):
    # Mock the function that gets all item names
    with patch(
        "app.routes.items.getAllItemNames", new_callable=AsyncMock
    ) as mock_get_names:
        mock_get_names.return_value = MOCK_ITEM_NAMES

        # Make the request
        response = client.get("/items/item_names")

        # Assert response
        assert response.status_code == 200
        assert len(response.json()) == 3
        assert "Test Item 1" in response.json()
        assert "Test Item 2" in response.json()
        assert "Test Item 3" in response.json()


def test_get_item_names_error(mock_db_session):
    # Mock the function to raise an exception
    with patch(
        "app.routes.items.getAllItemNames", new_callable=AsyncMock
    ) as mock_get_names:
        mock_get_names.side_effect = Exception("Database error")

        # Make the request
        response = client.get("/items/item_names")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()


# Test for the /unique_effects endpoint
def test_get_unique_effects_success(mock_db_session):
    # Mock the function that gets all effects
    with patch(
        "app.routes.items.getAllEffectsTableName", new_callable=AsyncMock
    ) as mock_get_effects:
        mock_get_effects.return_value = STATIC_DATA_EFFECTS

        # Make the request
        response = client.get("/items/unique_effects")

        # Assert response
        assert response.status_code == 200
        assert len(response.json()) == 3
        assert "effect1" in response.json()
        assert "effect2" in response.json()
        assert "effect3" in response.json()


def test_get_unique_effects_error(mock_db_session):
    # Mock the function to raise an exception
    with patch(
        "app.routes.items.getAllEffectsTableName", new_callable=AsyncMock
    ) as mock_get_effects:
        mock_get_effects.side_effect = Exception("Database error")

        # Make the request
        response = client.get("/items/unique_effects")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()
