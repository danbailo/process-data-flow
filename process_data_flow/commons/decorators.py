import asyncio
import hashlib
import json
import signal
import time
from functools import wraps
from math import ceil

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.settings import REDIS_CLIENT

_logger: Logger = LoggerFactory.new()


def coro(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


def async_timeit(function):
    @wraps(function)
    def _async_timeit(*args, **kwargs):
        start = time.monotonic()
        try:
            return asyncio.run(function(*args, **kwargs))
        finally:
            _logger.debug(
                f'Time elapsed to run "{function.__name__}" - '
                f'{time.monotonic() - start:0.2f}s',
            )

    return _async_timeit


def timeit(function):
    @wraps(function)
    def _timeit(*args, **kwargs):
        start = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            _logger.debug(
                f'Time elapsed to run "{function.__name__}" - '
                f'{time.monotonic() - start:0.2f}s',
            )

    return _timeit


def timeout(seconds):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            def handle_timeout(signum, frame):
                raise TimeoutError(
                    f'The function "{function.__name__}" is taking more than '
                    f'{seconds} seconds to run! '
                )

            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(ceil(seconds))

            result = function(*args, **kwargs)

            signal.alarm(0)
            return result

        return wrapper

    return decorator


def cache(ttl: int = 60, *, is_class_method: bool):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            original_args = args
            if is_class_method is True:
                args = args[1:]
            key = (
                f'{function.__name__}:'
                + hashlib.md5((str(args) + str(kwargs)).encode()).hexdigest()
            )
            cached_result = REDIS_CLIENT.get(key)
            if cached_result:
                try:
                    cached_result = json.loads(cached_result)
                except Exception:
                    _logger.debug(
                        'Error when trying to deserialize value', exc_info=True
                    )

                _logger.debug('Using cache from Redis', key=key, value=cached_result)
                return cached_result

            result = function(*original_args, **kwargs)

            _logger.debug('Caching result...', ttl=ttl)
            to_cache = result
            if not isinstance(to_cache, str):
                to_cache = json.dumps(result)
            REDIS_CLIENT.set(key, to_cache, ex=ttl)
            _logger.debug('Result cached!', ttl=ttl)

            return result

        return wrapper

    return decorator


def async_cache(ttl: int = 60, *, is_class_method: bool):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            original_args = args
            if is_class_method is True:
                args = args[1:]
            key = (
                f'{function.__name__}:'
                + hashlib.md5((str(args) + str(kwargs)).encode()).hexdigest()
            )
            cached_result = REDIS_CLIENT.get(key)
            if cached_result:
                try:
                    cached_result = json.loads(cached_result)
                except Exception:
                    _logger.debug(
                        'Error when trying to deserialize value', exc_info=True
                    )

                _logger.debug('Using cache from Redis', key=key, value=cached_result)
                return cached_result

            result = await function(*original_args, **kwargs)

            _logger.debug('Caching result...', ttl=ttl)
            to_cache = result
            if not isinstance(to_cache, str):
                to_cache = json.dumps(result)
            REDIS_CLIENT.set(key, to_cache, ex=ttl)
            _logger.debug('Result cached!', ttl=ttl)

            return result

        return wrapper

    return decorator
