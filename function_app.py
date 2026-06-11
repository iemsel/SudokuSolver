import azure.functions as func
import json
import os
import datetime
# from azure.storage.blob import BlobServiceClient

# Initialize the Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
connection_string = os.environ.get("AzureWebJobsStorage")
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# 2. Access the 'start' container specifically
container_name = "start" 
blob_name = "one.json" # Your uploaded file
# blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# # 3. Download the board
# # blob_data = blob_client.download_blob().readall()
# board = json.loads(blob_data).get('board')

# ---------------------------------------------------------
# 1. Sudoku Backtracking Algorithm (RQ2)
# ---------------------------------------------------------
def is_valid(board, row, col, num):
    """Checks if placing a number in a specific cell violates Sudoku rules."""
    # Check row
    for i in range(9):
        if board[row][i] == num:
            return False
            
    # Check column
    for i in range(9):
        if board[i][col] == num:
            return False
            
    # Check 3x3 sub-grid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    """Recursive backtracking algorithm to solve the 9x9 grid."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # Find an empty cell
                for num in range(1, 10):  # Try numbers 1-9
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        
                        if solve_sudoku(board):
                            return True
                            
                        # Backtrack if the guess leads to an unsolvable state
                        board[row][col] = 0 
                return False
    return True

# ---------------------------------------------------------
# 2. Azure Function HTTP Trigger & Storage Logic (RQ4)
# ---------------------------------------------------------
@app.route(route="solve", methods=["POST"])
def solve_sudoku_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse the incoming HTTP request
        req_body = req.get_json()
        board = req_body.get('board')

        # Validate the grid structure (must be 9x9)
        if not board or len(board) != 9 or not all(len(row) == 9 for row in board):
            return func.HttpResponse(
                json.dumps({"error": "Invalid board. Please provide a 9x9 2D array."}), 
                status_code=400,
                mimetype="application/json"
            )

        # Execute the solving logic
        solved = solve_sudoku(board)

        if not solved:
            return func.HttpResponse(
                json.dumps({"error": "This Sudoku puzzle cannot be solved."}), 
                status_code=400,
                mimetype="application/json"
            )

        # Connect to Azure Blob Storage using the connection string
        connection_string = os.environ.get("AzureWebJobsStorage")
        # blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "sudoku-solutions"
        
        # Ensure the container exists
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        # Generate a unique filename based on the current timestamp
        file_name = f"solution-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        
        # Prepare the JSON data payload
        result_data = {
            "status": "solved",
            "solution": board,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Upload the JSON file to Blob Storage
        blob_client.upload_blob(json.dumps(result_data), overwrite=True)

        # Return the successful response back to the client
        return func.HttpResponse(
            json.dumps({
                "message": "Sudoku solved and saved to Azure Blob Storage!", 
                "solution": board, 
                "blob_file": file_name
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        # Catch and log errors, similar to the tracking done by Application Insights
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            status_code=500,
            mimetype="application/json"
        )