import logging
import os
from datetime import datetime
import functools
import asyncio
from logging.handlers import RotatingFileHandler
import traceback
from typing import Any, Optional, Callable
import logging_loki
from app.envVariables import LOKI_HOST, LOKI_PORT, USE_LOKI

LOG_DIR_NAME = "backend_logs"
# Maximum size of each log file before rotation (10MB)
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024
# Number of backup log files to keep
LOG_FILE_BACKUP_COUNT = 5
DEFAULT_LOG_LEVEL = logging.DEBUG
SENSITIVE_FIELDS = {"password", "token", "access_token", "secret", "api_key", "key"}


def redact(value: Any) -> Any:
    """
    Redact sensitive information from values to prevent logging sensitive data.

    This function recursively processes dictionaries, lists, and strings to hide
    sensitive information like passwords, tokens, and API keys.
    """
    if isinstance(value, dict):
        return {
            k: (
                "***"
                if any(sensitive in k.lower() for sensitive in SENSITIVE_FIELDS)
                else v
            )
            for k, v in value.items()
        }
    elif isinstance(value, list):
        return [redact(item) for item in value]
    elif isinstance(value, str) and any(
        sensitive in value.lower() for sensitive in SENSITIVE_FIELDS
    ):
        return "***"
    return value


class CustomFormatter(logging.Formatter):
    """
    Custom formatter that adds class and function information to log records.

    This formatter extends the standard logging.Formatter to include additional
    context information in log messages, such as the class name, function name,
    and function arguments.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with additional context.
        """
        # Set default values for custom attributes if they don't exist
        record.__dict__.setdefault("class", "")
        record.__dict__.setdefault("function", "")
        record.__dict__.setdefault("func_args", "")
        record.__dict__.setdefault("kwargs", "")

        # Format exception info if present to include full traceback
        if record.exc_info:
            record.exc_text = "".join(traceback.format_exception(*record.exc_info))

        return super().format(record)


# Create log directory if it doesn't exist
os.makedirs(LOG_DIR_NAME, exist_ok=True)
logFile = os.path.join(LOG_DIR_NAME, f"logs-{datetime.now().strftime('%Y-%m-%d')}.txt")

# Configure the main logger
logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LOG_LEVEL)

# Stream handler for console output
streamHandler = logging.StreamHandler()
streamHandler.setLevel(DEFAULT_LOG_LEVEL)

# Rotating file handler for log files (automatically rotates when file gets too large)
fileHandler = RotatingFileHandler(
    logFile, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT
)
fileHandler.setLevel(DEFAULT_LOG_LEVEL)

formatter = CustomFormatter(
    "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(class)s.%(function)s - %(levelname)s - %(message)s - args: %(func_args)s - kwargs: %(kwargs)s"
)
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)

if USE_LOKI:
    lokiHandler = logging_loki.LokiHandler(
        url=f"http://{LOKI_HOST}:{LOKI_PORT}/loki/api/v1/push",
        tags={"application": "python-backend"},
        version="1",
    )
    logger.addHandler(lokiHandler)


def logMethod(func: Callable) -> Callable:
    """
    Decorator to automatically log function calls, successes, and errors.
    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """

    @functools.wraps(func)
    async def asyncWrapper(*args, **kwargs):
        # Get class name if this is a method (first arg is self)
        className = args[0].__class__.__name__ if args else ""
        funcName = func.__name__

        logger.info(
            "Function called",
            extra={
                "class": className,
                "function": funcName,
                "func_args": redact(args[1:]),
                "kwargs": redact(kwargs),
            },
        )

        try:
            result = await func(*args, **kwargs)

            logger.info(
                "Function exited successfully",
                extra={
                    "class": className,
                    "function": funcName,
                    "func_args": redact(args[1:]),
                    "kwargs": redact(kwargs),
                },
            )
            return result
        except Exception as e:
            logger.error(
                f"Error in function call: {str(e)}",
                extra={
                    "class": className,
                    "function": funcName,
                    "func_args": redact(args[1:]),
                    "kwargs": redact(kwargs),
                    "error": str(e),
                },
                exc_info=True,  # Include full traceback
            )
            raise

    @functools.wraps(func)
    def syncWrapper(*args, **kwargs):
        # Get class name if this is a method (first arg is self)
        className = args[0].__class__.__name__ if args else ""
        funcName = func.__name__

        logger.info(
            "Function called",
            extra={
                "class": className,
                "function": funcName,
                "func_args": redact(args[1:]),
                "kwargs": redact(kwargs),
            },
        )

        try:
            result = func(*args, **kwargs)

            logger.info(
                "Function exited successfully",
                extra={
                    "class": className,
                    "function": funcName,
                    "func_args": redact(args[1:]),
                    "kwargs": redact(kwargs),
                },
            )
            return result
        except Exception as e:
            logger.error(
                f"Error in function call: {str(e)}",
                extra={
                    "class": className,
                    "function": funcName,
                    "func_args": redact(args[1:]),
                    "kwargs": redact(kwargs),
                    "error": str(e),
                },
                exc_info=True,  # Include full traceback
            )
            raise

    if asyncio.iscoroutinefunction(func):
        return asyncWrapper
    else:
        return syncWrapper


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.

    This function provides a convenient way to get a logger with the same
    configuration as the main logger. If no name is provided, it returns
    the default logger.
    """
    return logging.getLogger(name or __name__)
