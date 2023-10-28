# Standard Library
from enum import Enum

# Django
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ErrorDetail as RestErrorDetail


class ErrorCode(Enum):
    E00 = dict(
        status=status.HTTP_400_BAD_REQUEST,
        message="An unexpected error occurred, try again",
    )
    AUTH01 = dict(
        status=status.HTTP_401_UNAUTHORIZED,
        message="Authentication failed",
    )
    AUTH02 = dict(
        status=status.HTTP_401_UNAUTHORIZED,
        message="You are not allowed to use this application",
    )

    @classmethod
    def get_by_message(cls, message: str):
        try:
            return next(
                error for error in cls if error.value["message"] == message
            )
        except (Exception,):
            return cls.E00

    @classmethod
    def get_by_code(cls, code: str):
        try:
            return next(error for error in cls if error.name == code)
        except (Exception,):
            return cls.E00


class ErrorDetail(RestErrorDetail):
    """
    A string-like object that can additionally have a code and detail.
    """

    code = None

    def __new__(cls, string, code=None, detail=None, field=None):
        self = super().__new__(cls, string)
        self.code = code
        self.detail = detail
        self.field = field
        return self

    def __repr__(self):
        return "ErrorDetail(string=%r, code=%r, detail=%r, field=%r)" % (
            str(self),
            self.code,
            self.detail,
            self.field,
        )


class MOAPIException(APIException):
    def __init__(self, error_code: ErrorCode = None, message: str = None):
        error = error_code
        if message:
            error = ErrorCode.get_by_message(message)
        data = error.value
        self.status_code = data["status"]
        super().__init__(data["message"], error.name)

    @staticmethod
    def raise_custom_error(message: any, status_code: int = None):
        return APIException(message, status_code)


class EventAuthFailed(Exception):
    def __init__(self, payload: dict[str, any], status_code: int = None):
        self.status_code = status_code
        self.payload = payload
        super().__init__(payload)
