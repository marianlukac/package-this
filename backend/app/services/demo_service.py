"""DemoService — reset and pre-scripted demo scenarios."""
import asyncio
import uuid

from sqlmodel import Session, text

from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.employee import Employee
from app.services.package_service import PackageService


class DemoService:
    @staticmethod
    def reset(session: Session) -> dict:
        """Truncate all data tables (FK-safe order) and re-run seed."""
        tables = [
            "domain_event", "audit_log", "package_history", "complaint_package",
            "complaint", "package_line_item", "package",
            "invoice", "sale",
            "via_point", "route_stop", "truck_route",
            "truck", "map_location", "customer", "employee",
        ]
        for table in tables:
            session.exec(text(f"DELETE FROM {table}"))
        session.commit()

        from seed.seed_data import seed
        seed(session)

        from sqlmodel import func, select

        from app.models.employee import Employee as Emp
        from app.models.package import Package
        pkg_count = session.exec(select(func.count(Package.id))).one()
        emp_count = session.exec(select(func.count(Emp.id))).one()

        return {"status": "reset_complete", "seeded_packages": pkg_count, "seeded_employees": emp_count}

    @staticmethod
    async def run_scenario(
        session: Session, actor: Employee, scenario_name: str, source: str = "demo",
    ) -> dict:
        scenarios = {
            "delayed-delivery": DemoService._scenario_delayed_delivery,
            "damaged-in-transit": DemoService._scenario_damaged_in_transit,
            "happy-customer": DemoService._scenario_happy_customer,
            "manager-reroute": DemoService._scenario_manager_reroute,
            "complaint-and-return": DemoService._scenario_complaint_and_return,
            "kevin-hunger-reroute": DemoService._scenario_kevin_hunger_reroute,
        }
        handler = scenarios.get(scenario_name)
        if not handler:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Unknown scenario: '{scenario_name}'.")

        # Generate one correlation ID for the entire scenario so all events are linked
        correlation_id = str(uuid.uuid4())
        affected = await handler(session, actor, source, correlation_id)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="demo.scenario.triggered", topic="manager-actions",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            actor_type="demo", source=source,
            entity_type="scenario", entity_id=scenario_name,
            payload={"scenario": scenario_name, "affected_packages": affected},
            summary=f"Demo scenario '{scenario_name}' triggered by {actor.name}",
            correlation_id=correlation_id,
        ))

        return {"scenario": scenario_name, "status": "executed", "affected_packages": affected}

    @staticmethod
    async def _scenario_delayed_delivery(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        await PackageService.record_delay(
            session, actor, "PKG-2024-010",
            "Road closed due to Pretzel Day crowd", 4.0, source
        )
        return ["PKG-2024-010"]

    @staticmethod
    async def _scenario_damaged_in_transit(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        pkg = await PackageService.advance_status(
            session, actor, "PKG-2024-006", "damaged",
            "Package dropped during transfer at Scranton hub", source,
            correlation_id=correlation_id,
        )
        return [pkg.package_id]

    @staticmethod
    async def _scenario_happy_customer(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        pkg = await PackageService.advance_status(
            session, actor, "PKG-2024-003", "ready_for_shipping",
            "All items verified and packed", source,
            correlation_id=correlation_id,
        )
        await asyncio.sleep(0.5)
        pkg2 = await PackageService.advance_status(
            session, actor, "PKG-2024-003", "shipped", "Dispatched via DM-TRUCK-02", source,
            correlation_id=correlation_id,
        )
        return [pkg.package_id]

    @staticmethod
    async def _scenario_manager_reroute(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        await PackageService.update_fields(
            session, actor, "PKG-2024-001",
            type("Upd", (), {"current_location": None, "destination": None, "truck_id": "DM-TRUCK-02",
                             "expected_delivery": None, "priority": "urgent", "contents_summary": None,
                             "fragile": None, "source": source})()
        )
        return ["PKG-2024-001"]

    @staticmethod
    async def _scenario_complaint_and_return(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        from app.services.complaint_service import ComplaintService
        await ComplaintService.create_complaint(
            session, actor, "SALE-2024-005",
            ["PKG-2024-013"], "Package returned — wrong item delivered.", source
        )
        return ["PKG-2024-013"]

    @staticmethod
    async def _scenario_kevin_hunger_reroute(
        session: Session, actor: Employee, source: str, correlation_id: str,
    ) -> list[str]:
        """Kevin redirects the truck for a snack detour, causing a delay."""
        from sqlmodel import select

        from app.models.package import Package

        pkg = session.exec(
            select(Package)
            .where(Package.salesperson_id == "kevin-malone")
            .where(Package.delay_reason.is_(None))
        ).first()

        if not pkg:
            pkg = session.exec(
                select(Package)
                .where(Package.delay_reason.is_(None))
            ).first()

        if not pkg:
            return []

        await PackageService.record_delay(
            session, actor, pkg.package_id,
            "Truck rerouted — driver hungry", 1.0, source,
        )
        return [pkg.package_id]
