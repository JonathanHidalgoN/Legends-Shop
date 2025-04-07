import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import DeliveryDateAssignerException
from staticData import STATIC_DELIVERY_DATE1, STATIC_DELIVERY_DATE2


STATIC_DELIVERY_DATES = [STATIC_DELIVERY_DATE1, STATIC_DELIVERY_DATE2]

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_delivery_dates_success():
    """Test successful retrieval of delivery dates for a location."""
    with patch(
        "app.delivery.DeliveryDateAssigner.DeliveryDateAssigner.getItemDeliveryDates",
        new=AsyncMock(return_value=STATIC_DELIVERY_DATES),
    ):
        response = client.get("/delivery_dates/dates/1")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["itemId"] == STATIC_DELIVERY_DATE1.itemId
        assert response.json()[0]["locationId"] == STATIC_DELIVERY_DATE1.locationId
        assert (
            response.json()[0]["deliveryDate"]
            == STATIC_DELIVERY_DATE1.deliveryDate.isoformat()
        )
        assert response.json()[1]["itemId"] == STATIC_DELIVERY_DATE2.itemId
        assert response.json()[1]["locationId"] == STATIC_DELIVERY_DATE2.locationId
        assert (
            response.json()[1]["deliveryDate"]
            == STATIC_DELIVERY_DATE2.deliveryDate.isoformat()
        )


@pytest.mark.asyncio
async def test_get_delivery_dates_error():
    """Test error handling when retrieving delivery dates fails."""
    with patch(
        "app.delivery.DeliveryDateAssigner.DeliveryDateAssigner.getItemDeliveryDates",
        new=AsyncMock(
            side_effect=DeliveryDateAssignerException("Failed to get delivery dates")
        ),
    ):
        response = client.get("/delivery_dates/dates/1")
        assert response.status_code == 500
        assert "Failed to get delivery dates" in response.json()["detail"]


@pytest.mark.asyncio
async def test_populate_delivery_dates_success():
    """Test successful population of delivery dates."""
    with patch(
        "app.delivery.DeliveryDateAssigner.DeliveryDateAssigner.assignDeliveryDates",
        new=AsyncMock(return_value=None),
    ):
        response = client.post("/delivery_dates/populate")
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully populated delivery dates"


@pytest.mark.asyncio
async def test_populate_delivery_dates_error():
    """Test error handling when populating delivery dates fails."""
    with patch(
        "app.delivery.DeliveryDateAssigner.DeliveryDateAssigner.assignDeliveryDates",
        new=AsyncMock(
            side_effect=DeliveryDateAssignerException("Failed to assign delivery days")
        ),
    ):
        response = client.post("/delivery_dates/populate")
        assert response.status_code == 500
        assert "Failed to assign delivery days" in response.json()["detail"]
