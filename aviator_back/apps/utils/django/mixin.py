# Django
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import exceptions as rest_exceptions


class APIErrorsMixin:
    """
    Mixin that transforms Django and Python exceptions into rest_framework ones
    without the mixin, they return 500 status code which is not desired.
    """

    expected_exceptions = {
        AssertionError: rest_exceptions.APIException,
        ValueError: rest_exceptions.ValidationError,
        PermissionError: rest_exceptions.PermissionDenied,
        ObjectDoesNotExist: rest_exceptions.NotFound,
        ValidationError: rest_exceptions.ValidationError,
    }

    def handle_exception(self, exc):
        exception_ancestors = exc.__class__.__mro__[:-1]  # Without `object`

        for ancestor_class in exception_ancestors:
            drf_exception_class = self.expected_exceptions.get(ancestor_class)

            if drf_exception_class is None:
                continue

            drf_exception = drf_exception_class(self.get_error_message(exc))

            return super().handle_exception(drf_exception)

        return super().handle_exception(exc)

    def get_first_matching_attr(self, obj, *attrs, default=None):
        for attr in attrs:
            if hasattr(obj, attr):
                return getattr(obj, attr)

        return default

    def get_error_message(self, exc):
        if hasattr(exc, "message_dict"):
            return exc.message_dict
        error_msg = self.get_first_matching_attr(exc, "message", "messages")

        if isinstance(error_msg, list):
            error_msg = ", ".join(error_msg)

        if error_msg is None:
            error_msg = str(exc)

        return error_msg
