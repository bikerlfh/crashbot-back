import json
import hashlib
from django.core.cache import cache
from rest_framework.response import Response


def cache_on_request_data(cache_timeout=None):
    def decorator(view_func):
        def _wrapped_view_func(view, request, *args, **kwargs):
            request_data = ''
            # Serialize request data
            if request.method == 'GET':
                request_data = json.dumps(request.GET.dict(), sort_keys=True)
            elif request.method == 'POST':
                request_data = json.dumps(request.data, sort_keys=True)
            # Use serialized request data to generate a unique cache key
            cache_key = f"{view.__class__.__name__}" \
                        f"{hashlib.sha256(request_data.encode()).hexdigest()}"
            # If 'refresh' parameter is True, delete the cache
            if request.GET.get('refresh') == 'True':
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
                    cache_timeout
                )
            else:
                response = Response(
                    data=cache_response['data'],
                    status=cache_response['status']
                )
            return response
        return _wrapped_view_func
    return decorator
