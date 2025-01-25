from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from data import database

app = FastAPI()


@app.get("/")
async def root(db: AsyncSession = Depends(database.getDbSession)):
    return {"message": "Hello World"}
