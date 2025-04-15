from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from app.data.models.MetaDataTable import MetaDataTable
from typing import Optional

async def addMetaData(
    asyncSession: AsyncSession,
    field: str,
    value: str
) -> None:
    """
    Add or update metadata in the MetaDataTable.
    """
    record = {
        "field_name": field,
        "value": value
    }
    
    ins = insert(MetaDataTable).values(**record)
    await asyncSession.execute(ins)
    await asyncSession.flush()

async def getMetaData(
    asyncSession: AsyncSession,
    field: str
) -> Optional[str]:
    """
    Get metadata value for a specific field.
    """
    result = await asyncSession.execute(
        select(MetaDataTable.value).where(MetaDataTable.field_name == field)
    )
    row = result.scalar_one_or_none()
    return row
        
