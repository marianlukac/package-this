"""ManagerActionsService — 7 manager-only actions."""
import json
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.audit.logger import AuditLogger
from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.customer import Customer
from app.models.employee import Employee, PersonaType
from app.models.package import TERMINAL_STATUSES, Package
from app.models.package_history import PackageHistory, PackageHistoryEventType
from app.schemas.manager_action import ManagerActionRequest, ManagerActionResponse


def _require_manager(actor: Employee) -> None:
    if actor.persona != PersonaType.MANAGER:
        raise HTTPException(
            status_code=403,
            detail=f"Manager persona required. Current persona: {actor.persona} ({actor.name}).",
        )


def _add_package_history(
    session: Session, package_id: str, actor: Employee,
    action: str, source: str, reason: str, payload: dict,
) -> None:
    session.add(PackageHistory(
        package_id=package_id,
        event_type=PackageHistoryEventType.MANAGER_ACTION_PERFORMED,
        actor_id=actor.employee_id, actor_name=actor.name,
        timestamp=datetime.utcnow(), source=source,
        entity_type="package", entity_id=package_id,
        new_value=json.dumps({"action": action, **payload}),
        reason=reason,
    ))


class ManagerActionsService:
    @staticmethod
    async def perform_action(
        session: Session, actor: Employee, request: ManagerActionRequest,
    ) -> ManagerActionResponse:
        _require_manager(actor)

        dispatch = {
            "approve_reroute": ManagerActionsService._approve_reroute,
            "override_priority": ManagerActionsService._override_priority,
            "mark_customer_unhappy": ManagerActionsService._mark_customer_unhappy,
            "approve_return": ManagerActionsService._approve_return,
            "approve_expensive_delivery": ManagerActionsService._approve_expensive_delivery,
            "force_truck_reassignment": ManagerActionsService._force_truck_reassignment,
            "trigger_demo_scenario": ManagerActionsService._trigger_demo_scenario,
        }

        handler = dispatch.get(request.action)
        if not handler:
            raise HTTPException(status_code=422, detail=f"Unknown action: '{request.action}'.")

        await handler(session, actor, request)
        return ManagerActionResponse(action=request.action, status="applied", entity_id=request.entity_id)

    @staticmethod
    async def _approve_reroute(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        pkg = session.exec(select(Package).where(Package.package_id == request.entity_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{request.entity_id}' not found.")

        _add_package_history(session, pkg.package_id, actor, "approve_reroute", request.source,
                             request.reason, request.payload)
        AuditLogger.log(session, actor, request.source, "package", pkg.package_id, "approve_reroute",
                        new_value=request.payload, reason=request.reason)
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="manager.action.performed", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=request.source, entity_type="package", entity_id=pkg.package_id,
            payload={"action": "approve_reroute", **request.payload, "reason": request.reason},
            summary=f"Michael approved reroute for {pkg.package_id}: {request.reason}",
        ))

    @staticmethod
    async def _override_priority(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        pkg = session.exec(select(Package).where(Package.package_id == request.entity_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{request.entity_id}' not found.")
        if pkg.status in TERMINAL_STATUSES:
            raise HTTPException(status_code=409, detail="Cannot override priority on a terminal package.")

        prev_priority = pkg.priority
        new_priority = request.payload.get("priority", pkg.priority)
        pkg.priority = new_priority
        pkg.updated_at = datetime.utcnow()

        _add_package_history(session, pkg.package_id, actor, "override_priority", request.source,
                             request.reason, {"previous_priority": prev_priority, "new_priority": new_priority})
        AuditLogger.log(session, actor, request.source, "package", pkg.package_id, "override_priority",
                        previous_value={"priority": prev_priority}, new_value={"priority": new_priority},
                        reason=request.reason)
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="manager.action.performed", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=request.source, entity_type="package", entity_id=pkg.package_id,
            payload={"action": "override_priority", "previous_priority": prev_priority,
                     "new_priority": new_priority, "reason": request.reason},
            summary=f"Michael overrode priority on {pkg.package_id}: {prev_priority} → {new_priority}",
        ))

    @staticmethod
    async def _mark_customer_unhappy(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        customer = session.exec(select(Customer).where(Customer.customer_id == request.entity_id)).first()
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer '{request.entity_id}' not found.")

        customer.is_unhappy = True
        AuditLogger.log(session, actor, request.source, "customer", customer.customer_id,
                        "mark_customer_unhappy", reason=request.reason)
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="manager.action.performed", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=request.source, entity_type="customer", entity_id=customer.customer_id,
            payload={"action": "mark_customer_unhappy", "reason": request.reason},
            summary=f"Michael marked {customer.name} as unhappy: {request.reason}",
        ))

    @staticmethod
    async def _approve_return(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        from app.services.package_service import PackageService
        await PackageService.approve_return(
            session, actor, request.entity_id, request.reason, request.source
        )

    @staticmethod
    async def _approve_expensive_delivery(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        pkg = session.exec(select(Package).where(Package.package_id == request.entity_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{request.entity_id}' not found.")

        _add_package_history(session, pkg.package_id, actor, "approve_expensive_delivery",
                             request.source, request.reason, request.payload)
        AuditLogger.log(session, actor, request.source, "package", pkg.package_id,
                        "approve_expensive_delivery", new_value=request.payload, reason=request.reason)
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="manager.action.performed", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=request.source, entity_type="package", entity_id=pkg.package_id,
            payload={"action": "approve_expensive_delivery", **request.payload, "reason": request.reason},
            summary=f"Michael approved expensive delivery for {pkg.package_id}",
        ))

    @staticmethod
    async def _force_truck_reassignment(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        pkg = session.exec(select(Package).where(Package.package_id == request.entity_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{request.entity_id}' not found.")

        new_truck_id = request.payload.get("new_truck_id")
        prev_truck = pkg.truck_id
        if new_truck_id:
            pkg.truck_id = new_truck_id
            pkg.updated_at = datetime.utcnow()

        _add_package_history(session, pkg.package_id, actor, "force_truck_reassignment",
                             request.source, request.reason,
                             {"previous_truck": prev_truck, "new_truck": new_truck_id})
        AuditLogger.log(session, actor, request.source, "package", pkg.package_id,
                        "force_truck_reassignment",
                        previous_value={"truck_id": prev_truck}, new_value={"truck_id": new_truck_id},
                        reason=request.reason)
        session.commit()

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="manager.action.performed", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=request.source, entity_type="package", entity_id=pkg.package_id,
            payload={"action": "force_truck_reassignment", "previous_truck": prev_truck,
                     "new_truck": new_truck_id, "reason": request.reason},
            summary=f"Michael forced truck reassignment for {pkg.package_id}: {prev_truck} → {new_truck_id}",
        ))

    @staticmethod
    async def _trigger_demo_scenario(session: Session, actor: Employee, request: ManagerActionRequest) -> None:
        from app.services.demo_service import DemoService
        scenario_name = request.payload.get("scenario_name", request.entity_id)
        await DemoService.run_scenario(session, actor, scenario_name, request.source)
