# Django
from rest_framework.views import exception_handler

# Current Folder
from .formatters import ErrorFormatter


def exception_errors_format_handler(exc, context):
    response = exception_handler(exc, context)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    formatter = ErrorFormatter(exc)

    response.data = formatter()

    return response
