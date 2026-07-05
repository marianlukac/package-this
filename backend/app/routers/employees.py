from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.employee import EmployeeResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeResponse])
def list_employees(session: Session = Depends(get_session)):
    return EmployeeService.get_all(session)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, session: Session = Depends(get_session)):
    emp = EmployeeService.get_by_id(session, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")
    from app.schemas.employee import EmployeeResponse
    return EmployeeResponse(
        id=emp.id, employee_id=emp.employee_id, name=emp.name,
        persona=emp.persona, title=emp.title, email=emp.email, is_active=emp.is_active,
    )
