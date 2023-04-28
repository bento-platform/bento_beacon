import json
import os


class Config:
    DEBUG = os.environ.get("BEACON_DEBUG", False)

    BEACON_SPEC_VERSION = "v2.0.0"

    # version of this implementation
    BENTO_BEACON_VERSION = os.environ.get("BENTO_BEACON_VERSION")

    SMALL_CELL_COUNT_THRESHOLD = int(os.environ.get(
        "BEACON_SMALL_CELL_COUNT_THRESHOLD", 5))

    MAX_FILTERS = int(os.environ.get("BEACON_MAX_FILTERS", 2))

    # max granularity for unauthorized users
    DEFAULT_GRANULARITY = {
        "individuals": "count",
        "variants": "count",
        "biosamples": "count",
        "cohorts": "record",
        "datasets": "record",
        "info": "record"
    }

    BEACON_BASE_URL = os.environ.get("BEACON_BASE_URL")

    ENTRY_TYPES_DETAILS = {
        "biosamples": {
            "entryType": "biosample",
            "name": "Biosample",
            "ontologyTermForThisType": {"id": "NCIT:C70699", "label": "Biospecimen"},
            "defaultSchema": {
                "id": "ga4gh-beacon-biosample-v2.0.0",
                "name": "Default schema for biosamples",
                    "referenceToSchemaDefinition": "https://github.com/ga4gh-beacon/beacon-v2/blob/main/models/json/beacon-v2-default-model/biosamples/defaultSchema.json",
                    "schemaVersion": "v2.0.0"
            },
            "partOfSpecification": "Beacon v2.0.0"
        },
        "cohorts": {
            "entryType": "cohort",
            "name": "Cohort",
            "ontologyTermForThisType": {"id": "NCIT:C61512", "label": "Cohort"},
            "defaultSchema": {
                "id": "ga4gh-beacon-cohort-v2.0.0",
                "name": "Default schema for cohorts",
                    "referenceToSchemaDefinition": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/cohorts/defaultSchema.json",
                    "schemaVersion": "v2.0.0"
            },
            "partOfSpecification": "Beacon v2.0.0"

        },
        "datasets": {
            "entryType": "dataset",
            "name": "Dataset",
            "ontologyTermForThisType":  {"id": "NCIT:C47824", "label": "Data set"},
            "defaultSchema": {
                "id": "ga4gh-beacon-dataset-v2.0.0",
                "name": "Default schema for datasets",
                        "referenceToSchemaDefinition": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/datasets/defaultSchema.json",
                        "schemaVersion": "v2.0.0"
            },
            "partOfSpecification": "Beacon v2.0.0"

        },
        "individuals": {
            "entryType": "individual",
            "name": "Individual",
            "ontologyTermForThisType":  {"id": "NCIT:C25190", "label": "Person"},
            "defaultSchema": {
                "id": "phenopacket-v1",
                "name": "phenopacket v1",
                        "referenceToSchemaDefinition": "https://raw.githubusercontent.com/phenopackets/phenopacket-schema/master/src/main/proto/phenopackets/schema/v1/phenopackets.proto",
                        "schemaVersion": "v1.0.0"
            },
            "partOfSpecification": "Phenopacket v1"
        },
        "variants": {
            "entryType": "genomicVariation",
            "name": "Genomic Variant",
            "ontologyTermForThisType":  {"id": "ENSGLOSSARY:0000092", "label": "Variant"},
            "defaultSchema": {
                "id": "ga4gh-beacon-variant-v2.0.0",
                "name": "Default schema for a genomic variation",
                        "referenceToSchemaDefinition": "https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/genomicVariations/defaultSchema.json",
                        "schemaVersion": "v2.0.0"
            },
            "partOfSpecification": "Beacon v2.0.0"

        }
    }
# -------------------
# katsu

    KATSU_BASE_URL = os.environ.get(
        "KATSU_BASE_URL")
    KATSU_BIOSAMPLES_ENDPOINT = "/api/biosamples"
    KATSU_INDIVIDUALS_ENDPOINT = "/api/individuals"
    KATSU_BATCH_INDIVIDUALS_ENDPOINT = "/api/batch/individuals"
    KATSU_DATASETS_ENDPOINT = "/api/datasets"
    KATSU_SEARCH_ENDPOINT = "/private/search"
    KATSU_RESOURCES_ENDPOINT = "/api/resources"
    KATSU_PHENOTYPIC_FEATURE_TERMS_ENDPOINT = "/api/phenotypic_feature_type_autocomplete"
    KATSU_DISEASES_TERMS_ENDPOINT = "/api/disease_term_autocomplete"
    KATSU_SAMPLED_TISSUES_TERMS_ENDPOINT = "/api/biosample_sampled_tissue_autocomplete"
    KATSU_TIMEOUT = int(os.environ.get("BEACON_KATSU_TIMEOUT", 180))

    MAP_EXTRA_PROPERTIES_TO_INFO = os.environ.get(
        "MAP_EXTRA_PROPERTIES_TO_INFO", True)

    PHENOPACKETS_SCHEMA_REFERENCE = {
        "entityType": "individual",
        "schema": "phenopackets v1"
    }
# -------------------
# gohan

    GOHAN_BASE_URL = os.environ.get("GOHAN_BASE_URL")
    GOHAN_SEARCH_ENDPOINT = "/variants/get/by/variantId"
    GOHAN_COUNT_ENDPOINT = "/variants/count/by/variantId"
    GOHAN_OVERVIEW_ENDPOINT = "/variants/overview"
    GOHAN_TIMEOUT = int(os.environ.get("BEACON_GOHAN_TIMEOUT", 60))

# -------------------
# drs

    DRS_INTERNAL_URL = os.environ.get("DRS_INTERNAL_URL")
    DRS_EXTERNAL_URL = os.environ.get("DRS_EXTERNAL_URL")

# -------------------
# handle injected config files
#   a) obtain reference to the expected configuration files' location by
#      using the programmable env variable `CONFIG_ABSOLUTE_PATH` if it exists, or
#   b) default to using "this file's directory" as the reference to where
#      configuration files are expected to be located
    def retrieve_config_json(filename):
        # TODO: abstract out CONFIG_PATH if needed
        config_path = os.environ.get(
            "CONFIG_ABSOLUTE_PATH", os.path.dirname(os.path.abspath(__file__)))
        print(f"Searching for file {filename} in {config_path}")
        file_path = os.path.join(config_path, filename)
        try:
            with open(file_path) as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            # TODO: proper error response
            return {"message": "Beacon error, missing config file"}

    BEACON_COHORT = retrieve_config_json("beacon_cohort.json")

    BEACON_CONFIG = retrieve_config_json("beacon_config.json")
