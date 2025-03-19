from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.profile.ProfileWorker import ProfileWorker
from app.customExceptions import ProfileWorkerException, UserNoGoldRow


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
