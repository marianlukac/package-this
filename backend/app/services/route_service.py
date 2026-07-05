"""RouteService — linear-interpolation route calculation, stop management, via-point insertion."""
import json
import math
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.customer import Customer
from app.models.truck_route import RouteStatus, RouteStop, TruckRoute, ViaPoint

# Warehouse coordinates — Dunder Mifflin HQ
WAREHOUSE_LAT = 41.4090
WAREHOUSE_LNG = -75.6624

# Approximate waypoints per km of straight-line distance (~30s of demo-time movement each)
WAYPOINTS_PER_KM = 4
# Estimated minutes per stop in demo time (drives + service time)
MINUTES_PER_STOP = 6


def _segment_waypoints(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> list[list[float]]:
    """Build waypoints for a route segment, including the destination point."""
    dlat = (lat2 - lat1) * 111.0
    dlng = (lng2 - lng1) * 85.0
    dist_km = math.sqrt(dlat ** 2 + dlng ** 2)
    n_steps = max(1, int(dist_km * WAYPOINTS_PER_KM))
    points = []
    for i in range(1, n_steps + 1):
        t = i / (n_steps + 1)
        points.append([round(lat1 + (lat2 - lat1) * t, 6), round(lng1 + (lng2 - lng1) * t, 6)])
    points.append([round(lat2, 6), round(lng2, 6)])
    return points


def calculate_route(
    session: Session, truck_id: str, customer_ids: list[str]
) -> TruckRoute:
    """Build a TruckRoute with ordered RouteStops and interpolated geometry."""
    if not customer_ids:
        raise HTTPException(status_code=400, detail="Route must have at least one customer stop.")
    if len(customer_ids) > 12:
        raise HTTPException(status_code=400, detail="Route may not exceed 12 customer stops.")

    ordered_customers: list[Customer] = []
    for cid in customer_ids:
        c = session.exec(select(Customer).where(Customer.customer_id == cid)).first()
        if not c:
            raise HTTPException(status_code=404, detail=f"Customer '{cid}' not found.")
        if c.lat is None or c.lng is None:
            raise HTTPException(status_code=400, detail=f"Customer '{cid}' has no GPS coordinates.")
        ordered_customers.append(c)

    route_id = f"ROUTE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    route = TruckRoute(
        route_id=route_id,
        truck_id=truck_id,
        status=RouteStatus.PLANNED,
        estimated_duration_minutes=len(customer_ids) * MINUTES_PER_STOP,
    )

    # Build geometry: warehouse -> stop1 -> stop2 -> ... -> warehouse
    all_waypoints: list[list[float]] = [[round(WAREHOUSE_LAT, 6), round(WAREHOUSE_LNG, 6)]]
    prev_lat, prev_lng = WAREHOUSE_LAT, WAREHOUSE_LNG
    for c in ordered_customers:
        segment = _segment_waypoints(prev_lat, prev_lng, c.lat, c.lng)
        all_waypoints.extend(segment)
        prev_lat, prev_lng = c.lat, c.lng

    # Return leg to warehouse
    return_segment = _segment_waypoints(prev_lat, prev_lng, WAREHOUSE_LAT, WAREHOUSE_LNG)
    all_waypoints.extend(return_segment)

    route.geometry = json.dumps(all_waypoints)
    session.add(route)
    session.flush()

    # Build route stops
    for stop_order, c in enumerate(ordered_customers, start=1):
        stop = RouteStop(
            stop_id=f"{route_id}-STOP-{stop_order:02d}",
            route_id=route_id,
            customer_id=c.customer_id,
            stop_order=stop_order,
            estimated_arrival=datetime.utcnow() + timedelta(minutes=stop_order * MINUTES_PER_STOP),
        )
        session.add(stop)

    session.flush()
    return route


def insert_via_point(
    session: Session,
    route_id: str,
    lat: float,
    lng: float,
    name: str,
    reason: str,
    insert_before_stop_order: int,
) -> ViaPoint:
    """Splice a via-point into the route geometry before the given stop order."""
    route = session.exec(select(TruckRoute).where(TruckRoute.route_id == route_id)).first()
    if not route:
        raise HTTPException(status_code=404, detail=f"Route '{route_id}' not found.")

    via = ViaPoint(
        route_id=route_id,
        name=name,
        lat=lat,
        lng=lng,
        reason=reason,
        inserted_before_stop_order=insert_before_stop_order,
    )
    session.add(via)

    # Find the target stop's customer coordinates to locate insertion point in geometry
    geometry: list[list[float]] = json.loads(route.geometry)
    target_stop = session.exec(
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .where(RouteStop.stop_order == insert_before_stop_order)
    ).first()

    if target_stop:
        customer = session.exec(
            select(Customer).where(Customer.customer_id == target_stop.customer_id)
        ).first()
        if customer and customer.lat is not None:
            # Find waypoint closest to stop's customer and insert via-point before it
            best_idx = len(geometry) // 2
            best_dist = float("inf")
            for i, wp in enumerate(geometry):
                dist = abs(wp[0] - customer.lat) + abs(wp[1] - customer.lng)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
            geometry.insert(best_idx, [round(lat, 6), round(lng, 6)])
            route.geometry = json.dumps(geometry)

    session.flush()
    return via


def get_route_detail(session: Session, route_id: str) -> dict:
    """Return full route with geometry, stops, and via-points."""
    route = session.exec(select(TruckRoute).where(TruckRoute.route_id == route_id)).first()
    if not route:
        raise HTTPException(status_code=404, detail=f"Route '{route_id}' not found.")

    stops = session.exec(
        select(RouteStop)
        .where(RouteStop.route_id == route_id)
        .order_by(RouteStop.stop_order)
    ).all()

    via_points = session.exec(
        select(ViaPoint)
        .where(ViaPoint.route_id == route_id)
        .order_by(ViaPoint.inserted_at)
    ).all()

    customer_names: dict[str, str] = {}
    for stop in stops:
        if stop.customer_id not in customer_names:
            c = session.exec(select(Customer).where(Customer.customer_id == stop.customer_id)).first()
            customer_names[stop.customer_id] = c.name if c else stop.customer_id

    return {
        "route_id": route.route_id,
        "truck_id": route.truck_id,
        "status": route.status,
        "geometry": json.loads(route.geometry),
        "estimated_duration_minutes": route.estimated_duration_minutes,
        "current_waypoint_index": route.current_waypoint_index,
        "started_at": route.started_at,
        "completed_at": route.completed_at,
        "stops": [
            {
                "stop_id": s.stop_id,
                "stop_order": s.stop_order,
                "customer_id": s.customer_id,
                "customer_name": customer_names.get(s.customer_id, s.customer_id),
                "estimated_arrival": s.estimated_arrival,
                "arrived_at": s.arrived_at,
                "is_completed": s.is_completed,
            }
            for s in stops
        ],
        "via_points": [
            {
                "id": v.id,
                "name": v.name,
                "lat": v.lat,
                "lng": v.lng,
                "reason": v.reason,
                "inserted_before_stop_order": v.inserted_before_stop_order,
                "inserted_at": v.inserted_at,
            }
            for v in via_points
        ],
    }
