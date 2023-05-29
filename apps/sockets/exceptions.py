class WebSocketException(Exception):
    pass


class WSFunctionNotFound(WebSocketException):
    pass


class WSCustomerNotFound(WebSocketException):
    pass
