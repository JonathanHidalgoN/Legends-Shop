import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_ALEMBIC_URL: str = os.getenv(
    "DATABASE_ALEMBIC_URL", "postgresql+asyncpg://db:1234@$localhost:2345/BD"
)
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://db:1234@$localhost:2345/BD"
)
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "Empty")
FRONTEND_PORT: str = os.getenv("FRONTEND_PORT", "Empty")
SECRET_KEY: str = os.getenv("SECRET_KEY", "Empty")
ALGORITHM: str = os.getenv("ALGORITHM", "Empty")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
