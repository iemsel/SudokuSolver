import azure.functions as func
import json
import os
import datetime
import traceback
from azure.storage.blob import BlobServiceClient

import sudoku_solver

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="solve", methods=["POST"])
def solve_sudoku_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        board = req_body.get('board')

        if not board or len(board) != 9 or not all(len(row) == 9 for row in board):
            return func.HttpResponse(
                json.dumps({"error": "Invalid board. Must be 9x9 array."}), 
                status_code=400,
                mimetype="application/json"
            )

        board_copy = [row[:] for row in board]

        if sudoku_solver.solve(board_copy):
            # Try to save to blob (but don't fail the whole request if it doesn't work)
            try:
                connection_string = os.environ.get("AzureWebJobsStorage") or "UseDevelopmentStorage=true"
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                container_client = blob_service_client.get_container_client("sudoku-solutions")
                if not container_client.exists():
                    container_client.create_container()

                file_name = f"solution-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                blob_client = blob_service_client.get_blob_client(container="sudoku-solutions", blob=file_name)

                result_data = {
                    "status": "solved",
                    "solution": board_copy,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "original": board
                }
                blob_client.upload_blob(json.dumps(result_data, indent=2), overwrite=True)
                saved_message = f"Saved as {file_name}"
            except Exception as blob_err:
                saved_message = f"Blob save failed: {str(blob_err)}"

            return func.HttpResponse(
                json.dumps({
                    "message": "Sudoku solved successfully!",
                    "solution": board_copy,
                    "info": saved_message
                }),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "No solution found for this puzzle."}), 
                status_code=400,
                mimetype="application/json"
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "traceback": traceback.format_exc()
            }), 
            status_code=500,
            mimetype="application/json"
        )