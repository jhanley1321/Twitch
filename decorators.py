# decorators.py
from functools import wraps
import time
import requests

def retry_on_failure(max_retries=3, delay=1):
    """
    Retry API calls on failure.

    Args:
        max_retries (int): Maximum number of retry attempts.
        delay (int): Delay in seconds between retries.

    Returns:
        decorator: A decorator function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator