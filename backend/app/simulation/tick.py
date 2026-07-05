"""process_truck_tick — advance a single truck one waypoint along its route geometry."""
import json
from datetime import datetime

from sqlmodel import Session, select

from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.package import Package, PackageStatus
from app.models.truck import Truck, TruckStatus
from app.models.truck_route import RouteStatus, RouteStop, TruckRoute
from app.services.route_service import WAREHOUSE_LAT, WAREHOUSE_LNG
from app.services.truck_service import TruckService

ARRIVAL_THRESHOLD = 0.0003  # ~30m in degrees


async def process_truck_tick(
    session: Session,
    truck: Truck,
    tick_number: int,
    location_event_every_n_ticks: int,
) -> None:
    """Advance a truck one waypoint and handle arrival events."""
    if truck.status not in (TruckStatus.ON_ROUTE, TruckStatus.REROUTED, TruckStatus.RETURNING):
        return
    if not truck.current_route_id:
        return

    route = session.exec(
        select(TruckRoute).where(TruckRoute.route_id == truck.current_route_id)
    ).first()
    if not route:
        return

    geometry: list[list[float]] = json.loads(route.geometry)
    if not geometry:
        return

    waypoint_idx = route.current_waypoint_index
    if waypoint_idx >= len(geometry):
        await _complete_route(session, truck, route)
        return

    waypoint = geometry[waypoint_idx]
    new_lat, new_lng = float(waypoint[0]), float(waypoint[1])

    truck.current_lat = new_lat
    truck.current_lng = new_lng
    truck.last_location_update = datetime.utcnow()
    truck.updated_at = datetime.utcnow()
    route.current_waypoint_index = waypoint_idx + 1

    publisher = get_publisher()

    await _check_stop_arrival(session, truck, route, new_lat, new_lng, publisher)

    packages = session.exec(
        select(Package)
        .where(Package.truck_id == truck.truck_id)
        .where(Package.status == PackageStatus.IN_TRANSIT)
    ).all()
    for pkg in packages:
        pkg.current_lat = new_lat
        pkg.current_lng = new_lng
        pkg.current_location = f"{new_lat:.4f},{new_lng:.4f}"
        pkg.updated_at = datetime.utcnow()

    if tick_number % location_event_every_n_ticks == 0:
        await publisher.publish(make_envelope(
            event_type="truck.location.updated", topic="truck-location",
            actor_id=truck.truck_id, actor_name=truck.name, actor_type="system",
            source="simulation", entity_type="truck", entity_id=truck.truck_id,
            payload={
                "truck_id": truck.truck_id,
                "lat": new_lat, "lng": new_lng,
                "waypoint_index": waypoint_idx,
                "status": truck.status,
            },
            summary=f"{truck.name} at ({new_lat:.4f}, {new_lng:.4f})",
        ))

    session.commit()


async def _check_stop_arrival(
    session: Session, truck: Truck, route: TruckRoute, lat: float, lng: float, publisher
) -> None:
    """Check if the truck has arrived at a customer stop and record delivery."""
    pending_stops = session.exec(
        select(RouteStop)
        .where(RouteStop.route_id == route.route_id)
        .where(RouteStop.is_completed == False)  # noqa: E712
        .order_by(RouteStop.stop_order)
    ).all()

    for stop in pending_stops:
        from app.models.customer import Customer
        customer = session.exec(
            select(Customer).where(Customer.customer_id == stop.customer_id)
        ).first()
        if not customer or customer.lat is None:
            continue

        dist = abs(lat - customer.lat) + abs(lng - customer.lng)
        if dist <= ARRIVAL_THRESHOLD:
            delivered = await TruckService.record_delivery(
                session, truck.truck_id, stop.customer_id,
                actor_id=truck.truck_id,
                actor_name=truck.name,
                source="simulation",
            )
            await publisher.publish(make_envelope(
                event_type="truck.arrived_at_stop", topic="truck-location",
                actor_id=truck.truck_id, actor_name=truck.name, actor_type="system",
                source="simulation", entity_type="truck", entity_id=truck.truck_id,
                payload={
                    "truck_id": truck.truck_id, "customer_id": stop.customer_id,
                    "customer_name": customer.name, "stop_order": stop.stop_order,
                    "delivered_packages": delivered,
                },
                summary=f"{truck.name} arrived at {customer.name}",
            ))

            remaining = session.exec(
                select(RouteStop)
                .where(RouteStop.route_id == route.route_id)
                .where(RouteStop.is_completed == False)  # noqa: E712
            ).all()
            if not remaining:
                truck.status = TruckStatus.RETURNING
            break


async def _complete_route(session: Session, truck: Truck, route: TruckRoute) -> None:
    """Handle truck arrival back at warehouse after all stops complete."""
    dist = abs((truck.current_lat or 0) - WAREHOUSE_LAT) + abs((truck.current_lng or 0) - WAREHOUSE_LNG)

    if truck.status == TruckStatus.RETURNING or dist <= 0.001:
        truck.status = TruckStatus.AT_WAREHOUSE
        truck.current_lat = WAREHOUSE_LAT
        truck.current_lng = WAREHOUSE_LNG
        truck.current_route_id = None
        truck.is_delayed = False
        truck.delay_reason = None
        truck.delay_started_at = None
        truck.updated_at = datetime.utcnow()

        route.status = RouteStatus.COMPLETED
        route.completed_at = datetime.utcnow()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="truck.returned.to.warehouse", topic="truck-location",
            actor_id=truck.truck_id, actor_name=truck.name, actor_type="system",
            source="simulation", entity_type="truck", entity_id=truck.truck_id,
            payload={"truck_id": truck.truck_id, "route_id": route.route_id},
            summary=f"{truck.name} returned to warehouse",
        ))

        session.commit()
