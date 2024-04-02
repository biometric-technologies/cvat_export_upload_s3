import pandas as pd
from io import StringIO, BytesIO
import os


def get_tasks_csv(client, bucket, object_name):
    try:
        response = client.get_object(bucket, object_name)
        return pd.read_csv(response)
    except:
        # If file does not exist, create a new DataFrame
        return pd.DataFrame(columns=['Project Id', 'Task Id', 'Project Name', 'Task Name', 'Status', 'Path'])


def upload_tasks_csv(client, bucket, object_name, tasks_csv):
    try:
        csv_buffer = StringIO()
        tasks_csv.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        client.put_object(bucket, object_name, data=BytesIO(csv_bytes), length=len(csv_bytes),
                          content_type='application/csv')
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Error: {e}")


def upload_file(minio_client, bucket_name, object_name, file_path):
    try:
        with open(file_path, 'rb') as file_data:
            file_stat = os.stat(file_path)
            minio_client.put_object(
                bucket_name, object_name, file_data, file_stat.st_size
            )
        return True
    except Exception as e:
        print("Error occurred:", e)
        return False
