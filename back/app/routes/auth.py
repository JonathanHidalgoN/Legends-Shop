from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.functions import createAccessToken, verifyPassword, verifyToken, hashPassword
from app.data import database
from app.data.queries.authQueries import getUserInDB
from app.schemas.AuthSchemas import Token, UserInDB 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

#Source:https://fastapi.tiangolo.com/tutorial/security/first-steps/#create-mainpy
router = APIRouter()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

fakeDB = {
    "admin":{
        "username":"admin",
        "hashed_password":hashPassword("secret")
    }
}

def getCurrentUser(token:Annotated[str, Depends(oauth2Scheme)]):
    userName: str | None = verifyToken(token)
    if not userName:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WW-Authenticate":"Bearer"},
        )
    return userName

# https://stackoverflow.com/questions/65059811/what-does-depends-with-no-parameter-do
@router.post("/token", response_model=Token)
async def getToken(dataForm: Annotated[OAuth2PasswordRequestForm,  Depends()],
                   db: AsyncSession = Depends(database.getDbSession),):
    try:
        matchUser : UserInDB | None = await getUserInDB(db, dataForm.username)
    except Exception:
        raise HTTPException(status_code=503, detail="Error retriving the user from the server")
    if not matchUser:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verifyPassword(dataForm.password, matchUser.hashedPassword):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    accessToken = createAccessToken(data={"sub":matchUser.userName})
    return {"access_token":accessToken, "token_type": "bearer"}

@router.get("/test")
async def protectTest(user:Annotated[str, Depends(getCurrentUser)]):
    return {"message":user}
