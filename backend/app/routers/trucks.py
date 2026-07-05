from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.persona.middleware import require_permission
from app.services.truck_service import TruckService

router = APIRouter(prefix="/trucks", tags=["Trucks"])


class AssignPackageBody(BaseModel):
    package_id: str


class RerouteBody(BaseModel):
    location_id: int
    reason: str


@router.get("", response_model=list)
def list_trucks(session: Session = Depends(get_session)):
    return TruckService.get_all(session)


@router.get("/{truck_id}", response_model=dict)
def get_truck(truck_id: str, session: Session = Depends(get_session)):
    return TruckService.get_by_id(session, truck_id)


@router.get("/{truck_id}/current-location", response_model=dict)
def get_current_location(truck_id: str, session: Session = Depends(get_session)):
    return TruckService.get_current_location(session, truck_id)


@router.get("/{truck_id}/current-route", response_model=dict)
def get_current_route(truck_id: str, session: Session = Depends(get_session)):
    return TruckService.get_current_route(session, truck_id)


@router.post("/{truck_id}/assign", response_model=dict)
async def assign_package(
    truck_id: str,
    body: AssignPackageBody,
    session: Session = Depends(get_session),
    actor=Depends(require_permission("assign_to_truck")),
):
    return await TruckService.assign_package(session, truck_id, body.package_id, actor)


@router.post("/{truck_id}/dispatch", response_model=dict)
async def dispatch_truck(
    truck_id: str,
    session: Session = Depends(get_session),
    actor=Depends(require_permission("dispatch_truck")),
):
    return await TruckService.dispatch_truck(session, truck_id, actor)


@router.post("/{truck_id}/reroute", response_model=dict)
async def kevin_reroute(
    truck_id: str,
    body: RerouteBody,
    session: Session = Depends(get_session),
    actor=Depends(require_permission("approve_reroute")),
):
    return await TruckService.kevin_reroute(session, truck_id, body.location_id, body.reason, actor)
