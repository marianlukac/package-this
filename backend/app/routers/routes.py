from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.package import Package, PackageStatus
from app.models.truck import Truck
from app.services.route_service import get_route_detail, list_routes

router = APIRouter(tags=["Routes"])


@router.get("/routes", response_model=list)
def get_routes(status: Optional[str] = None, session: Session = Depends(get_session)):
    return list_routes(session, status=status)


@router.get("/routes/{route_id}", response_model=dict)
def get_route(route_id: str, session: Session = Depends(get_session)):
    return get_route_detail(session, route_id)


@router.get("/deliveries/active", response_model=list)
def get_active_deliveries(session: Session = Depends(get_session)):
    packages = session.exec(
        select(Package).where(Package.status.in_([
            PackageStatus.SHIPPED, PackageStatus.IN_TRANSIT,
        ]))
    ).all()
    trucks = {t.truck_id: t for t in session.exec(select(Truck)).all()}
    return [
        {
            "package_id": p.package_id, "customer_id": p.customer_id,
            "status": p.status, "truck_id": p.truck_id,
            "destination": p.destination, "expected_delivery": p.expected_delivery,
            "truck_lat": trucks[p.truck_id].current_lat if p.truck_id and p.truck_id in trucks else None,
            "truck_lng": trucks[p.truck_id].current_lng if p.truck_id and p.truck_id in trucks else None,
        }
        for p in packages
    ]
