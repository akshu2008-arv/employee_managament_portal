import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class EmployeeNotFoundException(Exception):
    def __init__(self, employee_id: str):
        self.employee_id = employee_id


class DuplicateEmployeeException(Exception):
    def __init__(self, message: str):
        self.message = message


class CSVFileException(Exception):
    pass


def build_validation_message(error: dict) -> str:
    location = error.get("loc", ())
    field = location[-1] if location else "input"
    error_type = error.get("type", "")

    if error_type in {"int_parsing", "float_parsing", "bool_parsing", "date_parsing"}:
        return f"Wrong data type for '{field}'. Please send the correct type."

    if error_type == "missing":
        return f"Missing required field: '{field}'."

    return error.get("msg", "Invalid input")


def register_exception_handlers(app) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            logger.warning(f"HTTP error: {exc.detail.get('message', exc.detail)}")
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "ERROR", "message": str(exc.detail)},
        )

    @app.exception_handler(EmployeeNotFoundException)
    async def employee_not_found_handler(
        request: Request, exc: EmployeeNotFoundException
    ):
        logger.warning(f"Employee {exc.employee_id} was not found")
        return JSONResponse(
            status_code=404,
            content={
                "error": "EMPLOYEE_NOT_FOUND",
                "message": f"Employee {exc.employee_id} does not exist",
            },
        )

    @app.exception_handler(DuplicateEmployeeException)
    async def duplicate_employee_handler(
        request: Request, exc: DuplicateEmployeeException
    ):
        logger.warning(exc.message)
        return JSONResponse(
            status_code=409,
            content={
                "error": "DUPLICATE_EMPLOYEE",
                "message": exc.message,
            },
        )

    @app.exception_handler(CSVFileException)
    async def csv_error_handler(request: Request, exc: CSVFileException):
        logger.error("Unable to access employee CSV data")
        return JSONResponse(
            status_code=500,
            content={
                "error": "DATA_SOURCE_ERROR",
                "message": "Employee data could not be accessed",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        first = exc.errors()[0]
        message = build_validation_message(first)
        logger.warning(f"Validation error: {message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "VALIDATION_ERROR",
                "message": message,
            },
        )

    @app.exception_handler(Exception)
    async def global_error_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong. Please try again later.",
            },
        )
