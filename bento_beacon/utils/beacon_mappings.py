from flask import current_app

# temp hardcoding for beacon required fields missing from katsu
# TODO: better solution or move to config
BIOSAMPLE_STATUS = {"id": "BFO:0000040", "label": "material entity"}
BIOSAMPLE_ORIGIN_TYPE = {"id": "OBI:0001479", "label": "specimen from organism"}

# mostly identity, but a few remappings
katsu_beacon_biosample_mapped_fields = {
    "id": "id",
    "individualId": "individualId",
    "sampledTissue": "sampleOriginDetail",
    "procedure": "obtentionProcedure",
    "tumorProgression": "tumorProgression",
    "tumorGrade": "tumorGrade",
    "histologicalDiagnosis": "histologicalDiagnosis",
    "diagnosticMarkers": "diagnosticMarkers",
    "phenotypicFeatures": "phenotypicFeatures",
}


def katsu_biosample_to_beacon_biosample(obj):
    obj_keys = obj.keys()
    beacon_biosample = {}

    # beacon required fields without katsu equivalents
    beacon_biosample["biosampleStatus"] = BIOSAMPLE_STATUS
    beacon_biosample["sampleOriginType"] = BIOSAMPLE_ORIGIN_TYPE

    # directly mapped fields
    for katsu_property, beacon_property in katsu_beacon_biosample_mapped_fields.items():
        if (katsu_property) in obj_keys:
            beacon_biosample[beacon_property] = obj[katsu_property]

    # remaining fields
    age_at_collection = obj.get("individualAgeAtCollection", {}).get("age")
    if age_at_collection is not None:
        beacon_biosample["collectionMoment"] = age_at_collection

    # beacon prefers mapping extra properties to "info"
    if "extraProperties" in obj.keys() and current_app.config["MAP_EXTRA_PROPERTIES_TO_INFO"]:
        beacon_biosample["info"] = obj["extraProperties"]

    return beacon_biosample


################################################################################
# only need beacon |-> katsu mapping

# beacon spec for a biosample entry is at beacon-v2-Models/BEACON-V2-draft4-Model/biosamples/defaultSchema.json
# katsu: https://github.com/bento-platform/katsu/blob/55e7cab78b713202cfc3e6b7a4a2af697098a88a/chord_metadata_service/phenopackets/schemas.py#L238-L286
# phenopackets schema:
# https://github.com/phenopackets/phenopacket-schema/blob/master/src/main/proto/phenopackets/schema/v1/base.proto#L235-L305


def katsu_to_beacon_dataset_mapping(kd):
    if kd:
        return {
            "id": kd.get("identifier"),
            "title": kd.get("title"),
            "description": kd.get("description"),
            # "dataUseConditions": kd.get("dataUse"),
        }


# TODO: beacon spec dataUseConditions
# either wait for katsu to send full DUO ontologies, or write a Bento code -> DUO ontology mapping
