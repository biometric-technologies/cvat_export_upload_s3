from pathlib import Path

from dotenv import dotenv_values
from minio import Minio
import os
from cvat_utils import get_tasks, export_task
from minio_utils import get_tasks_csv, upload_tasks_csv, upload_file
from cvat_sdk.api_client import Configuration, ApiClient
from utils import str_to_bool
import argparse

parser = argparse.ArgumentParser('Export annotations', add_help=False)
parser.add_argument('--config_env', default='.env', type=str, help="Path to .evn config")
args = parser.parse_args()

print("Start sync data")
env_vars = dotenv_values(args.config_env)

minio_client = Minio(env_vars["MINIO_URL"],
                     access_key=env_vars["MINIO_ACCESS_KEY"],
                     secret_key=env_vars["MINIO_SECRET_KEY"],
                     secure=str_to_bool(env_vars["MINIO_SECURE"]))
cvat_client = ApiClient(
    Configuration(
        host=env_vars["CVAT_URL"],
        username=env_vars["CVAT_USERNAME"],
        password=env_vars["CVAT_PASSWORD"],
    )
)
export_format = env_vars["CVAT_EXPORT_FORMAT"]
project_ids = [int(id) for id in env_vars["CVAT_PROJECT_IDS"].split(',')]
skip_task_ids = [int(id) for id in env_vars["CVAT_TASKS_SKIP_IDS"].split(',')]
status = env_vars["CVAT_TASK_STATUS"]

bucket = env_vars["MINIO_BUCKET"]
bucket_dir = env_vars["MINIO_DIR"]
csv_object_name = f'{bucket_dir}/backup.csv'

tasks_csv = get_tasks_csv(minio_client, bucket, csv_object_name)
print('Retrieved sync data')
print(tasks_csv)

synced_ids = tasks_csv['Task Id'].tolist()
print('Synced Tasks:', synced_ids)

tasks_to_sync = get_tasks(cvat_client, project_ids, status, skip_task_ids + synced_ids)
print(f'Found {len(tasks_to_sync)} tasks to sync:', [t.name for _, t in tasks_to_sync])

synced_count = 0
for p, t in tasks_to_sync:
    export_path = f'.tmp/task_{t.id}.zip'
    Path(export_path).parent.mkdir(parents=True, exist_ok=True)
    print(f'Downloading task {t.name} data in format {export_format}')
    exported = export_task(cvat_client, t.id, export_format, export_path)
    if exported:
        object_name = f'{bucket_dir}/project_{t.project_id}/task_{t.id}.zip'
        print(f'Uploading task {t.name} to {object_name}')
        uploaded = upload_file(minio_client, bucket, object_name, export_path)
        if uploaded:
            tasks_csv.loc[len(tasks_csv)] = [p.id, t.id, p.name, t.name, t.status, object_name]
            synced_count += 1
            print(f'Task {t.name} successfully synced')
        else:
            print("Skipping task because of upload error", t.name)
    else:
        print("Skipping task because of export error", t.name)

if synced_count > 0:
    print('Uploading synced csv data')
    upload_tasks_csv(minio_client, bucket, csv_object_name, tasks_csv)
    print(tasks_csv)
else:
    print("No tasks were synced")

if os.path.exists(".tmp"):
    print("Removing temp directory")
    os.rmdir(".tmp")

print("Sync completed")
