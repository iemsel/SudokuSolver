from azure.storage.blob import BlobServiceClient
import os
import json
import uuid

connection_string = os.environ["BLOB_CONNECTION_STRING"]

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)

container_name = "sudoku"

def save_solution(puzzle, solution, execution_time):

    data = {
        "puzzle": puzzle,
        "solution": solution,
        "executionTime": execution_time
    }

    blob_name = f"solution-{uuid.uuid4()}.json"

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    blob_client.upload_blob(
        json.dumps(data),
        overwrite=True
    )