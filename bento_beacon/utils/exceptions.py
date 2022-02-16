from ..utils.beacon_response import build_response_meta


class APIException(Exception):
    def __init__(self, message="Internal Server Error", status_code=None, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def beacon_exception(self):
        return {
            "meta": build_response_meta(),
            "error": {
                "errorCode": 500,
                "errorMessage": self.message
            }
        }


class NotImplemented(APIException):
    def __init__(self, message="Not implemented", status_code=501):
        super().__init__()
        self.message = message
        self.status_code = status_code