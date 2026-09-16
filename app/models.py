from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator


class Employee(BaseModel):
    employee_id: str = Field(min_length=1)
    name: str = Field(min_length=2)
    email: EmailStr
    department: str = Field(min_length=1)
    salary: float = Field(gt=0)
    joining_date: date
    is_active: bool = True

    @field_validator("employee_id", "department")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if value.strip() == "":
            raise ValueError("must not be empty")
        return value.strip()


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = None
    department: str | None = Field(default=None, min_length=1)
    salary: float | None = Field(default=None, gt=0)
    joining_date: date | None = None
    is_active: bool | None = None


class LoginData(BaseModel):
    username: str
    password: str
