import logging
import os
from datetime import datetime

logDirName: str = "backend_logs"
os.makedirs(logDirName, exist_ok=True)
logFile = os.path.join(logDirName, f"logs-{datetime.now().strftime("%Y-%m-%d")}.txt")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
fileHandler = logging.FileHandler(logFile)
formatter = logging.Formatter(
    "%(asctime)s- %(name)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s"
)
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)
