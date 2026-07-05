from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.lifecycle.transitions import InvalidTransitionError, MissingLineItemsError
from app.persona.middleware import get_current_user, require_permission
from app.schemas.package import PackageCreate, PackageResponse, PackageUpdate
from app.schemas.package_history import PackageHistoryListResponse
from app.schemas.package_line_item import LineItemCreate, LineItemResponse, LineItemUpdate
from app.schemas.status_change import DelayRequest, StatusChangeRequest
from app.services.package_service import PackageService

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.get("", response_model=dict[str, Any])
def list_packages(
    status: str | None = None,
    priority: str | None = None,
    customer_id: str | None = None,
    salesperson_id: str | None = None,
    invoice_creator_id: str | None = None,
    truck_id: str | None = None,
    has_delay: bool | None = None,
    exception_state: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    items, total = PackageService.get_all(
        session, status=status, priority=priority, customer_id=customer_id,
        salesperson_id=salesperson_id, invoice_creator_id=invoice_creator_id,
        truck_id=truck_id, has_delay=has_delay, exception_state=exception_state,
        search=search, sort_by=sort_by, limit=limit, offset=offset,
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/at-risk", response_model=list)
def get_at_risk_packages(session: Session = Depends(get_session)):
    return PackageService.get_at_risk(session)


@router.get("/delayed", response_model=list)
def get_delayed_packages(session: Session = Depends(get_session)):
    return PackageService.get_delayed(session)


@router.get("/{package_id}", response_model=PackageResponse)
def get_package(package_id: str, session: Session = Depends(get_session)):
    pkg = PackageService.get_by_id(session, package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
    from app.services.package_service import _to_response
    return _to_response(session, pkg)


@router.post("", response_model=PackageResponse, status_code=201)
async def create_package(
    body: PackageCreate,
    actor=Depends(require_permission("create_package")),
    session: Session = Depends(get_session),
):
    return await PackageService.create_package(
        session, actor, body.sale_id, body.destination,
        body.priority, body.contents_summary, body.fragile,
    )


@router.patch("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: str,
    body: PackageUpdate,
    actor=Depends(require_permission("edit_package_fields")),
    session: Session = Depends(get_session),
):
    return await PackageService.update_fields(session, actor, package_id, body)


@router.delete("/{package_id}", status_code=204)
async def delete_package(
    package_id: str,
    actor=Depends(require_permission("delete_package")),
    session: Session = Depends(get_session),
):
    await PackageService.delete_package(session, actor, package_id)


@router.get("/{package_id}/history", response_model=PackageHistoryListResponse)
def get_package_history(package_id: str, session: Session = Depends(get_session)):
    pkg = PackageService.get_by_id(session, package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
    return PackageService.get_history(session, package_id)


@router.post("/{package_id}/status", response_model=PackageResponse)
async def advance_status(
    package_id: str,
    body: StatusChangeRequest,
    # No router-level permission guard — permission dispatch is inside advance_status() based on target_status (T092)
    actor=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return await PackageService.advance_status(
            session, actor, package_id, body.status, body.reason, "ui", body.correlation_id
        )
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except MissingLineItemsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/{package_id}/delay", response_model=PackageResponse)
async def record_delay(
    package_id: str,
    body: DelayRequest,
    actor=Depends(require_permission("record_delay")),
    session: Session = Depends(get_session),
):
    return await PackageService.record_delay(
        session, actor, package_id, body.delay_reason, body.delay_duration_hours
    )


@router.post("/{package_id}/line-items", response_model=LineItemResponse, status_code=201)
async def add_line_item(
    package_id: str,
    body: LineItemCreate,
    actor=Depends(require_permission("manage_line_items")),
    session: Session = Depends(get_session),
):
    return await PackageService.add_line_item(session, actor, package_id, body)


@router.patch("/{package_id}/line-items/{item_id}", response_model=LineItemResponse)
async def update_line_item(
    package_id: str,
    item_id: int,
    body: LineItemUpdate,
    actor=Depends(require_permission("manage_line_items")),
    session: Session = Depends(get_session),
):
    return await PackageService.update_line_item(session, actor, package_id, item_id, body)


@router.delete("/{package_id}/line-items/{item_id}", status_code=204)
async def remove_line_item(
    package_id: str,
    item_id: int,
    actor=Depends(require_permission("manage_line_items")),
    session: Session = Depends(get_session),
):
    await PackageService.remove_line_item(session, actor, package_id, item_id)
