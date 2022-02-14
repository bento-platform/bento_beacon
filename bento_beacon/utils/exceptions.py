from flask import jsonify


class APIException(Exception):
    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def beacon_exception(self):
        # TODO: build proper beacon error response 
        return jsonify({"beacon error message": self.message})


class NotImplemented(APIException):
    def __init__(self, message="Not implemented", status_code=501):
        super().__init__()
        self.message = message
        self.status_code = status_code





# Beacon error schema

# {
#   "$schema": "http://json-schema.org/draft-07/schema",
#   "type": "object",
#   "description": "An unsuccessful operation.",
#   "properties": {
#     "meta": {
#       "description": "Information about the response that could be relevant for the Beacon client in order to interpret the results.",
#       "$ref": "./sections/beaconResponseMeta.json"
#     },
#     "error": {
#       "description": "Returning an error.",
#       "$ref": "../common/beaconCommonComponents.json#/definitions/BeaconError"
#     }
#   },
#   "required": ["meta", "error"],
#   "additionalProperties": true
# }




    #     "BeaconError": {
    #   "description": "Beacon-specific error.",
    #   "type": "object",
    #   "required": ["errorCode"],
    #   "properties": {
    #     "errorCode": {
    #       "type": "integer",
    #       "format": "int32",
    #       "examples": ["404"],
    #       "description": "Entry not found"
    #     },
    #     "errorMessage": {
    #       "type": "string",
    #       "examples": [
    #         "the provided parameters are incomplete. 'xyz' is missing."
    #       ]
    #     }
    #   }
    # },