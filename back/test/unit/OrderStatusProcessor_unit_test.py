import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.OrderStatusProcessor import OrderStatusProcessor


@pytest.fixture
def processor() -> OrderStatusProcessor:
    mockSession = MagicMock(spec=AsyncSession)
    processor = OrderStatusProcessor(mockSession)
    return processor


@pytest.mark.asyncio
async def test_update_order_statuses_no_orders(processor):
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []

    processor.asyncSession.execute = AsyncMock(return_value=mock_result)

    await processor.updateOrderStatuses()
    assert (
        # One query for pending orders tomorrow
        # One query for pending orders today
        # One query to update shipped to delivered
        processor.asyncSession.execute.await_count
        == 3
    )


@pytest.mark.asyncio
async def test_update_order_statuses_db_error(processor):
    processor.asyncSession.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(SQLAlchemyError):
        await processor.updateOrderStatuses()
