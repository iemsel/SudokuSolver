import azure.functions as func
import logging

app = func.FunctionApp()

@app.route(route="solveSudoku")
def solveSudoku(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("Sudoku request received")

    return func.HttpResponse(
        "Sudoku solver executed successfully",
        status_code=200
    )