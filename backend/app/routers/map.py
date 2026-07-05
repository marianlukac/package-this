from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.map_location import MapLocation

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/locations", response_model=list)
def get_map_locations(session: Session = Depends(get_session)):
    locations = session.exec(select(MapLocation).order_by(MapLocation.id)).all()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "location_type": loc.location_type,
            "lat": loc.lat,
            "lng": loc.lng,
            "description": loc.description,
        }
        for loc in locations
    ]


@router.get("/markers", response_model=list)
def get_map_markers(session: Session = Depends(get_session)):
    """Stable alias for GET /map/locations — same response shape, semantically named for agents."""
    return get_map_locations(session)
