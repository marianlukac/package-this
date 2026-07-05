from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import get_session
from app.models.employee import Employee
from app.persona.permissions import has_permission

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class PersonaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        persona_id = request.headers.get("X-Persona-Id")

        if request.method in WRITE_METHODS and not persona_id:
            # Allow through — route-level dependencies handle enforcement
            # Middleware only resolves the employee if header is present
            pass

        request.state.current_user = None
        request.state.persona_id = persona_id

        return await call_next(request)


def get_current_user(request: Request, session: Session = Depends(get_session)) -> Employee | None:
    persona_id = request.headers.get("X-Persona-Id")
    if not persona_id:
        return None
    employee = session.exec(select(Employee).where(Employee.employee_id == persona_id)).first()
    return employee


def require_persona(request: Request, session: Session = Depends(get_session)) -> Employee:
    persona_id = request.headers.get("X-Persona-Id")
    if not persona_id:
        raise HTTPException(
            status_code=401,
            detail="X-Persona-Id header is required for write operations.",
        )
    employee = session.exec(select(Employee).where(Employee.employee_id == persona_id)).first()
    if not employee:
        raise HTTPException(
            status_code=401,
            detail=f"No employee found with id '{persona_id}'. Check /employees for valid slugs.",
        )
    return employee


def require_permission(operation: str) -> Callable:
    def dependency(
        request: Request, session: Session = Depends(get_session)
    ) -> Employee:
        employee = require_persona(request, session)
        if not has_permission(employee.persona, operation):
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Persona '{employee.persona}' ({employee.name}) does not have "
                    f"permission for '{operation}'."
                ),
            )
        return employee

    return dependency


def require_manager() -> Callable:
    return require_permission("approve_reroute")
