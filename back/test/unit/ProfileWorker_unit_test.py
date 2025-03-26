from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.profile.ProfileWorker import ProfileWorker
from app.customExceptions import ProfileWorkerException, UserNoGoldRow
from staticData import STATIC_DATA_USER_IN_DB1, STATIC_ORDER_SUMMARY1, STATIC_PROFILE_INFO1


@pytest.fixture
def worker() -> ProfileWorker:
    mockSession = MagicMock(spec=AsyncSession)
    worker = ProfileWorker(mockSession)
    return worker


@pytest.mark.asyncio
async def test_getUserGoldWithUserName_success(worker: ProfileWorker):
    userName = "testuser"
    expectedGold = 1000

    with patch(
        "app.profile.ProfileWorker.getCurrentUserGoldWithUserName",
        new=AsyncMock(return_value=expectedGold),
    ):
        result = await worker.getUserGoldWithUserName(userName)
        assert result == expectedGold


@pytest.mark.asyncio
async def test_getUserGoldWithUserName_no_gold(worker: ProfileWorker):
    userName = "testuser"

    with patch(
        "app.profile.ProfileWorker.getCurrentUserGoldWithUserName",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(UserNoGoldRow):
            await worker.getUserGoldWithUserName(userName)


@pytest.mark.asyncio
async def test_getUserGoldWithUserName_sqlalchemy_error(worker: ProfileWorker):
    userName = "testuser"

    with patch(
        "app.profile.ProfileWorker.getCurrentUserGoldWithUserName",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ProfileWorkerException) as excinfo:
            await worker.getUserGoldWithUserName(userName)
        assert "SQLAlchemyError" in str(excinfo.value)

@pytest.mark.asyncio
async def test_getProfileInfo_success(worker: ProfileWorker):
    userName = "testuser"
    fakeUser = STATIC_DATA_USER_IN_DB1 
    fakeOrderSummaryList = [STATIC_ORDER_SUMMARY1]
    expectedProfileInfo = STATIC_PROFILE_INFO1
    with patch("app.profile.ProfileWorker.getUserInDB", new=AsyncMock(return_value=fakeUser)):
        with patch.object(worker, "buildOrderSummaryForUser", new=AsyncMock(return_value=fakeOrderSummaryList)):
            result = await worker.getProfileInfo(userName)
            assert result == expectedProfileInfo

@pytest.mark.asyncio
async def test_getProfileInfo_none_user(worker: ProfileWorker):
    userName = "testuser"
    with patch("app.profile.ProfileWorker.getUserInDB", new=AsyncMock(return_value=None)):
        with pytest.raises(ProfileWorkerException) as excinfo:
            await worker.getProfileInfo(userName)
        assert "None value in user info" in str(excinfo.value)

@pytest.mark.asyncio
async def test_getProfileInfo_sqlalchemy_error(worker: ProfileWorker):
    userName = "testuser"
    with patch("app.profile.ProfileWorker.getUserInDB", new=AsyncMock(side_effect=SQLAlchemyError("DB error"))):
        with pytest.raises(ProfileWorkerException) as excinfo:
            await worker.getProfileInfo(userName)
        assert "SQLAlchemyError" in str(excinfo.value)
