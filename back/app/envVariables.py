import os
from dotenv import load_dotenv

load_dotenv()
ON_AZURE : bool = os.getenv("ON_AZURE", "False").lower() == "true"
if ON_AZURE:
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "")
    DATABASE_URL: str = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    DATABASE_ALEMBIC_URL: str = DATABASE_URL
else:
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
LOKI_HOST: str = os.getenv("LOKI_HOST", "Empty")
LOKI_PORT: str = os.getenv("LOKI_PORT", "Empty")
USE_LOKI: bool = os.getenv("USE_LOKI", "False").lower() == "true"
USE_PROMETHEUS: bool = os.getenv("USE_PROMETHEUS", "False").lower() == "true"
TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
