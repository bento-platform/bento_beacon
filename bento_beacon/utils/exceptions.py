class APIException(Exception):
    def __init__(self, message="Internal Server Error", status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload


class NotImplemented(APIException):
    def __init__(self, message="Not implemented", status_code=501):
        super().__init__()
        self.message = message
        self.status_code = status_code


class InvalidQuery(APIException):
    def __init__(self, message="Invalid query", status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code


class InvalidFilterError(InvalidQuery):
    def __init__(self):
        super().__init__(message="Query used an unsupported filter")


class NotFoundException(APIException):
    def __init__(self, message="Not found", status_code=404):
        super().__init__()
        self.message = message
        self.status_code = status_code


class PermissionsException(APIException):
    def __init__(self, message="Insufficient permissions", status_code=403):
        super().__init__()
        self.message = message
        self.status_code = status_code
