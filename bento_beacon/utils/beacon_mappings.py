
# temp hardcoding for beacon required fields missing from katsu
BIOSAMPLE_STATUS = {"id": "BFO:0000040", "label": "material entity"}
BIOSAMPLE_ORIGIN_TYPE = {"id": "OBI:0001479",
                         "label": "specimen from organism"}

katsu_beacon_mapped_fields = {
    "id": "id",
    "individual_id": "individualId",
    "sampled_tissue": "sampleOriginDetail",
    "procedure": "obtentionProcedure",
    "tumor_progression": "tumorProgression",
    "tumor_grade": "tumorGrade",
    "histological_diagnosis": "histologicalDiagnosis",
    "diagnostic_markers": "diagnosticMarkers",
    "phenotypic_features": "phenotypicFeatures"
}


def katsu_biosample_to_beacon_biosample(obj):
    obj_keys = obj.keys()
    beacon_biosample = {}

    # beacon required fields
    beacon_biosample["biosampleStatus"] = BIOSAMPLE_STATUS
    beacon_biosample["sampleOriginType"] = BIOSAMPLE_ORIGIN_TYPE

    # directly mapped fields
    for katsu_property, beacon_property in katsu_beacon_mapped_fields.items():
        if (katsu_property) in obj_keys:
            beacon_biosample[beacon_property] = obj[katsu_property]

    # todo:
    # collectionMoment
    # notes
    # info

    return beacon_biosample


################################################################################
# only need beacon |-> katsu mapping

# beacon spec for a biosample entry is at beacon-v2-Models/BEACON-V2-draft4-Model/biosamples/defaultSchema.json
# katsu: https://github.com/bento-platform/katsu/blob/55e7cab78b713202cfc3e6b7a4a2af697098a88a/chord_metadata_service/phenopackets/schemas.py#L238-L286
# phenopackets schema:
# https://github.com/phenopackets/phenopacket-schema/blob/master/src/main/proto/phenopackets/schema/v1/base.proto#L235-L305
