import requests
import json
import io


def get_tcga_projects():
    endpoint = "https://api.gdc.cancer.gov/projects"

    response = requests.get(endpoint, params={"size": "2000"})
    data = response.json()

    # retrieve only TCGA projects
    return [
        project["id"] for project in data["data"]["hits"] if "TCGA" in project["id"]
    ]


def map_file_name_to_file_uuid(file_name: str):
    filename_to_id = {}

    with open(file_name, 'r') as file:
        next(file)
        
        for line in file:
            columns = line.strip().split('\t')
            filename_to_id[columns[1]] = columns[0]

    return filename_to_id


def get_uuid_from_manifest(file_name: str):
    with open(file_name, "r") as file:
        return [line.split("\t")[0] for line in file.readlines()[1:]]


def generate_manifest_file(file_uuids: list, file_name: str):
    endpoint = "https://api.gdc.cancer.gov/manifest"

    response = requests.post(
        endpoint,
        headers={"Content-Type": "application/json", "Accept": "application/tsv"},
        json={"ids": file_uuids},
    )

    if response.status_code == 200:
        with open(file_name, "w") as file:
            file.write(response.text)
    else:
        print("Request failed with status code ", response.status_code)


def map_file_uuid_to_sample_id(file_uuids: list):
    endpoint = "https://api.gdc.cancer.gov/files"

    filters = {
        "op": "in",
        "content":{
            "field": "file_id",
            "value": file_uuids 
            }
        }

    params = {
        "filters": json.dumps(filters),
        "fields": "cases.samples.sample_id,cases.samples.submitter_id", # the fields you want to retrieve
        "format": "JSON",
        "size": "10000",
        }

    response = requests.post(endpoint, json=params)
    data = response.json()

    # use submitter_id instead of sample_id
    return {file["id"]: file['cases'][0]['samples'][0]['submitter_id'] for file in data["data"]["hits"]}


def get_uuids_for_expression_data_files(project_id: str):
    endpoint = "https://api.gdc.cancer.gov/files"

    filters = {
        "op": "and",
        "content": [
            {
                "content": {"field": "cases.project.project_id", "value": [project_id]},
                "op": "in",
            },
            {
                "op": "in",
                "content": {"field": "cases.project.program.name", "value": ["TCGA"]},
            },
            {
                "op": "in",
                "content": {
                    "field": "files.analysis.workflow_type",
                    "value": ["STAR - Counts"],
                },
            },
            {
                "content": {
                    "field": "files.data_category",
                    "value": ["Transcriptome Profiling"],
                },
                "op": "in",
            },
            {"op": "in", "content": {"field": "files.data_format", "value": ["tsv"]}},
            {
                "op": "in",
                "content": {
                    "field": "files.data_type",
                    "value": ["Gene Expression Quantification"],
                },
            },
            {
                "op": "in",
                "content": {
                    "field": "files.experimental_strategy",
                    "value": ["RNA-Seq"],
                },
            },
        ],
    }
    response = requests.get(
        endpoint,
        params={
            "filters": json.dumps(filters),
            "fields": "file_id",
            "format": "JSON",
            "size": "10000",
        },
    )

    data = response.json()
    return [file["id"] for file in data["data"]["hits"]]


def get_uuids_for_clinical_data_files(project_id: str):
    endpoint = "https://api.gdc.cancer.gov/files"

    filters = {
        "op": "and",
        "content": [
            {
                "content": {"field": "cases.project.project_id", "value": [project_id]},
                "op": "in",
            },
            {
                "op": "in",
                "content": {"field": "cases.project.program.name", "value": ["TCGA"]},
            },
            {
                "op": "in",
                "content": {
                    "field": "files.data_category",
                    "value": ["clinical"],
                },
            },
            {
                "op": "in",
                "content": {"field": "files.data_format", "value": ["bcr xml"]},
            },
            {
                "op": "in",
                "content": {
                    "field": "files.data_type",
                    "value": ["Clinical Supplement"],
                },
            },
        ],
    }


    response = requests.get(
        endpoint,
        params={
            "filters": json.dumps(filters),
            "fields": "file_id",
            "format": "JSON",
            "size": "10000",
        },
    )

    data = response.json()
    return [file["id"] for file in data["data"]["hits"]]


def download_files(file_uuids: list):
    endpoint = "https://api.gdc.cancer.gov/data"

    response = requests.post(
        endpoint,
        data=json.dumps({"ids": file_uuids}),
        headers={"Content-Type": "application/json"},
    )

    # import re
    # response_head_cd = response.headers["Content-Disposition"]

    # file_name = re.findall("filename=(.+)", response_head_cd)[0]

    # with open(file_name, "wb") as output_file:
    #     output_file.write(response.content)
    
    # Create and return a BytesIO object from the response content
    return io.BytesIO(response.content)