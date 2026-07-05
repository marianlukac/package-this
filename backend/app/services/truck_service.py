"""TruckService — truck assignment, dispatch, delivery, and reroute operations."""
import json
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.map_location import LocationType, MapLocation
from app.models.package import Package, PackageStatus
from app.models.package_history import PackageHistory, PackageHistoryEventType
from app.models.truck import Truck, TruckStatus
from app.models.truck_route import RouteStatus, RouteStop
from app.services.route_service import calculate_route, get_route_detail, insert_via_point


class TruckService:
    @staticmethod
    def get_all(session: Session) -> list[dict]:
        trucks = session.exec(select(Truck).order_by(Truck.truck_number)).all()
        result = []
        for t in trucks:
            pkg_count = len(session.exec(
                select(Package).where(Package.truck_id == t.truck_id)
                .where(Package.status.in_([PackageStatus.READY_FOR_SHIPPING, PackageStatus.SHIPPED, PackageStatus.IN_TRANSIT]))
            ).all())
            result.append({
                "truck_id": t.truck_id,
                "truck_number": t.truck_number,
                "name": t.name,
                "status": t.status,
                "current_lat": t.current_lat,
                "current_lng": t.current_lng,
                "current_stop_index": t.current_stop_index,
                "delay_reason": t.delay_reason,
                "delay_duration_hours": t.delay_duration_hours,
                "current_route_id": t.current_route_id,
                "package_count": pkg_count,
            })
        return result

    @staticmethod
    def get_by_id(session: Session, truck_id: str) -> dict:
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")

        packages = session.exec(
            select(Package)
            .where(Package.truck_id == truck_id)
            .where(Package.status.in_([PackageStatus.READY_FOR_SHIPPING, PackageStatus.SHIPPED, PackageStatus.IN_TRANSIT]))
        ).all()

        assigned_pkgs = []
        for pkg in packages:
            customer = session.exec(select(Customer).where(Customer.customer_id == pkg.customer_id)).first()
            stop_order = 0
            if truck.current_route_id:
                stop = session.exec(
                    select(RouteStop)
                    .where(RouteStop.route_id == truck.current_route_id)
                    .where(RouteStop.customer_id == pkg.customer_id)
                ).first()
                if stop:
                    stop_order = stop.stop_order
            assigned_pkgs.append({
                "package_id": pkg.package_id,
                "customer_name": customer.name if customer else pkg.customer_id,
                "status": pkg.status,
                "stop_order": stop_order,
            })

        return {
            "truck_id": truck.truck_id,
            "truck_number": truck.truck_number,
            "name": truck.name,
            "status": truck.status,
            "current_lat": truck.current_lat,
            "current_lng": truck.current_lng,
            "delay_reason": truck.delay_reason,
            "delay_duration_hours": truck.delay_duration_hours,
            "delay_started_at": truck.delay_started_at,
            "current_route_id": truck.current_route_id,
            "current_stop_index": truck.current_stop_index,
            "assigned_packages": assigned_pkgs,
        }

    @staticmethod
    def get_current_location(session: Session, truck_id: str) -> dict:
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")
        return {
            "truck_id": truck.truck_id,
            "lat": truck.current_lat,
            "lng": truck.current_lng,
            "status": truck.status,
            "updated_at": truck.last_location_update,
        }

    @staticmethod
    def get_current_route(session: Session, truck_id: str) -> dict:
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")
        if not truck.current_route_id:
            return {
                "truck_id": truck_id,
                "route_id": None,
                "status": truck.status,
                "geometry": [],
                "stops": [],
                "via_points": [],
                "current_waypoint_index": 0,
                "estimated_duration_minutes": 0,
                "started_at": None,
                "completed_at": None,
            }
        return get_route_detail(session, truck.current_route_id)

    @staticmethod
    async def assign_package(
        session: Session, truck_id: str, package_id: str,
        actor: Employee, source: str = "api",
    ) -> dict:
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")

        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")

        if pkg.status != PackageStatus.READY_FOR_SHIPPING:
            raise HTTPException(
                status_code=409,
                detail=f"Package '{package_id}' must be ready_for_shipping to assign to a truck (current: {pkg.status}).",
            )
        if pkg.truck_id and pkg.truck_id != truck_id:
            raise HTTPException(
                status_code=409,
                detail=f"Package '{package_id}' is already assigned to truck '{pkg.truck_id}'.",
            )

        pkg.truck_id = truck_id
        pkg.updated_at = datetime.utcnow()

        session.add(PackageHistory(
            package_id=pkg.package_id,
            event_type=PackageHistoryEventType.ASSIGNED_TO_TRUCK,
            actor_id=actor.employee_id, actor_name=actor.name,
            timestamp=datetime.utcnow(), source=source,
            entity_type="package", entity_id=pkg.package_id,
            new_value=json.dumps({"truck_id": truck_id}),
        ))
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="package.assigned.to.truck", topic="package-status",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="package", entity_id=pkg.package_id,
            payload={"package_id": pkg.package_id, "truck_id": truck_id},
            summary=f"Package {pkg.package_id} assigned to {truck.name}",
        ))

        return {"truck_id": truck_id, "package_id": package_id, "assigned": True}

    @staticmethod
    async def dispatch_truck(
        session: Session, truck_id: str,
        actor: Employee, source: str = "api",
    ) -> dict:
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")

        if truck.status not in (TruckStatus.AT_WAREHOUSE, TruckStatus.LOADING, TruckStatus.READY):
            raise HTTPException(
                status_code=409,
                detail=f"Truck '{truck_id}' must be at warehouse, loading, or ready to dispatch (current: {truck.status}).",
            )

        packages = session.exec(
            select(Package)
            .where(Package.truck_id == truck_id)
            .where(Package.status == PackageStatus.READY_FOR_SHIPPING)
        ).all()

        if not packages:
            raise HTTPException(
                status_code=409,
                detail=f"Truck '{truck_id}' has no ready_for_shipping packages assigned.",
            )

        seen_customers: dict[str, Customer] = {}
        for pkg in packages:
            if pkg.customer_id not in seen_customers:
                c = session.exec(select(Customer).where(Customer.customer_id == pkg.customer_id)).first()
                if c:
                    seen_customers[pkg.customer_id] = c

        customer_ids = list(seen_customers.keys())
        route = calculate_route(session, truck_id, customer_ids)

        # Generate one correlation ID for this entire dispatch operation
        correlation_id = str(uuid.uuid4())

        for pkg in packages:
            pkg.status = PackageStatus.IN_TRANSIT
            pkg.updated_at = datetime.utcnow()
            session.add(PackageHistory(
                package_id=pkg.package_id,
                event_type=PackageHistoryEventType.STATUS_CHANGED,
                actor_id=actor.employee_id, actor_name=actor.name,
                timestamp=datetime.utcnow(), source=source,
                entity_type="package", entity_id=pkg.package_id,
                previous_value=json.dumps({"status": PackageStatus.READY_FOR_SHIPPING}),
                new_value=json.dumps({"status": PackageStatus.IN_TRANSIT}),
                correlation_id=correlation_id,
            ))

        truck.status = TruckStatus.ON_ROUTE
        truck.current_route_id = route.route_id
        truck.current_stop_index = 0
        truck.is_delayed = False
        truck.delay_reason = None
        truck.delay_duration_hours = None
        truck.delay_started_at = None
        truck.updated_at = datetime.utcnow()

        route.status = RouteStatus.ACTIVE
        route.started_at = datetime.utcnow()

        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="truck.route.created", topic="truck-location",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="truck", entity_id=truck_id,
            payload={"truck_id": truck_id, "route_id": route.route_id, "stop_count": len(customer_ids)},
            summary=f"{truck.name} dispatched with {len(packages)} packages across {len(customer_ids)} stops",
            correlation_id=correlation_id,
        ))

        # Emit package.status.updated for each package that was moved to in_transit
        for pkg in packages:
            await publisher.publish(make_envelope(
                event_type="package.status.updated", topic="package-status",
                actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
                source=source, entity_type="package", entity_id=pkg.package_id,
                payload={"package_id": pkg.package_id,
                         "previous_status": PackageStatus.READY_FOR_SHIPPING,
                         "new_status": PackageStatus.IN_TRANSIT},
                summary=f"Package {pkg.package_id} moved to in_transit by dispatch of {truck.name}",
                correlation_id=correlation_id,
            ))

        return {"truck_id": truck_id, "status": truck.status, "route_id": route.route_id}

    @staticmethod
    async def record_delivery(
        session: Session, truck_id: str, customer_id: str,
        actor_id: str, actor_name: str, source: str = "simulation",
    ) -> list[str]:
        """Mark all in-transit packages for a customer on this truck as delivered."""
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            return []

        customer = session.exec(select(Customer).where(Customer.customer_id == customer_id)).first()
        customer_lat = customer.lat if customer else None
        customer_lng = customer.lng if customer else None
        customer_name = customer.name if customer else customer_id

        packages = session.exec(
            select(Package)
            .where(Package.truck_id == truck_id)
            .where(Package.customer_id == customer_id)
            .where(Package.status == PackageStatus.IN_TRANSIT)
        ).all()

        delivered_ids: list[str] = []
        publisher = get_publisher()

        for pkg in packages:
            pkg.status = PackageStatus.DELIVERED
            pkg.current_location = customer_name
            pkg.current_lat = customer_lat
            pkg.current_lng = customer_lng
            pkg.truck_id = None
            pkg.updated_at = datetime.utcnow()

            session.add(PackageHistory(
                package_id=pkg.package_id,
                event_type=PackageHistoryEventType.DELIVERED,
                actor_id=actor_id, actor_name=actor_name,
                timestamp=datetime.utcnow(), source=source,
                entity_type="package", entity_id=pkg.package_id,
                new_value=json.dumps({"status": "delivered", "customer": customer_name}),
            ))

            await publisher.publish(make_envelope(
                event_type="package.delivered", topic="package-status",
                actor_id=actor_id, actor_name=actor_name, actor_type="system",
                source=source, entity_type="package", entity_id=pkg.package_id,
                payload={"package_id": pkg.package_id, "customer_id": customer_id,
                         "customer_name": customer_name, "truck_id": truck_id},
                summary=f"Package {pkg.package_id} delivered to {customer_name}",
            ))
            delivered_ids.append(pkg.package_id)

        if truck.current_route_id:
            stop = session.exec(
                select(RouteStop)
                .where(RouteStop.route_id == truck.current_route_id)
                .where(RouteStop.customer_id == customer_id)
            ).first()
            if stop:
                stop.is_completed = True
                stop.arrived_at = datetime.utcnow()
                stop.completed_at = datetime.utcnow()

        session.flush()
        return delivered_ids

    @staticmethod
    async def kevin_reroute(
        session: Session, truck_id: str, location_id: int, reason: str,
        actor: Employee, source: str = "api",
    ) -> dict:
        """Insert a food/donut via-point into the truck's active route."""
        truck = session.exec(select(Truck).where(Truck.truck_id == truck_id)).first()
        if not truck:
            raise HTTPException(status_code=404, detail=f"Truck '{truck_id}' not found.")

        if truck.status not in (TruckStatus.ON_ROUTE, TruckStatus.REROUTED):
            raise HTTPException(
                status_code=409,
                detail=f"Truck '{truck_id}' must be on_route or rerouted to trigger a reroute (current: {truck.status}).",
            )

        if not truck.current_route_id:
            raise HTTPException(status_code=409, detail=f"Truck '{truck_id}' has no active route.")

        location = session.exec(
            select(MapLocation).where(MapLocation.id == location_id)
        ).first()
        if not location or location.location_type not in (LocationType.FOOD, LocationType.DONUT):
            raise HTTPException(
                status_code=404,
                detail=f"Location {location_id} not found or is not a food/donut location.",
            )

        next_stop = session.exec(
            select(RouteStop)
            .where(RouteStop.route_id == truck.current_route_id)
            .where(RouteStop.is_completed == False)  # noqa: E712
            .order_by(RouteStop.stop_order)
        ).first()
        insert_before = next_stop.stop_order if next_stop else 1

        via = insert_via_point(
            session, truck.current_route_id,
            lat=location.lat, lng=location.lng,
            name=location.name, reason=reason,
            insert_before_stop_order=insert_before,
        )

        truck.status = TruckStatus.REROUTED
        truck.is_delayed = True
        truck.delay_reason = reason
        truck.delay_duration_hours = 0.5
        truck.delay_started_at = datetime.utcnow()
        truck.updated_at = datetime.utcnow()

        in_transit_packages = session.exec(
            select(Package)
            .where(Package.truck_id == truck_id)
            .where(Package.status == PackageStatus.IN_TRANSIT)
        ).all()

        affected_ids: list[str] = []
        for pkg in in_transit_packages:
            pkg.delay_reason = reason
            pkg.delay_duration_hours = 0.5
            pkg.updated_at = datetime.utcnow()
            session.add(PackageHistory(
                package_id=pkg.package_id,
                event_type=PackageHistoryEventType.DELAY_RECORDED,
                actor_id=actor.employee_id, actor_name=actor.name,
                timestamp=datetime.utcnow(), source=source,
                entity_type="package", entity_id=pkg.package_id,
                new_value=json.dumps({"delay_reason": reason, "via_point": location.name}),
                reason=reason,
            ))
            affected_ids.append(pkg.package_id)

        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="truck.rerouted", topic="truck-reroute",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="truck", entity_id=truck_id,
            payload={
                "truck_id": truck_id, "via_point": location.name,
                "lat": location.lat, "lng": location.lng,
                "reason": reason, "affected_packages": affected_ids,
            },
            summary=f"{truck.name} rerouted via {location.name} — {len(affected_ids)} packages delayed",
        ))

        return {
            "truck_id": truck_id,
            "status": truck.status,
            "via_point": {"name": location.name, "lat": location.lat, "lng": location.lng, "reason": reason},
            "affected_packages": affected_ids,
        }
