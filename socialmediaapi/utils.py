import functools
import logging

logger = logging.getLogger(__name__)


def log(logger):
    def decorator_log(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.info(f"Function {func.__name__} called with args {signature}")
            result = func(*args, **kwargs)
            return await result

        return wrapper

    return decorator_log
