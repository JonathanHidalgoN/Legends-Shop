import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL: str = os.getenv("DATABASE_URL", "Empty") 
FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "Empty") 
FRONTEND_PORT: str = os.getenv("FRONTEND_PORT", "Empty") 
