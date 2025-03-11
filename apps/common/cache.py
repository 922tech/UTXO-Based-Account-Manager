import functools
import weakref
from typing import Literal, Any

from django.conf import settings
from django.core.cache import cache, caches
import importlib


class NotFoundInCache(Exception):
    pass


class CacheWriteFailed(Exception):
    pass


# it is simply a UUID which tends to be very rare to be set as a value in cache
_DEFAULT = 286065875339472950250869089301745750457


def check_success(exception: Exception):
    """
    calls each wrapped function, if got the call returned None(as all the cache methods of the
    `django.core.cache.cache` do), raises the given exception.
    """

    def check_success_decorator(func):
        @functools.wraps(func)
        def decorated_func(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if result is None and kwargs.get('raise_exception', False):
                raise exception

        return decorated_func

    return check_success_decorator


class CachePrefix:
    FILE = 'f'



class Cache:
    """
    This class is the place of overriding the Django's built-in cache methods
    """

    def __init__(self, name='default'):
        self._cache = caches[name]
        self.name = 'default'

    def __getattr__(self, item):
        """
        If the attribute isn't found on the class itself looks for it on self._cache
        This class uses a bridge to the core cache class of django and prefers composition to inheritance
        """
        return getattr(self._cache, item)

    @staticmethod
    def clear_all():
        """Clears all the caches"""
        for c in caches:
            c.clear()

    def get(self, key, *, raise_exception=False, **kwargs):
        """
        Value of a key may be None in the cache. This method is meant to distinguish between the real None value from
        the cache and an unsuccessful call to the cache.
        If raise_exception is not set, it acts just like the `django.core.cache.cache.get` method
        """
        assert not all(
            ['default' in kwargs, raise_exception]
        ), f"Cannot set `raise_exception=True` and `default` at the same time"
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('default', None)
        value = self._cache.get(key, default=_DEFAULT, **kwargs_copy)
        if value == _DEFAULT and raise_exception:
            raise NotFoundInCache(f"key `{key}` not found in cache `{self.name}`")
        if value == _DEFAULT and 'default' in kwargs:
            return kwargs.get('default')

        return self._cache.get(key, **kwargs)

    @check_success(CacheWriteFailed("setting value was unsuccessful"))
    def set(self, key, value, raise_exception=False, **kwargs):
        return self._cache.set(key, value, **kwargs)

    @check_success(CacheWriteFailed("adding key was unsuccessful"))
    def add(self, key, value, *, raise_exception=False, **kwargs):
        return self._cache.add(key, value, **kwargs)

    @check_success(CacheWriteFailed("deleting key was unsuccessful"))
    def delete(self, key, **kwargs):
        return self._cache.delete(key, **kwargs)

    def get_key(self, prefix: str, id_: Any):
        return f'{getattr(CachePrefix, prefix)}-{id_}'

    @check_success(CacheWriteFailed("setting value was unsuccessful"))
    def set_for_id(self, prefix: str, id_: Any, value, **kwargs):
        return self.set(f'{prefix}-{id_}', value, **kwargs)

    @check_success(CacheWriteFailed("setting value was unsuccessful"))
    def get_for_id(self, prefix: str, id_: Any, **kwargs):
        key = f'{prefix}-{id_}'
        return self.get(key, **kwargs)


def lru_cache_method(*lru_args, **lru_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator
