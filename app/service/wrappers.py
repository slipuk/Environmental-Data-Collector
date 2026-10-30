import asyncio
import functools
from time import perf_counter
from .logger import log

def timeit(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            start = perf_counter()
            result = await func(*args, **kwargs)
            execution_time = perf_counter() - start
            log.message("INFO", f"{func.__name__} finished: elapsed={execution_time:.3f}")
            print(f"INFO {func.__name__} finished: elapsed={execution_time:.3f}")
            return result
    else:
        @functools.wraps(func)
        def inner(*args, **kwargs):
            start = perf_counter()
            result = func(*args, **kwargs)
            execution_time = perf_counter() - start
            log.message("INFO", f"{func.__name__} finished: elapsed={execution_time:.3f}")
            print(f"INFO {func.__name__} finished: elapsed={execution_time:.3f}")
            return result
    return inner
