import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import ProfileWorkerException, UserNoGoldRow
from app.routes.auth import getCurrentUserTokenFlow
from staticData import (
    STATIC_DATA_USER_IN_DB1,
    STATIC_ORDER_SUMMARY1,
    STATIC_PROFILE_INFO1,
)

client = TestClient(app)


async def fake_getCurrentUserTokenFlow() -> str:
    return "testUser"


app.dependency_overrides[getCurrentUserTokenFlow] = fake_getCurrentUserTokenFlow


@pytest.mark.asyncio
async def test_get_user_gold_success():
    """Test successful retrieval of user's gold."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getUserGoldWithUserName",
        new=AsyncMock(return_value=5000),
    ):
        response = client.get("/profile/current_gold")
        assert response.status_code == 200
        assert response.json() == 5000


@pytest.mark.asyncio
async def test_get_user_gold_no_gold_row():
    """Test error handling when user has no gold row."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getUserGoldWithUserName",
        new=AsyncMock(side_effect=UserNoGoldRow()),
    ):
        response = client.get("/profile/current_gold")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_gold_error():
    """Test error handling when retrieving user's gold fails."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getUserGoldWithUserName",
        new=AsyncMock(side_effect=ProfileWorkerException("SQLAlchemyError")),
    ):
        response = client.get("/profile/current_gold")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_profile_info_success():
    """Test successful retrieval of user's profile info."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getProfileInfo",
        new=AsyncMock(return_value=STATIC_PROFILE_INFO1),
    ):
        response = client.get("/profile/info")
        assert response.status_code == 200
        assert response.json()["user"]["userName"] == STATIC_DATA_USER_IN_DB1.userName
        assert response.json()["user"]["email"] == STATIC_DATA_USER_IN_DB1.email
        assert len(response.json()["ordersInfo"]) == 1
        assert (
            response.json()["ordersInfo"][0]["itemName"]
            == STATIC_ORDER_SUMMARY1.itemName
        )


@pytest.mark.asyncio
async def test_get_profile_info_error():
    """Test error handling when retrieving user's profile info fails."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getProfileInfo",
        new=AsyncMock(side_effect=ProfileWorkerException("SQLAlchemyError")),
    ):
        response = client.get("/profile/info")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_profile_info_none_user():
    """Test error handling when user is None."""
    with patch(
        "app.profile.ProfileWorker.ProfileWorker.getProfileInfo",
        new=AsyncMock(side_effect=ProfileWorkerException("None value in user info")),
    ):
        response = client.get("/profile/info")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
