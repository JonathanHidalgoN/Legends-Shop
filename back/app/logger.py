import logging
import os
from datetime import datetime
import functools
import asyncio
from logging.handlers import RotatingFileHandler
import traceback
from typing import Any, Optional, Callable

# ===== CONFIGURATION CONSTANTS =====
# Directory where log files will be stored
LOG_DIR_NAME = "backend_logs"
# Maximum size of each log file before rotation (10MB)
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024
# Number of backup log files to keep
LOG_FILE_BACKUP_COUNT = 5
# Default logging level (DEBUG shows all messages, INFO shows info and above, etc.)
DEFAULT_LOG_LEVEL = logging.DEBUG
# Fields that should be redacted (hidden) in logs for security
SENSITIVE_FIELDS = {"password", "token", "access_token", "secret", "api_key", "key"}


def redact(value: Any) -> Any:
    """
    Redact sensitive information from values to prevent logging sensitive data.

    This function recursively processes dictionaries, lists, and strings to hide
    sensitive information like passwords, tokens, and API keys.

    Args:
        value: The value to redact (can be a dict, list, string, or other type)

    Returns:
        The redacted value with sensitive information replaced with '***'

    Example:
        >>> redact({"username": "user", "password": "secret123"})
        {"username": "user", "password": "***"}
    """
    if isinstance(value, dict):
        # For dictionaries, check each key for sensitive terms
        return {
            k: (
                "***"
                if any(sensitive in k.lower() for sensitive in SENSITIVE_FIELDS)
                else v
            )
            for k, v in value.items()
        }
    elif isinstance(value, list):
        # For lists, recursively redact each item
        return [redact(item) for item in value]
    elif isinstance(value, str) and any(
        sensitive in value.lower() for sensitive in SENSITIVE_FIELDS
    ):
        # For strings that might contain sensitive information
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

        This method adds custom attributes to the log record before formatting,
        allowing us to include class name, function name, and arguments in the log message.

        Args:
            record: The log record to format

        Returns:
            The formatted log message as a string
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


# ===== LOGGER SETUP =====
# Create log directory if it doesn't exist
os.makedirs(LOG_DIR_NAME, exist_ok=True)
# Create a log file with today's date
log_file = os.path.join(LOG_DIR_NAME, f"logs-{datetime.now().strftime('%Y-%m-%d')}.txt")

# Configure the main logger
logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LOG_LEVEL)

# Stream handler for console output (shows logs in terminal)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(DEFAULT_LOG_LEVEL)

# Rotating file handler for log files (automatically rotates when file gets too large)
file_handler = RotatingFileHandler(
    log_file, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT
)
file_handler.setLevel(DEFAULT_LOG_LEVEL)

# Create formatter with detailed information
# %(asctime)s - Timestamp
# %(name)s - Logger name
# %(filename)s:%(lineno)d - File and line number
# %(class)s.%(function)s - Class and function name
# %(levelname)s - Log level (DEBUG, INFO, etc.)
# %(message)s - The log message
# %(func_args)s - Function arguments
# %(kwargs)s - Keyword arguments
formatter = CustomFormatter(
    "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(class)s.%(function)s - %(levelname)s - %(message)s - args: %(func_args)s - kwargs: %(kwargs)s"
)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def logMethod(func: Callable) -> Callable:
    """
    Decorator to automatically log function calls, successes, and errors.

    This decorator can be applied to any function or method to automatically log:
    - When the function is called (with arguments)
    - When the function exits successfully
    - Any exceptions that occur during execution

    It works with both synchronous and asynchronous functions.

    Usage:
        @logMethod
        def my_function(arg1, arg2):
            # Function code here
            pass

        @logMethod
        async def my_async_function(arg1, arg2):
            # Async function code here
            pass

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

        # Log function entry with arguments (redacted for security)
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
            # Execute the async function
            result = await func(*args, **kwargs)

            # Log successful exit
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
            # Log error with full traceback
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
            raise  # Re-raise the exception after logging

    @functools.wraps(func)
    def syncWrapper(*args, **kwargs):
        # Get class name if this is a method (first arg is self)
        className = args[0].__class__.__name__ if args else ""
        funcName = func.__name__

        # Log function entry with arguments (redacted for security)
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
            # Execute the synchronous function
            result = func(*args, **kwargs)

            # Log successful exit
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
            # Log error with full traceback
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
            raise  # Re-raise the exception after logging

    # Return the appropriate wrapper based on whether the function is async
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

    Usage:
        # Get the default logger
        logger = get_logger()

        # Get a logger with a specific name
        my_logger = get_logger("my_module")

        # Use the logger
        my_logger.info("This is an info message")
        my_logger.error("This is an error message")

    Args:
        name: The name of the logger (optional)

    Returns:
        A configured logger
    """
    return logging.getLogger(name or __name__)


# ===== USAGE EXAMPLES =====
"""
# Example 1: Using the logMethod decorator
from app.logger import logMethod

class UserService:
    @logMethod
    def create_user(self, username, password):
        # This will automatically log the function call, success, and any errors
        return {"id": 1, "username": username}

# Example 2: Using the logger directly
from app.logger import get_logger

logger = get_logger("user_service")

def process_user_data(user_data):
    logger.info("Processing user data", extra={"user_id": user_data["id"]})
    try:
        # Process data
        result = do_something(user_data)
        logger.info("User data processed successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to process user data: {str(e)}", exc_info=True)
        raise

# Example 3: Logging with different levels
logger.debug("Detailed information for debugging")
logger.info("General information about program execution")
logger.warning("Warning messages for potentially problematic situations")
logger.error("Error messages for serious problems")
logger.critical("Critical messages for fatal errors")
"""
