# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# temp file, all of this to be handled elsewhere in final version
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

BEACONS = [
    "https://rsrq.bento.sd4h.ca/api/beacon",
    "https://bqc19.bento.sd4h.ca/api/beacon",
    # "https://staging.bqc19.bento.sd4h.ca/api/beacon",
    "https://staging.bento.sd4h.ca/api/beacon",
    "https://ichange.bento.sd4h.ca/api/beacon",
    # "https://qa.bento.sd4h.ca/api/beacon/",
    # "https://bentov2.local/api/beacon",
    # "https://renata.bento.sd4h.ca/api/beacon",
]

NETWORK_TIMEOUT = 30

VALID_ENDPOINTS = ["analyses", "biosamples", "cohorts", "datasets", "g_variants", "individuals", "runs", "overview"]



KATSU_CONFIG_INTERSECTION = [
    {
        "section_title": "Common Filters",
        "fields": [
            {
                "config": {
                    "bin_size": 10,
                    "maximum": 100,
                    "minimum": 0,
                    "taper_left": 10,
                    "taper_right": 100,
                    "units": "years"
                },
                "datatype": "number",
                "description": "Age at arrival",
                "id": "age",
                "mapping": "individual/age_numeric",
                "options": [
                    "[30, 40)",
                    "[40, 50)",
                    "[50, 60)",
                    "[60, 70)",
                    "[70, 80)",
                    "[80, 90)"
                ],
                "title": "Age"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Sex at birth",
                "id": "sex",
                "mapping": "individual/sex",
                "options": [
                    "MALE",
                    "FEMALE"
                ],
                "title": "Sex"
            }
        ]
    }
]






KATSU_CONFIG_UNION = [
    {
        "section_title": "All Filters",
        "fields": [
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Phenotypic features of the individual",
                "id": "phenotypic_features_type",
                "mapping": "individual/phenopackets/phenotypic_features/pftype/label",
                "options": [
                    "Asthma",
                    "Allergy",
                    "Rhinosinusitis",
                    "Overlap Syndrome",
                    "Tabagism",
                    "Asthma subject type",
                    "Phenotype",
                    "Loss of appetite",
                    "Abdominal pain",
                    "Headache",
                    "Cough",
                    "Cardiac arrest",
                    "Viral pneumonia/pneumonitis",
                    "Pulmonary hypertension",
                    "Nausea",
                    "HIV Infection",
                    "Hyperglycemia",
                    "Patient immunosuppressed",
                    "Fever",
                    "Chest pain",
                    "Pneumothorax",
                    "Dementia",
                    "Hypertension",
                    "Loss of sense of smell"
                ],
                "title": "Phenotypic Features"
            },
            {
                "config": {
                    "bin_size": 10,
                    "maximum": 100,
                    "minimum": 0,
                    "taper_left": 10,
                    "taper_right": 100,
                    "units": "years"
                },
                "datatype": "number",
                "description": "Age at arrival",
                "id": "age",
                "mapping": "individual/age_numeric",
                "options": [
                    "< 10",
                    "[10, 20)",
                    "[20, 30)",
                    "[30, 40)",
                    "[40, 50)",
                    "[50, 60)",
                    "[60, 70)",
                    "[70, 80)",
                    "[80, 90)",
                    "[90, 100)",
                    "< 18",
                    "[18, 30)",
                    "≥ 90"
                ],
                "title": "Age"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Sex at birth",
                "id": "sex",
                "mapping": "individual/sex",
                "options": [
                    "MALE",
                    "FEMALE",
                    "UNKNOWN_SEX"
                ],
                "title": "Sex"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Measurements performed",
                "group_by": "assay/label",
                "id": "measurement_types",
                "mapping": "individual/phenopackets/measurements",
                "options": [
                    "Body Mass Index",
                    "Cp20 Measurement",
                    "Eosinophils Percentage",
                    "Histological Eosinophils",
                    "Histological Neutrophils",
                    "Immunoglobulin E",
                    "Neutrophils Percentage"
                ],
                "title": "Measurement types"
            },
            {
                "config": {
                    "bin_size": "10",
                    "maximum": 50,
                    "minimum": 0,
                    "taper_left": 0,
                    "taper_right": 50,
                    "units": "kg/m^2"
                },
                "datatype": "number",
                "description": "Measurements performed",
                "group_by": "assay/id",
                "group_by_value": "NCIT:C16358",
                "id": "measurement_bmi",
                "mapping": "individual/phenopackets/measurements",
                "options": [
                    "[0, 10)",
                    "[10, 20)",
                    "[20, 30)",
                    "[30, 40)",
                    "[40, 50)",
                    "< 18",
                    "[18, 30)",
                    "≥ 30"
                ],
                "title": "BMI",
                "value_mapping": "value/quantity/value"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Visits where measurements were performed",
                "group_by": "extra_properties/visit_index",
                "id": "measurement_visits",
                "mapping": "individual/phenopackets/measurements",
                "options": [
                    "1",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "2",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "3",
                    "30",
                    "31",
                    "32",
                    "33",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9"
                ],
                "title": "Recurring visits"
            },
            {
                "config": {
                    "bin_size": 50,
                    "maximum": 1000,
                    "minimum": 0,
                    "taper_left": 50,
                    "taper_right": 500,
                    "units": "years"
                },
                "datatype": "number",
                "description": "Measurements performed x",
                "group_by": "assay/label",
                "group_by_value": "Immunoglobulin E",
                "id": "measurement_immnoglobulin_e",
                "mapping": "individual/phenopackets/measurements",
                "options": [
                    "< 50",
                    "[50, 100)",
                    "[100, 150)",
                    "[150, 200)",
                    "[200, 250)",
                    "[250, 300)",
                    "[300, 350)",
                    "[350, 400)",
                    "[400, 450)",
                    "[450, 500)",
                    "≥ 500"
                ],
                "title": "Immunoglobulin E",
                "value_mapping": "value/quantity/value"
            },
            {
                "config": {
                    "bin_size": 10,
                    "maximum": 1000,
                    "minimum": 0,
                    "taper_left": 10,
                    "taper_right": 100,
                    "units": "years"
                },
                "datatype": "number",
                "description": "Measurements performed Cp20",
                "group_by": "assay/label",
                "group_by_value": "Cp20 Measurement",
                "id": "measurement_Cp20",
                "mapping": "individual/phenopackets/measurements",
                "options": [
                    "< 10",
                    "[10, 20)",
                    "[20, 30)",
                    "[30, 40)",
                    "[40, 50)",
                    "[50, 60)",
                    "[60, 70)",
                    "[70, 80)",
                    "[80, 90)",
                    "[90, 100)",
                    "≥ 100"
                ],
                "title": "Cp20",
                "value_mapping": "value/quantity/value"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Tissue from which the specimen was collected",
                "id": "sampled_tissue",
                "mapping": "individual/phenopackets/biosamples/sampled_tissue/label",
                "options": [
                    "Sputum-DTT plug",
                    "Cells from nasal brush-with reagent",
                    "Bronchoalveolar lavage supernatant aliquot",
                    "Sputum slide",
                    "Whole blood RNA",
                    "Blood cells",
                    "EDTA arterial plasma aliquot",
                    "Blood cells pellet",
                    "Nasal lavage or nasosorption supernatant",
                    "Urine aliquot",
                    "Sputum cells pellet",
                    "Nasal mucosa biopsy",
                    "DTT sputum supernatant aliquot",
                    "Cellules mononuclées isolées de sang périphérique (PBMC)",
                    "Buffy coat aliquot",
                    "Serum aliquot",
                    "Stools",
                    "Bronchial biopsies RNA",
                    "Plasma aliquot",
                    "Cells from nasal brush-dry",
                    "Buffycoat DNA",
                    "Nasal polyp biopsy",
                    "Macrophages RNA from bronchoalveolar lavage",
                    "Nasal secretion swab",
                    "EDTA whole blood aliquot",
                    "Sputum cells RNA",
                    "Bronchoalveolar lavage slide",
                    "Bronchial biopsy",
                    "Sputum supernatant aliquot without DTT",
                    "Venous serum aliquot",
                    "Optic Pathway",
                    "Parietal Lobe",
                    "Hypothalamus",
                    "Fronto-Temporal Lobe",
                    "Frontal Lobe",
                    "Cerebellum",
                    "Fronto-Parietal Lobe",
                    "Temporo-Occipital Lobe",
                    "Temporo-Parietal Lobe",
                    "Intraventricular",
                    "Fronto-Temporo-Insular",
                    "Unknown",
                    "Diencephalon",
                    "Brainstem",
                    "Cell Line",
                    "Supratentorial",
                    "Pineal",
                    "Thalamus",
                    "Ventricle",
                    "Hemisphere",
                    "Temporal Lobe",
                    "Ventricle (Lateral)",
                    "Suprasellar",
                    "Occipital Lobe",
                    "Mandible",
                    "Medulla Oblongata",
                    "Ventricle (Fourth)",
                    "Cerebellar Vermis",
                    "Ventricle (Third)",
                    "Cortex",
                    "Spinal Cord",
                    "Posterior Fossa",
                    "Optic Chiasm",
                    "Cerebello-Pontine Angle",
                    "Pons",
                    "Parieto-Occipital Lobe"
                ],
                "title": "Biosample Tissue Location"
            },
            {
                "config": {
                    "bin_by": "month"
                },
                "datatype": "date",
                "description": "Date of initial verbal consent (participant, legal representative or tutor), yyyy-mm-dd",
                "id": "date_of_consent",
                "mapping": "individual/extra_properties/date_of_consent",
                "options": [
                    "Jan 2020",
                    "Feb 2020",
                    "Mar 2020",
                    "Apr 2020",
                    "May 2020",
                    "Jun 2020",
                    "Jul 2020",
                    "Aug 2020",
                    "Sep 2020",
                    "Oct 2020",
                    "Nov 2020",
                    "Dec 2020",
                    "Jan 2021",
                    "Feb 2021",
                    "Mar 2021",
                    "Apr 2021",
                    "May 2021",
                    "Jun 2021",
                    "Jul 2021",
                    "Aug 2021",
                    "Sep 2021",
                    "Oct 2021",
                    "Nov 2021",
                    "Dec 2021",
                    "Jan 2022",
                    "Feb 2022",
                    "Mar 2022",
                    "Apr 2022",
                    "May 2022",
                    "Jun 2022",
                    "Jul 2022",
                    "Aug 2022",
                    "Sep 2022",
                    "Oct 2022",
                    "Nov 2022",
                    "Dec 2022",
                    "Jan 2023",
                    "Feb 2023",
                    "Mar 2023",
                    "Apr 2023",
                    "May 2023",
                    "Jun 2023",
                    "Jul 2023",
                    "Aug 2023",
                    "Sep 2023",
                    "Oct 2023",
                    "Nov 2023",
                    "Dec 2023"
                ],
                "title": "Verbal consent date"
            },
            {
                "config": {
                    "enum": [
                        "I have no problems in walking about",
                        "I have slight problems in walking about",
                        "I have moderate problems in walking about",
                        "I have severe problems in walking about",
                        "I am unable to walk about"
                    ]
                },
                "datatype": "string",
                "description": "Mobility",
                "id": "mobility",
                "mapping": "individual/extra_properties/mobility",
                "options": [
                    "I have no problems in walking about",
                    "I have slight problems in walking about",
                    "I have moderate problems in walking about",
                    "I have severe problems in walking about",
                    "I am unable to walk about"
                ],
                "title": "Functional status"
            },
            {
                "config": {
                    "enum": [
                        "Uninfected",
                        "Mild",
                        "Moderate",
                        "Severe",
                        "Dead"
                    ]
                },
                "datatype": "string",
                "description": "Covid severity",
                "id": "covid_severity",
                "mapping": "individual/extra_properties/covid_severity",
                "options": [
                    "Uninfected",
                    "Mild",
                    "Moderate",
                    "Severe",
                    "Dead"
                ],
                "title": "Covid severity"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Diseases observed as either present or absent",
                "id": "diseases",
                "mapping": "individual/phenopackets/diseases/term/label",
                "options": [
                    "viral pneumonia",
                    "Polycythemia vera",
                    "Non-Hodgkin Lymphoma",
                    "Hashimoto Thyroiditis",
                    "diabetes mellitus",
                    "Glioblastoma",
                    "coronary artery disease, autosomal dominant, 1",
                    "COVID-19",
                    "Rheumatologic disease",
                    "Marfan syndrome",
                    "Miller syndrome",
                    "Cystic fibrosis",
                    "Takotsubo cardiomyopathy",
                    "autoimmune disorder of cardiovascular system",
                    "Negative",
                    "Medulloblastoma",
                    "Testicular Cancer",
                    "Sarcoma",
                    "DIPG",
                    "Ovarian Tumor",
                    "Control",
                    "Neurofibromatosis",
                    "Desmoplastic infantile ganglioglioma (DIG)",
                    "GBM",
                    "HGG",
                    "Desmoplastic Infantile Astrocytoma (DIA)",
                    "Melanoma",
                    "Acute Lymphocytic Leukemia (ALL)",
                    "Ependymoma-PFB",
                    "Germinoma",
                    "Normal Brain",
                    "Schwannoma",
                    "Giant Cell Lesion (central)",
                    "Anaplastic Astrocytoma (AA)",
                    "Odontogenic Myxoma",
                    "Glioneuronal Tumor",
                    "Oligodendroglioma GrII",
                    "Craniopharyngioma",
                    "Ganglioglioma",
                    "Anaplastic Ependymoma",
                    "Brain Tumor",
                    "Neurofibroma",
                    "ATRT",
                    "Pilocytic Astrocytoma",
                    "Ependymoma-PFA",
                    "Angiosarcoma",
                    "DNET",
                    "Cemento Ossifying Fibroma",
                    "Meningioma",
                    "Diffuse Astrocytoma",
                    "Oral Granular Cell Tumor (OGCT)",
                    "Ewing's Sarcoma",
                    "HNSCC",
                    "Neuroblastoma",
                    "Acute Myeloid Leukemia (AML)",
                    "Parathyroid Tumor",
                    "Diffuse midline glioma, H3 K27M-mutant",
                    "Giant Cell Tumor (GCT)",
                    "Ependymoma - myxopapillary",
                    "Rhabdomyosarcoma",
                    "Glioma",
                    "Epithelioid Hemangioendothelioma",
                    "Endometrial Sarcoma",
                    "Giant Cell Lesion (peripheral)",
                    "Low Grade Glioma (LGG)",
                    "Astrocytoma",
                    "ETMR",
                    "Subcutaneous Panniculitis-like T-cell lymphoma",
                    "Giant Cell lesion",
                    "PNET",
                    "Anaplastic Oligoastrocytoma",
                    "Osteosarcoma",
                    "Pilomyxoid Astrocytoma (PMA)",
                    "Pleomorphic Xanthoastrocytoma (PXA)",
                    "Immunodeficiency",
                    "Cortical Dysplasia",
                    "Oligoastrocytoma",
                    "Anaplastic Oligodendroglioma",
                    "Ependymoma",
                    "Choroid Plexus Carcinoma",
                    "Oral Squamous Cell Carcinoma (OSCC)",
                    "Chondroblastoma"
                ],
                "title": "Diseases"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Tissue from which the biosample was extracted",
                "id": "tissues",
                "mapping": "biosample/sampled_tissue/label",
                "mapping_for_search_filter": "individual/biosamples/sampled_tissue/label",
                "options": [
                    "Plasma",
                    "blood",
                    "Serum"
                ],
                "title": "Sampled Tissues"
            },
            {
                "config": {
                    "bins": [
                        200,
                        300,
                        500,
                        1000,
                        1500,
                        2000
                    ],
                    "minimum": 0,
                    "units": "mg/L"
                },
                "datatype": "number",
                "description": "Numeric measures from a laboratory test",
                "id": "lab_test_result_value",
                "mapping": "individual/extra_properties/lab_test_result_value",
                "options": [
                    "< 200",
                    "[200, 300)",
                    "[300, 500)",
                    "[500, 1000)",
                    "[1000, 1500)",
                    "[1500, 2000)",
                    "≥ 2000"
                ],
                "title": "Lab Test Result"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "A clinical procedure performed on a subject",
                "group_by": "procedure/code/label",
                "id": "medical_procedures",
                "mapping": "individual/phenopackets/medical_actions",
                "options": [
                    "Liver Biopsy",
                    "Magnetic Resonance Imaging",
                    "Positron Emission Tomography",
                    "Punch Biopsy",
                    "X-Ray Imaging"
                ],
                "title": "Medical Procedures"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Treatment with an agent such as a drug",
                "group_by": "treatment/agent/label",
                "id": "medical_treatments",
                "mapping": "individual/phenopackets/medical_actions",
                "options": [
                    "Acetaminophen",
                    "Ibuprofen",
                    "NCIT:C1119"
                ],
                "title": "Medical Treatments"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Interpretation for an individual variant or gene (CANDIDATE, CONTRIBUTORY, etc)",
                "id": "interpretation_status",
                "mapping": "individual/phenopackets/interpretations/diagnosis/genomic_interpretations/interpretation_status",
                "options": [
                    "CONTRIBUTORY"
                ],
                "title": "Genomic Interpretations"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "ACMG Pathogenicity category for a particular variant (BENIGN, PATHOGENIC, etc)",
                "id": "acmg_pathogenicity_classification",
                "mapping": "individual/phenopackets/interpretations/diagnosis/genomic_interpretations/variant_interpretation/acmg_pathogenicity_classification",
                "options": [
                    "PATHOGENIC"
                ],
                "title": "Variant Pathogenicity"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Types of experiments performed on a sample",
                "id": "experiment_type",
                "mapping": "experiment/experiment_type",
                "mapping_for_search_filter": "individual/biosamples/experiment/experiment_type",
                "options": [
                    "Other",
                    "Neutralizing antibody titers",
                    "Metabolite profiling",
                    "RNA-Seq",
                    "WGS",
                    "Proteomic profiling",
                    "WES"
                ],
                "title": "Experiment Types"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "Study type of the experiment (e.g. Genomics, Transcriptomics, etc.)",
                "id": "experiment_study_type",
                "mapping": "experiment/study_type",
                "mapping_for_search_filter": "individual/biosamples/experiment/study_type",
                "options": [
                    "Serology",
                    "Other",
                    "Genomics",
                    "Proteomics",
                    "Transcriptomics",
                    "Metabolomics"
                ],
                "title": "Study Types"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "File type of experiment results files",
                "id": "experiment_results_file_type",
                "mapping": "experiment/experiment_results/file_format",
                "mapping_for_search_filter": "individual/biosamples/experiment/experiment_results/file_format",
                "options": [
                    "PDF",
                    "XLSX",
                    "JPEG",
                    "CRAM",
                    "VCF",
                    "MP4",
                    "DOCX",
                    "CSV",
                    "MARKDOWN"
                ],
                "title": "Results File Types"
            },
            {
                "config": {
                    "bin_by": "month"
                },
                "datatype": "date",
                "description": "Date of initial verbal consent (participant, legal representative or tutor)",
                "id": "dconsverbpa",
                "mapping": "individual/extra_properties/dconsverbpa",
                "options": [
                    "Mar 2020",
                    "Apr 2020",
                    "May 2020",
                    "Jun 2020",
                    "Jul 2020",
                    "Aug 2020",
                    "Sep 2020",
                    "Oct 2020",
                    "Nov 2020",
                    "Dec 2020",
                    "Jan 2021",
                    "Feb 2021",
                    "Mar 2021",
                    "Apr 2021",
                    "May 2021",
                    "Jun 2021",
                    "Jul 2021",
                    "Aug 2021",
                    "Sep 2021",
                    "Oct 2021",
                    "Nov 2021",
                    "Dec 2021",
                    "Jan 2022",
                    "Feb 2022",
                    "Mar 2022",
                    "Apr 2022",
                    "May 2022",
                    "Jun 2022",
                    "Jul 2022",
                    "Aug 2022",
                    "Sep 2022",
                    "Oct 2022",
                    "Nov 2022",
                    "Dec 2022",
                    "Jan 2023",
                    "Feb 2023",
                    "Mar 2023",
                    "Apr 2023",
                    "May 2023",
                    "Jun 2023",
                    "Jul 2023",
                    "Aug 2023"
                ],
                "title": "Verbal consent date"
            },
            {
                "config": {
                    "enum": [
                        "Hospitalized",
                        "Outpatient"
                    ]
                },
                "datatype": "string",
                "description": "Has the participant been hospitalized or is the participant seen as an outpatient?",
                "id": "type_partic",
                "mapping": "individual/extra_properties/type_partic",
                "options": [
                    "Hospitalized",
                    "Outpatient"
                ],
                "title": "Hospitalization"
            },
            {
                "config": {
                    "enum": [
                        "Non-smoker",
                        "Smoker",
                        "Former smoker",
                        "Passive smoker",
                        "Not specified"
                    ]
                },
                "datatype": "string",
                "description": "Smoking status",
                "id": "smoking",
                "mapping": "individual/extra_properties/smoking",
                "options": [
                    "Non-smoker",
                    "Smoker",
                    "Former smoker",
                    "Passive smoker",
                    "Not specified"
                ],
                "title": "Smoking"
            },
            {
                "config": {
                    "enum": [
                        "Positive",
                        "Negative",
                        "Indeterminate"
                    ]
                },
                "datatype": "string",
                "description": "Final COVID status according to the PCR test",
                "id": "covidstatus",
                "mapping": "individual/extra_properties/covidstatus",
                "options": [
                    "Positive",
                    "Negative",
                    "Indeterminate"
                ],
                "title": "COVID status"
            },
            {
                "config": {
                    "enum": [
                        "Alive",
                        "Deceased"
                    ]
                },
                "datatype": "string",
                "description": "Vital status at discharge",
                "id": "death_dc",
                "mapping": "individual/extra_properties/death_dc",
                "options": [
                    "Alive",
                    "Deceased"
                ],
                "title": "Vital status"
            },
            {
                "config": {
                    "bins": [
                        20,
                        25,
                        27,
                        30,
                        35,
                        40
                    ],
                    "units": "kg/m^2"
                },
                "datatype": "number",
                "description": "BMI",
                "id": "bmi",
                "mapping": "individual/extra_properties/bmi",
                "options": [
                    "< 20",
                    "[20, 25)",
                    "[25, 27)",
                    "[27, 30)",
                    "[30, 35)",
                    "[35, 40)",
                    "≥ 40"
                ],
                "title": "BMI"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Intensive Care Unit admission?",
                "id": "icu",
                "mapping": "individual/extra_properties/icu",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "ICU"
            },
            {
                "config": {
                    "enum": [
                        "Hospitalized adult",
                        "Adult outpatient",
                        "Pediatric",
                        "Pregnant woman"
                    ]
                },
                "datatype": "string",
                "description": "To which category the participant belongs?",
                "id": "core_cohorte",
                "mapping": "individual/extra_properties/core_cohorte",
                "options": [
                    "Hospitalized adult",
                    "Adult outpatient",
                    "Pediatric",
                    "Pregnant woman"
                ],
                "title": "Participant category"
            },
            {
                "config": {
                    "enum": [
                        "At home",
                        "In residence for the elderly (RPA)",
                        "Nursing home (CHSLD)",
                        "In intermediate and family-type resources",
                        "In rooming house",
                        "Homeless"
                    ]
                },
                "datatype": "string",
                "description": "Living where?",
                "id": "livewhere",
                "mapping": "individual/extra_properties/livewhere",
                "options": [
                    "At home",
                    "In residence for the elderly (RPA)",
                    "Nursing home (CHSLD)",
                    "In intermediate and family-type resources",
                    "In rooming house",
                    "Homeless"
                ],
                "title": "Domicile"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Has the participant been vaccinated?",
                "id": "vaccinate",
                "mapping": "individual/extra_properties/vaccinate",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Vaccinal status"
            },
            {
                "config": {
                    "enum": [
                        "1",
                        "2",
                        "3",
                        "4"
                    ]
                },
                "datatype": "string",
                "description": "Number of doses received",
                "id": "vaccin_dosenum",
                "mapping": "individual/extra_properties/vaccin_dosenum",
                "options": [
                    "1",
                    "2",
                    "3",
                    "4"
                ],
                "title": "Vaccine dose"
            },
            {
                "config": {
                    "enum": [
                        "I have no problem washing or dressing myself",
                        "I have slight problem washing or dressing myself",
                        "I have moderate problems washing or dressing myself",
                        "I have severe problems washing or dressing myself",
                        "I am unable to wash or dress myself"
                    ]
                },
                "datatype": "string",
                "description": "Self-care",
                "id": "selfcare",
                "mapping": "individual/extra_properties/selfcare",
                "options": [
                    "I have no problem washing or dressing myself",
                    "I have slight problem washing or dressing myself",
                    "I have moderate problems washing or dressing myself",
                    "I have severe problems washing or dressing myself",
                    "I am unable to wash or dress myself"
                ],
                "title": "Self-care"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Other chronic cardiac disease?",
                "id": "phx_cardiac",
                "mapping": "individual/extra_properties/phx_cardiac",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Cardiac history"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Prior transient ischemic attack (TIA)?",
                "id": "phx_tia",
                "mapping": "individual/extra_properties/phx_tia",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "TIA"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Asthma?",
                "id": "phx_asthma",
                "mapping": "individual/extra_properties/phx_asthma",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Asthma"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Prior stroke?",
                "id": "phx_cva",
                "mapping": "individual/extra_properties/phx_cva",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Stroke"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Diabetes?",
                "id": "phx_diabetes",
                "mapping": "individual/extra_properties/phx_diabetes",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Diabetes"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Malignant neoplasm?",
                "id": "phx_cancer",
                "mapping": "individual/extra_properties/phx_cancer",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Cancer"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Dementia?",
                "id": "phx_dementia",
                "mapping": "individual/extra_properties/phx_dementia",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Dementia"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Atrial fibrillation or flutter?",
                "id": "phx_afib",
                "mapping": "individual/extra_properties/phx_afib",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Atrial fibrillation"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "HIV or AIDS?",
                "id": "phx_hiv",
                "mapping": "individual/extra_properties/phx_hiv",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "HIV"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Arterial Hypertension?",
                "id": "phx_htn",
                "mapping": "individual/extra_properties/phx_htn",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Arterial Hypertension"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Immunosuppressed state?",
                "id": "phx_imm",
                "mapping": "individual/extra_properties/phx_imm",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Immunosupression"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Prior myocardial infarction?",
                "id": "phx_mi",
                "mapping": "individual/extra_properties/phx_mi",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Myocardial infarction"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Heart failure?",
                "id": "phx_chf",
                "mapping": "individual/extra_properties/phx_chf",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Heart failure"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Coronary artery disease?",
                "id": "phx_cad",
                "mapping": "individual/extra_properties/phx_cad",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Coronary artery disease"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Liver disease?",
                "id": "phx_liver",
                "mapping": "individual/extra_properties/phx_liver",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Liver disease"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Chronic obstructive pulmonary disease (emphysema, chronic bronchitis)?",
                "id": "phx_copd",
                "mapping": "individual/extra_properties/phx_copd",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "COPD"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Psychiatric disease?",
                "id": "phx_psych",
                "mapping": "individual/extra_properties/phx_psych",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Psychiatric disease"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Chronic kidney disease?",
                "id": "phx_ckd",
                "mapping": "individual/extra_properties/phx_ckd",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Chronic kidney disease"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Dialysis?",
                "id": "phx_dialysis",
                "mapping": "individual/extra_properties/phx_dialysis",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Dialysis"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Rheumatologic disease?",
                "id": "phx_rheum",
                "mapping": "individual/extra_properties/phx_rheum",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Rheumatologic disease"
            },
            {
                "config": {
                    "bins": [
                        5,
                        10,
                        50,
                        100
                    ],
                    "units": "mg/L"
                },
                "datatype": "number",
                "description": "C-reactive protein (CRP)",
                "id": "lab_crp",
                "mapping": "individual/extra_properties/lab_crp",
                "options": [
                    "< 5",
                    "[5, 10)",
                    "[10, 50)",
                    "[50, 100)",
                    "≥ 100"
                ],
                "title": "CRP"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Chest X-ray?",
                "id": "cxr",
                "mapping": "individual/extra_properties/cxr",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Chest X-ray"
            },
            {
                "config": {
                    "bins": [
                        4,
                        10,
                        15
                    ],
                    "units": "×10^9/L"
                },
                "datatype": "number",
                "description": "Total White Blood Cell (WBC) count",
                "id": "lab_wbc",
                "mapping": "individual/extra_properties/lab_wbc",
                "options": [
                    "< 4",
                    "[4, 10)",
                    "[10, 15)",
                    "≥ 15"
                ],
                "title": "WBC"
            },
            {
                "config": {
                    "bins": [
                        70,
                        90,
                        110,
                        130,
                        150
                    ],
                    "units": "g/L"
                },
                "datatype": "number",
                "description": "Haemoglobin",
                "id": "lab_hg",
                "mapping": "individual/extra_properties/lab_hg",
                "options": [
                    "< 70",
                    "[70, 90)",
                    "[90, 110)",
                    "[110, 130)",
                    "[130, 150)",
                    "≥ 150"
                ],
                "title": "Haemoglobin"
            },
            {
                "config": {
                    "bins": [
                        50,
                        90,
                        120,
                        200,
                        300
                    ],
                    "units": "μmol/L"
                },
                "datatype": "number",
                "description": "Creatinine",
                "id": "lab_cr",
                "mapping": "individual/extra_properties/lab_cr",
                "options": [
                    "< 50",
                    "[50, 90)",
                    "[90, 120)",
                    "[120, 200)",
                    "[200, 300)",
                    "≥ 300"
                ],
                "title": "Creatinine"
            },
            {
                "config": {
                    "bins": [
                        200,
                        300,
                        500,
                        1000,
                        1500,
                        2000
                    ],
                    "units": "ng/mL"
                },
                "datatype": "number",
                "description": "NT-proBNP",
                "id": "lab_ntprobnp",
                "mapping": "individual/extra_properties/lab_ntprobnp",
                "options": [
                    "< 200",
                    "[200, 300)",
                    "[300, 500)",
                    "[500, 1000)",
                    "[1000, 1500)",
                    "[1500, 2000)",
                    "≥ 2000"
                ],
                "title": "NT-proBNP"
            },
            {
                "config": {
                    "bins": [
                        200,
                        500,
                        1000,
                        1500,
                        2000
                    ],
                    "units": "U/L"
                },
                "datatype": "number",
                "description": "Lactate Dehydrogenase",
                "id": "lab_ldh",
                "mapping": "individual/extra_properties/lab_ldh",
                "options": [
                    "< 200",
                    "[200, 500)",
                    "[500, 1000)",
                    "[1000, 1500)",
                    "[1500, 2000)",
                    "≥ 2000"
                ],
                "title": "LDH"
            },
            {
                "config": {
                    "bins": [
                        500,
                        1000,
                        2000,
                        5000
                    ],
                    "units": "μg/L"
                },
                "datatype": "number",
                "description": "D-Dimer",
                "id": "lab_ddimer",
                "mapping": "individual/extra_properties/lab_ddimer",
                "options": [
                    "< 500",
                    "[500, 1000)",
                    "[1000, 2000)",
                    "[2000, 5000)",
                    "≥ 5000"
                ],
                "title": "D-Dimer"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Did or does the patient receive ventilatory support?",
                "id": "repsupport_yesno",
                "mapping": "individual/extra_properties/repsupport_yesno",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Respiratory support"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Have you been diagnosed with a new or recurrent case of COVID since your last follow-up?",
                "id": "newcovid",
                "mapping": "individual/extra_properties/newcovid",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Reinfection"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Does the participant report persistent symptoms related to SARS-CoV-2 infection?",
                "id": "sx_report",
                "mapping": "individual/extra_properties/sx_report",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Persisting symptoms"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No",
                        "Not available"
                    ]
                },
                "datatype": "string",
                "description": "Systemic corticosteroid?",
                "id": "rx_roid",
                "mapping": "individual/extra_properties/rx_roid",
                "options": [
                    "Yes",
                    "No",
                    "Not available"
                ],
                "title": "Systemic corticosteroid"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No",
                        "Not available"
                    ]
                },
                "datatype": "string",
                "description": "Antocoagulants?",
                "id": "rx_aco",
                "mapping": "individual/extra_properties/rx_aco",
                "options": [
                    "Yes",
                    "No",
                    "Not available"
                ],
                "title": "Antocoagulants"
            },
            {
                "config": {
                    "enum": [
                        "Worse",
                        "Same",
                        "Better",
                        "Indeterminate"
                    ]
                },
                "datatype": "string",
                "description": "Ability to self-care at discharge versus pre-COVID",
                "id": "selfcare_dc",
                "mapping": "individual/extra_properties/selfcare_dc",
                "options": [
                    "Worse",
                    "Same",
                    "Better",
                    "Indeterminate"
                ],
                "title": "Self-care post covid"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Acute kidney injury?",
                "id": "c_aki",
                "mapping": "individual/extra_properties/c_aki",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Acute kidney injury"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Acute Respiratory Distress Syndrome (ARDS)?",
                "id": "c_ards",
                "mapping": "individual/extra_properties/c_ards",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "ARDS"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Deep vein thrombosis (DVT)?",
                "id": "c_dvt",
                "mapping": "individual/extra_properties/c_dvt",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Deep vein thrombosis"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Stroke?",
                "id": "c_stroke",
                "mapping": "individual/extra_properties/c_stroke",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Stroke"
            },
            {
                "config": {
                    "enum": [
                        "Yes",
                        "No"
                    ]
                },
                "datatype": "string",
                "description": "Pulmonary embolism?",
                "id": "c_pe",
                "mapping": "individual/extra_properties/c_pe",
                "options": [
                    "Yes",
                    "No"
                ],
                "title": "Pulmonary embolism"
            },
            {
                "config": {
                    "enum": None
                },
                "datatype": "string",
                "description": "The type of molecule that was extracted from the biological material.",
                "id": "molecule",
                "mapping": "experiment/molecule",
                "mapping_for_search_filter": "individual/phenopackets/biosamples/experiment/molecule",
                "options": [
                    "genomic DNA"
                ],
                "title": "Molecules Used"
            }
        ]
    }
]















# KATSU_CONFIG_UNION = [
#     {
#         "section_title": "General",
#         "fields": [
#             {
#                 "mapping": "individual/age_numeric",
#                 "title": "Age",
#                 "description": "Age at arrival",
#                 "datatype": "number",
#                 "config": {
#                     "bin_size": 10,
#                     "taper_left": 10,
#                     "taper_right": 100,
#                     "units": "years",
#                     "minimum": 0,
#                     "maximum": 100,
#                 },
#                 "id": "age",
#                 "options": [
#                     "< 10",
#                     "[10, 20)",
#                     "[20, 30)",
#                     "[30, 40)",
#                     "[40, 50)",
#                     "[50, 60)",
#                     "[60, 70)",
#                     "[70, 80)",
#                     "[80, 90)",
#                     "[90, 100)",
#                 ],
#             },
#             {
#                 "mapping": "individual/sex",
#                 "title": "Sex",
#                 "description": "Sex at birth",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "sex",
#                 "options": ["MALE", "FEMALE"],
#             },
#             {
#                 "mapping": "individual/extra_properties/date_of_consent",
#                 "title": "Verbal consent date",
#                 "description": "Date of initial verbal consent (participant, legal representative or tutor), yyyy-mm-dd",
#                 "datatype": "date",
#                 "config": {"bin_by": "month"},
#                 "id": "date_of_consent",
#                 "options": [
#                     "Jan 2020",
#                     "Feb 2020",
#                     "Mar 2020",
#                     "Apr 2020",
#                     "May 2020",
#                     "Jun 2020",
#                     "Jul 2020",
#                     "Aug 2020",
#                     "Sep 2020",
#                     "Oct 2020",
#                     "Nov 2020",
#                     "Dec 2020",
#                     "Jan 2021",
#                     "Feb 2021",
#                     "Mar 2021",
#                     "Apr 2021",
#                     "May 2021",
#                     "Jun 2021",
#                     "Jul 2021",
#                     "Aug 2021",
#                     "Sep 2021",
#                     "Oct 2021",
#                     "Nov 2021",
#                     "Dec 2021",
#                     "Jan 2022",
#                     "Feb 2022",
#                     "Mar 2022",
#                     "Apr 2022",
#                     "May 2022",
#                     "Jun 2022",
#                     "Jul 2022",
#                     "Aug 2022",
#                     "Sep 2022",
#                     "Oct 2022",
#                     "Nov 2022",
#                     "Dec 2022",
#                     "Jan 2023",
#                     "Feb 2023",
#                     "Mar 2023",
#                     "Apr 2023",
#                     "May 2023",
#                     "Jun 2023",
#                     "Jul 2023",
#                     "Aug 2023",
#                     "Sep 2023",
#                     "Oct 2023",
#                     "Nov 2023",
#                     "Dec 2023",
#                 ],
#             },
#             {
#                 "mapping": "individual/extra_properties/mobility",
#                 "title": "Functional status",
#                 "description": "Mobility",
#                 "datatype": "string",
#                 "config": {
#                     "enum": [
#                         "I have no problems in walking about",
#                         "I have slight problems in walking about",
#                         "I have moderate problems in walking about",
#                         "I have severe problems in walking about",
#                         "I am unable to walk about",
#                     ]
#                 },
#                 "id": "mobility",
#                 "options": [
#                     "I have no problems in walking about",
#                     "I have slight problems in walking about",
#                     "I have moderate problems in walking about",
#                     "I have severe problems in walking about",
#                     "I am unable to walk about",
#                 ],
#             },
#             {
#                 "mapping": "individual/extra_properties/covid_severity",
#                 "title": "Covid severity",
#                 "description": "Covid severity",
#                 "datatype": "string",
#                 "config": {"enum": ["Uninfected", "Mild", "Moderate", "Severe", "Dead"]},
#                 "id": "covid_severity",
#                 "options": ["Uninfected", "Mild", "Moderate", "Severe", "Dead"],
#             },
#             {
#                 "mapping": "individual/phenopackets/phenotypic_features/pftype/label",
#                 "title": "Phenotypic Features",
#                 "description": "Individual phenotypic features, observed as either present or absent",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "phenotypic_features",
#                 "options": [
#                     "Loss of appetite",
#                     "Asthma",
#                     "Abdominal pain",
#                     "Headache",
#                     "Cough",
#                     "Cardiac arrest",
#                     "Nausea",
#                     "Pulmonary hypertension",
#                     "Viral pneumonia/pneumonitis",
#                     "HIV Infection",
#                     "Hyperglycemia",
#                     "Patient immunosuppressed",
#                     "Fever",
#                     "Chest pain",
#                     "Pneumothorax",
#                     "Hypertension",
#                     "Dementia",
#                     "Loss of sense of smell",
#                 ],
#             },
#             {
#                 "mapping": "individual/phenopackets/diseases/term/label",
#                 "title": "Diseases",
#                 "description": "Diseases observed as either present or absent",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "diseases",
#                 "options": [
#                     "viral pneumonia",
#                     "Glioblastoma",
#                     "Polycythemia vera",
#                     "Miller syndrome",
#                     "Cystic fibrosis",
#                     "coronary artery disease, autosomal dominant, 1",
#                     "Hashimoto Thyroiditis",
#                     "Rheumatologic disease",
#                     "Takotsubo cardiomyopathy",
#                     "autoimmune disorder of cardiovascular system",
#                     "COVID-19",
#                     "Marfan syndrome",
#                     "Non-Hodgkin Lymphoma",
#                     "diabetes mellitus",
#                 ],
#             },
#             {
#                 "mapping": "biosample/sampled_tissue/label",
#                 "mapping_for_search_filter": "individual/biosamples/sampled_tissue/label",
#                 "title": "Sampled Tissues",
#                 "description": "Tissue from which the biosample was extracted",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "tissues",
#                 "options": ["Plasma", "blood", "Serum"],
#             },
#         ],
#     },
#     {
#         "section_title": "Measurements",
#         "fields": [
#             {
#                 "mapping": "individual/extra_properties/lab_test_result_value",
#                 "title": "Lab Test Result",
#                 "description": "Numeric measures from a laboratory test",
#                 "datatype": "number",
#                 "config": {"bins": [200, 300, 500, 1000, 1500, 2000], "minimum": 0, "units": "mg/L"},
#                 "id": "lab_test_result_value",
#                 "options": [
#                     "< 200",
#                     "[200, 300)",
#                     "[300, 500)",
#                     "[500, 1000)",
#                     "[1000, 1500)",
#                     "[1500, 2000)",
#                     "≥ 2000",
#                 ],
#             },
#             {
#                 "mapping": "individual/phenopackets/measurements",
#                 "group_by": "assay/id",
#                 "group_by_value": "NCIT:C16358",
#                 "value_mapping": "value/quantity/value",
#                 "title": "BMI",
#                 "description": "Body Mass Index",
#                 "datatype": "number",
#                 "config": {"bins": [18.5, 30], "minimum": 0, "units": "kg/m^2"},
#                 "id": "bmi",
#                 "options": ["< 18", "[18, 30)", "≥ 30"],
#             },
#         ],
#     },
#     {
#         "section_title": "Medical Actions",
#         "fields": [
#             {
#                 "mapping": "individual/phenopackets/medical_actions",
#                 "group_by": "procedure/code/label",
#                 "title": "Medical Procedures",
#                 "description": "A clinical procedure performed on a subject",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "medical_procedures",
#                 "options": [
#                     "Liver Biopsy",
#                     "Magnetic Resonance Imaging",
#                     "Positron Emission Tomography",
#                     "Punch Biopsy",
#                     "X-Ray Imaging",
#                 ],
#             },
#             {
#                 "mapping": "individual/phenopackets/medical_actions",
#                 "group_by": "treatment/agent/label",
#                 "title": "Medical Treatments",
#                 "description": "Treatment with an agent such as a drug",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "medical_treatments",
#                 "options": ["Acetaminophen", "Ibuprofen", "Ondansetron"],
#             },
#         ],
#     },
#     {
#         "section_title": "Interpretations",
#         "fields": [
#             {
#                 "mapping": "individual/phenopackets/interpretations/diagnosis/genomic_interpretations/interpretation_status",
#                 "title": "Genomic Interpretations",
#                 "description": "Interpretation for an individual variant or gene (CANDIDATE, CONTRIBUTORY, etc)",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "interpretation_status",
#                 "options": ["CONTRIBUTORY"],
#             },
#             {
#                 "mapping": "individual/phenopackets/interpretations/diagnosis/genomic_interpretations/variant_interpretation/acmg_pathogenicity_classification",
#                 "title": "Variant Pathogenicity",
#                 "description": "ACMG Pathogenicity category for a particular variant (BENIGN, PATHOGENIC, etc)",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "acmg_pathogenicity_classification",
#                 "options": ["PATHOGENIC"],
#             },
#         ],
#     },
#     {
#         "section_title": "Experiments",
#         "fields": [
#             {
#                 "mapping": "experiment/experiment_type",
#                 "mapping_for_search_filter": "individual/biosamples/experiment/experiment_type",
#                 "title": "Experiment Types",
#                 "description": "Types of experiments performed on a sample",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "experiment_type",
#                 "options": [
#                     "Other",
#                     "Neutralizing antibody titers",
#                     "Metabolite profiling",
#                     "RNA-Seq",
#                     "WGS",
#                     "Proteomic profiling",
#                 ],
#             },
#             {
#                 "mapping": "experiment/study_type",
#                 "mapping_for_search_filter": "individual/biosamples/experiment/study_type",
#                 "title": "Study Types",
#                 "description": "Study type of the experiment (e.g. Genomics, Transcriptomics, etc.)",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "experiment_study_type",
#                 "options": ["Serology", "Genomics", "Other", "Proteomics", "Transcriptomics", "Metabolomics"],
#             },
#             {
#                 "mapping": "experiment/experiment_results/file_format",
#                 "mapping_for_search_filter": "individual/biosamples/experiment/experiment_results/file_format",
#                 "title": "Results File Types",
#                 "description": "File type of experiment results files",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "experiment_results_file_type",
#                 "options": ["XLSX", "CRAM", "VCF", "JPEG", "MP4", "DOCX", "CSV", "MARKDOWN"],
#             },
#         ],
#     },
# ]

# KATSU_CONFIG_INTERSECTION = [
#     {
#         "section_title": "General",
#         "fields": [
#             {
#                 "mapping": "individual/age_numeric",
#                 "title": "Age",
#                 "description": "Age at arrival",
#                 "datatype": "number",
#                 "config": {
#                     "bin_size": 10,
#                     "taper_left": 10,
#                     "taper_right": 100,
#                     "units": "years",
#                     "minimum": 0,
#                     "maximum": 100,
#                 },
#                 "id": "age",
#                 "options": [
#                     "< 10",
#                     "[10, 20)",
#                     "[20, 30)",
#                     "[30, 40)",
#                     "[40, 50)",
#                     "[50, 60)",
#                     "[60, 70)",
#                     "[70, 80)",
#                     "[80, 90)",
#                     "[90, 100)",
#                 ],
#             },
#             {
#                 "mapping": "individual/sex",
#                 "title": "Sex",
#                 "description": "Sex at birth",
#                 "datatype": "string",
#                 "config": {"enum": None},
#                 "id": "sex",
#                 "options": ["MALE", "FEMALE"],
#             },
#         ],
#     },
# ]
