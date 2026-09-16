import logging

from fastapi import Depends, FastAPI, Query, status

from app.auth import login_user, require_login
from app.csv_store import employee_to_row, load_employees, save_employees
from app.exceptions import (
    DuplicateEmployeeException,
    EmployeeNotFoundException,
    register_exception_handlers,
)
from app.models import Employee, EmployeeUpdate, LoginData

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
register_exception_handlers(app)

employees = load_employees()


@app.get("/")
def home():
    return {"message": "Employee API is running"}


@app.post("/login")
def login(data: LoginData):
    return login_user(data)


@app.get("/employees")
def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    department: str | None = None,
    is_active: bool | None = None,
):
    filtered = employees

    if department is not None:
        filtered = [
            emp for emp in filtered if emp["department"].lower() == department.lower()
        ]

    if is_active is not None:
        wanted = "true" if is_active else "false"
        filtered = [emp for emp in filtered if emp["is_active"].lower() == wanted]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    page_items = filtered[start:end]

    logger.info(f"Fetched employees page={page} limit={limit} total={total}")
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "employees": page_items,
    }


@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    for employee in employees:
        if employee["employee_id"] == employee_id:
            logger.info(f"Employee {employee_id} fetched successfully")
            return employee
    raise EmployeeNotFoundException(employee_id)


@app.post("/employees", status_code=status.HTTP_201_CREATED)
def create_employee(employee: Employee, _: str = Depends(require_login)):
    for existing in employees:
        if existing["employee_id"] == employee.employee_id:
            raise DuplicateEmployeeException(
                f"Employee {employee.employee_id} already exists"
            )
        if existing["email"].lower() == str(employee.email).lower():
            raise DuplicateEmployeeException(f"Email {employee.email} already exists")

    row = employee_to_row(employee)
    new_list = employees + [row]
    save_employees(new_list)
    employees.clear()
    employees.extend(new_list)

    logger.info(f"Employee {employee.employee_id} created successfully")
    return {
        "message": "Your data has been stored",
        "employee": employee,
    }


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    _: str = Depends(require_login),
):
    index = None
    for i, employee in enumerate(employees):
        if employee["employee_id"] == employee_id:
            index = i
            break

    if index is None:
        raise EmployeeNotFoundException(employee_id)

    updated = employees[index].copy()
    changes = data.model_dump(exclude_unset=True)

    if "email" in changes:
        new_email = str(changes["email"]).lower()
        for other in employees:
            if (
                other["employee_id"] != employee_id
                and other["email"].lower() == new_email
            ):
                raise DuplicateEmployeeException(
                    f"Email {changes['email']} already exists"
                )
        updated["email"] = str(changes["email"])

    if "name" in changes:
        updated["name"] = changes["name"]
    if "department" in changes:
        updated["department"] = changes["department"]
    if "salary" in changes:
        updated["salary"] = str(changes["salary"])
    if "joining_date" in changes:
        updated["joining_date"] = changes["joining_date"].isoformat()
    if "is_active" in changes:
        updated["is_active"] = str(changes["is_active"]).lower()

    new_list = employees.copy()
    new_list[index] = updated
    save_employees(new_list)
    employees.clear()
    employees.extend(new_list)

    logger.info(f"Employee {employee_id} updated")
    return updated


@app.delete("/employees/{employee_id}")
def deactivate_employee(employee_id: str, _: str = Depends(require_login)):
    index = None
    for i, employee in enumerate(employees):
        if employee["employee_id"] == employee_id:
            index = i
            break

    if index is None:
        raise EmployeeNotFoundException(employee_id)

    new_list = employees.copy()
    new_list[index] = employees[index].copy()
    new_list[index]["is_active"] = "false"
    save_employees(new_list)
    employees.clear()
    employees.extend(new_list)

    logger.info(f"Employee {employee_id} deactivated")
    return {"message": f"Employee {employee_id} deactivated successfully"}
