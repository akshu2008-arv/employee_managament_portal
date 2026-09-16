import logging
from pathlib import Path

import pandas as pd
import numpy as np
from app.exceptions import CSVFileException
from app.models import Employee

logger = logging.getLogger(__name__)

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "employees.csv"
CSV_FIELDS = [
    "employee_id",
    "name",
    "email",
    "department",
    "salary",
    "joining_date",
    "is_active",
]


def load_employees() -> list[dict]:
    try:
        # READ: CSV file → DataFrame (table)
        df = pd.read_csv(CSV_PATH, dtype=str)
        # keep columns in the correct order
        df = df.reindex(columns=CSV_FIELDS)
        # DataFrame → list of dicts (what main.py expects)
        rows = df.fillna("").to_dict(orient="records")
        logger.info(f"Loaded {len(rows)} employees from CSV")
        return rows
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError):
        logger.error("Unable to read employee data from CSV")
        raise CSVFileException()


def save_employees(rows: list[dict]) -> None:
    try:
        # list of dicts → DataFrame
        df = pd.DataFrame(rows, columns=CSV_FIELDS)
        # WRITE: DataFrame → CSV file
        df.to_csv(CSV_PATH, index=False)
        logger.info(f"Saved {len(rows)} employees to CSV")
    except OSError:
        logger.error("Unable to write employee data to CSV")
        raise CSVFileException()


def employee_to_row(employee: Employee) -> dict:
    return {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "email": str(employee.email),
        "department": employee.department,
        "salary": str(employee.salary),
        "joining_date": employee.joining_date.isoformat(),
        "is_active": str(employee.is_active).lower(),
    }
