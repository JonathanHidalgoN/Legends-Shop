import os
from dotenv import load_dotenv


# This function gets the databaseUrl
def getDatabaseUrl() -> str:
    load_dotenv()
    databaseUrl = os.getenv("DATABASE_URL", "Empty")
    return databaseUrl


##Run the app with this function and check if bracks, else check
# the alembic command to update with alchemy modesl
