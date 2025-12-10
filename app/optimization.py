"""
Optimization utilities for database queries and caching.
"""
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from functools import wraps
import hashlib

CACHE_TIMEOUT_LONG = 3600  # 1 hour for static-ish data
CACHE_TIMEOUT_SHORT = 300  # 5 minutes for more dynamic data


def cache_view_response(timeout=CACHE_TIMEOUT_LONG, cache_key_prefix=''):
    """
    Decorator to cache entire view responses.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method != 'GET' or request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            cache_key = f"{cache_key_prefix}:{request.get_full_path()}"
            response = cache.get(cache_key)
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
            return response
        return wrapper
    return decorator


def cache_queryset(queryset, cache_key, timeout=CACHE_TIMEOUT_SHORT):
    """
    Cache a queryset evaluation.
    """
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    result = list(queryset)
    cache.set(cache_key, result, timeout)
    return result


def clear_cache_pattern(pattern):
    """Clear cache keys matching a pattern (works with some backends)."""
    cache.delete(pattern)
