from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    persona: str
    title: str
    email: str
    is_active: bool
