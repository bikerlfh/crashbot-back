# Standard Library
import hashlib
import json

# Django
from django.core.cache import cache
from rest_framework.response import Response


def cache_on_request_data(cache_timeout=None):
    """
    Decorator for views that caches the response of a request
    based on the request data.
    cache_timeout: timeout in seconds
    send 'refresh=True' in the request (QueryParams) to delete the cache
    """

    def decorator(view_func):
        def _wrapped_view_func(view, request, *args, **kwargs):
            request_data = ""
            refresh_cache = request.GET.get("refresh", "False")
            # Serialize request data
            if request.method == "GET":
                data = request.GET.dict()
                data.pop("refresh", None)
                request_data = json.dumps(data, sort_keys=True)
            elif request.method == "POST":
                request_data = json.dumps(request.data, sort_keys=True)
            # Use serialized request data to generate a unique cache key
            cache_key = (
                f"{view.__class__.__name__}"
                f"{hashlib.sha256(request_data.encode()).hexdigest()}"
            )
            # If 'refresh' parameter is True, delete the cache
            if refresh_cache == "True":
                cache.delete(cache_key)
            cache_response = cache.get(cache_key)
            if not cache_response:
                response = view_func(view, request, *args, **kwargs)
                cache.set(
                    cache_key,
                    dict(
                        data=response.data,
                        status=response.status_code,
                    ),
                    cache_timeout,
                )
            else:
                response = Response(
                    data=cache_response["data"], status=cache_response["status"]
                )
            return response

        return _wrapped_view_func

    return decorator
