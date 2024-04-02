import os.path
from http import HTTPStatus
from http.client import HTTPResponse

from cvat_sdk.api_client import ApiClient
from cvat_sdk.core.helpers import get_paginated_collection

from time import sleep

MAX_RETRIES = 500
RETRY_INTERVAL = 5


def get_tasks(api_client: ApiClient, project_ids, status, skip_tasks_ids):
    with api_client:
        try:
            projects = get_paginated_collection(api_client.projects_api.list_endpoint)
            projects_map = {p.id: p for p in projects if p.id in project_ids}
            return [[projects_map[project_id], task]
                    for project_id in project_ids
                    for task in
                    get_paginated_collection(api_client.tasks_api.list_endpoint, status=status,
                                             project_id=int(project_id)) if task.id not in skip_tasks_ids]
        except Exception as e:
            print(f"Error: {e}")
            raise Exception(f"Error: {e}")


def export_task(api_client, task_id, export_format, location_path):
    with api_client:
        try:
            _export_dataset(api_client, task_id, export_format, location_path)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


def _export_dataset(api_client: ApiClient,
                    task_id,
                    export_format,
                    file_name) -> HTTPResponse:
    for _ in range(MAX_RETRIES):
        (_, response) = api_client.tasks_api.retrieve_dataset(id=task_id,
                                                              format=export_format,
                                                              _parse_response=False)
        if response.status == HTTPStatus.CREATED:
            break
        if not response.status == HTTPStatus.ACCEPTED:
            raise Exception(f"response.status not {HTTPStatus.ACCEPTED}")
        sleep(RETRY_INTERVAL)
    if not response.status == HTTPStatus.CREATED:
        raise Exception(f"response.status not {HTTPStatus.CREATED}")

    (_, response) = api_client.tasks_api.retrieve_dataset(id=task_id,
                                                          format=export_format,
                                                          action="download",
                                                          _parse_response=False)
    if response.status == HTTPStatus.OK:
        _save_zip(response, file_name)

    return response


def _save_zip(response, file_name, chunk_size=100):
    with open(file_name, 'wb') as out:
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            out.write(data)
    response.release_conn()
