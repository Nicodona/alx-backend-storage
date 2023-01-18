#!/usr/bin/env python3
"""
Contains the class definition for redis cache
"""
import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Counts the number of times a function is called
    Args:
        method: The function to be decorated
    Returns:
        The decorated function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function for the decorated function
        Args:
            self: The object instance
            *args: The arguments passed to the function
            **kwargs: The keyword arguments passed to the function
        Returns:
            The return value of the decorated function
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Counts the number of times a function is called
    Args:
        method: The function to be decorated
    Returns:
        The decorated function
    """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function for the decorated function
        Args:
            self: The object instance
            *args: The arguments passed to the function
            **kwargs: The keyword arguments passed to the function
        Returns:
            The return value of the decorated function
        """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data

    return wrapper


def replay(method: Callable) -> None:
    """
    Replays the history of a function
    Args:
        method: The function to be decorated
    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name).decode("utf-8")
    print("{} was called {} times:".format(name, calls))
    inputs = cache.lrange(name + ":inputs", 0, -1)
    outputs = cache.lrange(name + ":outputs", 0, -1)
    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(name, i.decode('utf-8'),
                                     o.decode('utf-8')))
