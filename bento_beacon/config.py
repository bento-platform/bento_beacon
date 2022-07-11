import os


class Config:
    BENTO_URL = os.environ.get("CHORD_URL", "http://127.0.0.1:5000/")

    # TODO: should default to false, not true
    BENTO_DEBUG = os.environ.get("CHORD_DEBUG", True)

    # can be "boolean", "count", or "record"
    BEACON_GRANULARITY = os.environ.get("BEACON_GRANULARITY", "count")

# -------------------
# katsu 

    KATSU_BASE_URL = os.environ.get(
        "KATSU_BASE_URL", "https://portal.bentov2.local/api/metadata/")
    KATSU_BIOSAMPLES_ENDPOINT = "api/biosamples"
    KATSU_SEARCH_ENDPOINT = "open/search"
    KATSU_TIMEOUT = os.environ.get("KATSU_TIMEOUT", 60)

    MAP_EXTRA_PROPERTIES_TO_INFO = os.environ.get(
        "MAP_EXTRA_PROPERTIES_TO_INFO", True)

# -------------------
# gohan 

    GOHAN_BASE_URL = os.environ.get(
        "GOHAN_BASE_URL", "https://portal.bentov2.local/api/gohan")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_TIMEOUT = os.environ.get("GOHAN_TIMEOUT", 60)

# -------------------
# beacon config jsons

    BEACON_CONFIGURATION = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "entryTypes": {
            "genomicVariant": {
                "additionallySupportedSchemas": [],
                "defaultSchema": {
                    "id": "ga4gh-beacon-variant-v2.0.0",
                    "name": "Default schema for a genomic variation",
                    "referenceToSchemaDefinition": "https://exampleBeacons.org/genomicVariations/defaultSchema.json",
                    "schemaVersion": "v2.0.0"
                },
                "description": "The location of a sequence.",
                "id": "genomicVariant",
                "name": "Genomic Variants",
                "ontologyTermForThisType": {
                    "id": "ENSGLOSSARY:0000092",
                    "label": "Variant"
                },
                "partOfSpecification": "Beacon v2.0.0"
            },
            "individual": {
                "additionallySupportedSchemas": [],
                "defaultSchema": {
                    "id": "ga4gh-beacon-individual-v2.0.0",
                    "name": "Default schema for an individual",
                    "referenceToSchemaDefinition": "https://exampleBeacons.org/individuals/defaultSchema.json",
                    "schemaVersion": "v2.0.0"
                },
                "description": "A human being. It could be a Patient, a Tissue Donor, a Participant, a Human Study Subject, etc.",
                "id": "individual",
                "name": "Individual",
                "ontologyTermForThisType": {
                    "id": "NCIT:C25190",
                    "label": "Person"
                },
                "partOfSpecification": "Beacon v2.0.0"
            }
        },
        "maturityAttributes": {
            "productionStatus": "DEV"
        },
        "securityAttributes": {
            "defaultGranularity": "count",
            "securityLevels": ["PUBLIC"]
        }
    }

    BEACON_MAP = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "endpointSets": {
            "genomicVariant": {
                "endpoints": {
                    "individual": {
                        "returnedEntryType": "individual",
                        "url": "https://exampleBeacons.org/g_variants/{id}/individuals"
                    }
                },
                "entryType": "genomicVariant",
                "openAPIEndpointsDefinition": "https://exampleBeacons.org/genomicVariations/endpoints.json",
                "rootUrl": "https://exampleBeacons.org/g_variants",
                "singleEntryUrl": "https://exampleBeacons.org/g_variants/{id}"
            },
            "individual": {
                "endpoints": {},
                "entryType": "individual",
                "filteringTermsUrl": "https://exampleBeacons.org/individuals/{id}/filtering_terms",
                "openAPIEndpointsDefinition": "https://exampleBeacons.org/individuals/endpoints.json",
                "rootUrl": "https://exampleBeacons.org/individuals",
                "singleEntryUrl": "https://exampleBeacons.org/individuals/{id}"
            }
        }
    }

    BEACON_ENDPOINTS = {
        "components": {
            "parameters": {
                "limit": {
                    "in": "query",
                    "name": "limit",
                    "schema": {
                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/common/beaconCommonComponents.json#/definitions/Limit"
                    }
                },
                "requestedSchema": {
                    "description": "Schema to be used to format the `result` field in the response. The response will use Beacon format.",
                    "example": "ga4gh-service-info-v1.0",
                    "in": "query",
                    "name": "requestedSchema",
                    "required": "false",
                    "schema": {
                        "type": "string"
                    }
                },
                "skip": {
                    "in": "query",
                    "name": "skip",
                    "schema": {
                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/common/beaconCommonComponents.json#/definitions/Skip"
                    }
                }
            },
            "responses": {
                "infoOKResponse": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconInfoResponse.json",
                                "description": "Response of a request for information about a Beacon"
                            }
                        }
                    },
                    "description": "Successful operation"
                }
            }
        },
        "info": {
            "contact": {
                "email": "beacon@ga4gh.org"
            },
            "description": "A Beacon is a web service for data discovery and sharing that can be queried for information about entry types defined by a Model.",
            "license": {
                "name": "Apache 2.0",
                "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
            },
            "title": "GA4GH Beacon API Specification",
            "version": "2.0.0"
        },
        "openapi": "3.0.2",
        "paths": {
            "/": {
                "get": {
                    "description": "Get information about the beacon",
                    "operationId": "getBeaconRoot",
                    "responses": {
                        "200": {
                            "$ref": "#/components/responses/infoOKResponse"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Informational endpoints"]
                },
                "parameters": [
                    {
                        "$ref": "#/components/parameters/requestedSchema"
                    }
                ]
            },
            "/configuration": {
                "get": {
                    "description": "TBD",
                    "operationId": "getBeaconConfiguration",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconConfigurationResponse.json",
                                        "description": "Response of a request for information about a Beacon"
                                    }
                                }
                            },
                            "description": "Successful operation"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Configuration"]
                }
            },
            "/entry_types": {
                "get": {
                    "description": "TBD",
                    "operationId": "getEntryTypes",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconEntryTypesResponse.json",
                                        "description": "Response of a request for information about a Beacon"
                                    }
                                }
                            },
                            "description": "Successful operation"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Configuration"]
                }
            },
            "/filtering_terms": {
                "get": {
                    "description": "Get the list of filtering terms handled by this beacon",
                    "operationId": "getFilteringTerms",
                    "responses": {
                        "200": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconFilteringTermsResponse.json"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Informational endpoints"]
                },
                "parameters": [
                    {
                        "$ref": "#/components/parameters/skip"
                    },
                    {
                        "$ref": "#/components/parameters/limit"
                    }
                ]
            },
            "/info": {
                "get": {
                    "description": "Get information about the beacon",
                    "operationId": "getBeaconInfoRoot",
                    "responses": {
                        "200": {
                            "$ref": "#/components/responses/infoOKResponse"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Informational endpoints"]
                },
                "parameters": [
                    {
                        "$ref": "#/components/parameters/requestedSchema"
                    }
                ]
            },
            "/map": {
                "get": {
                    "description": "TBD",
                    "operationId": "getBeaconMap",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconMapResponse.json",
                                        "description": "Response of a request for information about a Beacon"
                                    }
                                }
                            },
                            "description": "Successful operation"
                        },
                        "default": {
                            "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/beaconErrorResponse.json",
                            "description": "An unsuccessful operation"
                        }
                    },
                    "tags": ["Configuration"]
                }
            },
            "/service-info": {
                "get": {
                    "description": "Get information about the beacon using GA4GH ServiceInfo format",
                    "operationId": "getBeaconServiceInfo",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/framework/json/responses/ga4gh-service-info-1-0-0-schema.json"
                                    }
                                }
                            },
                            "description": "Successful operation"
                        }
                    },
                    "tags": ["Informational endpoints"]
                }
            }
        },
        "servers": []
    }
