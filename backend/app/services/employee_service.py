from sqlmodel import Session, select

from app.models.employee import Employee
from app.schemas.employee import EmployeeResponse


def _to_response(e: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=e.id, employee_id=e.employee_id, name=e.name,
        persona=e.persona, title=e.title, email=e.email, is_active=e.is_active,
    )


class EmployeeService:
    @staticmethod
    def get_all(session: Session) -> list[EmployeeResponse]:
        employees = session.exec(select(Employee).where(Employee.is_active == True).order_by(Employee.name)).all()
        return [_to_response(e) for e in employees]

    @staticmethod
    def get_by_id(session: Session, employee_id: str) -> Employee | None:
        return session.exec(select(Employee).where(Employee.employee_id == employee_id)).first()
