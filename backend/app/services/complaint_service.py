"""ComplaintService — create, update, close, and query complaints."""
import json
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.audit.logger import AuditLogger
from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.complaint import Complaint, ComplaintPackage, ComplaintStatus
from app.models.employee import Employee
from app.models.package import Package
from app.models.package_history import PackageHistory, PackageHistoryEventType
from app.schemas.complaint import ComplaintResponse


def _get_package_ids(session: Session, complaint_id: str) -> list[str]:
    links = session.exec(select(ComplaintPackage).where(ComplaintPackage.complaint_id == complaint_id)).all()
    return [lnk.package_id for lnk in links]


def _to_response(session: Session, complaint: Complaint) -> ComplaintResponse:
    from app.models.employee import Employee
    creator = session.exec(select(Employee).where(Employee.employee_id == complaint.created_by_id)).first()
    package_ids = _get_package_ids(session, complaint.complaint_id)
    return ComplaintResponse(
        id=complaint.id, complaint_id=complaint.complaint_id, sale_id=complaint.sale_id,
        description=complaint.description, status=complaint.status,
        created_by_id=complaint.created_by_id,
        created_by_name=creator.name if creator else complaint.created_by_id,
        package_ids=package_ids,
        created_at=complaint.created_at, updated_at=complaint.updated_at,
        closed_at=complaint.closed_at, source=complaint.source,
    )


def _add_package_history(
    session: Session, package_id: str, event_type: str, actor: Employee,
    source: str, new: dict | None = None,
) -> None:
    session.add(PackageHistory(
        package_id=package_id, event_type=event_type,
        actor_id=actor.employee_id, actor_name=actor.name,
        timestamp=datetime.utcnow(), source=source,
        entity_type="package", entity_id=package_id,
        new_value=json.dumps(new) if new else None,
    ))


class ComplaintService:
    @staticmethod
    async def create_complaint(
        session: Session, actor: Employee,
        sale_id: str, package_ids: list[str],
        description: str, source: str = "ui",
    ) -> ComplaintResponse:
        from app.models.sale import Sale
        sale = session.exec(select(Sale).where(Sale.sale_id == sale_id)).first()
        if not sale:
            raise HTTPException(status_code=404, detail=f"Sale '{sale_id}' not found.")

        for pid in package_ids:
            pkg = session.exec(select(Package).where(Package.package_id == pid).where(Package.sale_id == sale_id)).first()
            if not pkg:
                raise HTTPException(
                    status_code=422,
                    detail=f"Package '{pid}' does not belong to sale '{sale_id}'.",
                )

        complaint_id = f"CMP-{datetime.utcnow().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
        complaint = Complaint(
            complaint_id=complaint_id, sale_id=sale_id,
            description=description, status=ComplaintStatus.OPEN,
            created_by_id=actor.employee_id, source=source,
        )
        session.add(complaint)
        session.flush()

        for pid in package_ids:
            session.add(ComplaintPackage(complaint_id=complaint_id, package_id=pid))
            _add_package_history(session, pid, PackageHistoryEventType.COMPLAINT_CREATED, actor, source,
                                 new={"complaint_id": complaint_id, "description": description})

        AuditLogger.log(session, actor, source, "complaint", complaint_id, "create_complaint",
                        new_value={"sale_id": sale_id, "package_count": len(package_ids)})
        session.commit()
        session.refresh(complaint)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="complaint.created", topic="complaints",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="complaint", entity_id=complaint_id,
            payload={"complaint_id": complaint_id, "sale_id": sale_id,
                     "package_ids": package_ids, "description": description},
            summary=f"Complaint {complaint_id} created by {actor.name}",
        ))

        return _to_response(session, complaint)

    @staticmethod
    async def update_complaint(
        session: Session, actor: Employee,
        complaint_id: str, description: str, source: str = "ui",
    ) -> ComplaintResponse:
        complaint = session.exec(select(Complaint).where(Complaint.complaint_id == complaint_id)).first()
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found.")
        if complaint.status == ComplaintStatus.CLOSED:
            raise HTTPException(status_code=409, detail="Cannot update a closed complaint.")

        prev_desc = complaint.description
        complaint.description = description
        complaint.updated_at = datetime.utcnow()

        package_ids = _get_package_ids(session, complaint_id)
        for pid in package_ids:
            _add_package_history(session, pid, PackageHistoryEventType.COMPLAINT_UPDATED, actor, source,
                                 new={"complaint_id": complaint_id, "description": description})

        AuditLogger.log(session, actor, source, "complaint", complaint_id, "update_complaint",
                        previous_value={"description": prev_desc}, new_value={"description": description})
        session.commit()
        session.refresh(complaint)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="complaint.updated", topic="complaints",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="complaint", entity_id=complaint_id,
            payload={"complaint_id": complaint_id, "description": description},
            summary=f"Complaint {complaint_id} updated by {actor.name}",
        ))

        return _to_response(session, complaint)

    @staticmethod
    async def close_complaint(
        session: Session, actor: Employee, complaint_id: str, source: str = "ui",
    ) -> ComplaintResponse:
        complaint = session.exec(select(Complaint).where(Complaint.complaint_id == complaint_id)).first()
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found.")
        if complaint.status == ComplaintStatus.CLOSED:
            raise HTTPException(status_code=409, detail="Complaint is already closed.")

        complaint.status = ComplaintStatus.CLOSED
        complaint.closed_at = datetime.utcnow()
        complaint.updated_at = datetime.utcnow()

        package_ids = _get_package_ids(session, complaint_id)
        for pid in package_ids:
            _add_package_history(session, pid, PackageHistoryEventType.COMPLAINT_UPDATED, actor, source,
                                 new={"complaint_id": complaint_id, "status": "closed"})

        AuditLogger.log(session, actor, source, "complaint", complaint_id, "close_complaint",
                        new_value={"status": "closed"})
        session.commit()
        session.refresh(complaint)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="complaint.updated", topic="complaints",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="complaint", entity_id=complaint_id,
            payload={"complaint_id": complaint_id, "status": "closed"},
            summary=f"Complaint {complaint_id} closed by {actor.name}",
        ))

        return _to_response(session, complaint)

    @staticmethod
    def get_by_id(session: Session, complaint_id: str) -> ComplaintResponse | None:
        complaint = session.exec(select(Complaint).where(Complaint.complaint_id == complaint_id)).first()
        if not complaint:
            return None
        return _to_response(session, complaint)

    @staticmethod
    def get_all(
        session: Session, status: str | None = None, sale_id: str | None = None,
        package_id: str | None = None,
    ) -> list[ComplaintResponse]:
        if package_id:
            links = session.exec(select(ComplaintPackage).where(ComplaintPackage.package_id == package_id)).all()
            complaint_ids = [lnk.complaint_id for lnk in links]
            complaints = session.exec(select(Complaint).where(Complaint.complaint_id.in_(complaint_ids))).all()
        else:
            query = select(Complaint)
            if status:
                query = query.where(Complaint.status == status)
            if sale_id:
                query = query.where(Complaint.sale_id == sale_id)
            complaints = session.exec(query.order_by(Complaint.created_at.desc())).all()
        return [_to_response(session, c) for c in complaints]

    @staticmethod
    def get_by_customer(session: Session, customer_id: str) -> list[ComplaintResponse]:
        from app.models.sale import Sale
        sales = session.exec(select(Sale).where(Sale.customer_id == customer_id)).all()
        sale_ids = [s.sale_id for s in sales]
        complaints = session.exec(select(Complaint).where(Complaint.sale_id.in_(sale_ids))).all()
        return [_to_response(session, c) for c in complaints]
