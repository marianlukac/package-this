"""PackageService — all package, line-item, and lifecycle operations."""
import json
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app.audit.logger import AuditLogger
from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.lifecycle.transitions import MissingLineItemsError
from app.lifecycle.validator import LifecycleValidator
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.package import TERMINAL_STATUSES, Package, PackageStatus
from app.models.package_history import PackageHistory, PackageHistoryEventType
from app.models.package_line_item import PackageLineItem
from app.models.sale import Sale
from app.persona.permissions import has_permission
from app.schemas.package import PackageListItem, PackageResponse, PackageUpdate
from app.schemas.package_history import PackageHistoryListResponse, PackageHistoryResponse
from app.schemas.package_line_item import LineItemCreate, LineItemResponse, LineItemUpdate


def _line_items(session: Session, package_id: str) -> list[PackageLineItem]:
    return session.exec(select(PackageLineItem).where(PackageLineItem.package_id == package_id)).all()


def _open_complaint_count(session: Session, package_id: str) -> int:
    from app.models.complaint import Complaint, ComplaintPackage, ComplaintStatus
    count = session.exec(
        select(func.count(Complaint.id))
        .join(ComplaintPackage, Complaint.complaint_id == ComplaintPackage.complaint_id)
        .where(ComplaintPackage.package_id == package_id)
        .where(Complaint.status == ComplaintStatus.OPEN)
    ).one()
    return count


def _to_list_item(session: Session, pkg: Package) -> PackageListItem:
    customer = session.exec(select(Customer).where(Customer.customer_id == pkg.customer_id)).first()
    salesperson = session.exec(select(Employee).where(Employee.employee_id == pkg.salesperson_id)).first()
    inv_emp = session.exec(select(Employee).where(Employee.employee_id == pkg.invoicing_employee_id)).first() if pkg.invoicing_employee_id else None
    return PackageListItem(
        package_id=pkg.package_id, sale_id=pkg.sale_id, invoice_id=pkg.invoice_id,
        customer_id=pkg.customer_id, customer_name=customer.name if customer else pkg.customer_id,
        salesperson_id=pkg.salesperson_id, salesperson_name=salesperson.name if salesperson else pkg.salesperson_id,
        invoicing_employee_id=pkg.invoicing_employee_id,
        invoicing_employee_name=inv_emp.name if inv_emp else pkg.invoicing_employee_id,
        status=pkg.status, priority=pkg.priority, fragile=pkg.fragile,
        contents_summary=pkg.contents_summary, current_location=pkg.current_location,
        truck_id=pkg.truck_id, delay_reason=pkg.delay_reason,
        expected_delivery=pkg.expected_delivery,
        created_at=pkg.created_at, updated_at=pkg.updated_at,
    )


def _to_response(session: Session, pkg: Package) -> PackageResponse:
    customer = session.exec(select(Customer).where(Customer.customer_id == pkg.customer_id)).first()
    salesperson = session.exec(select(Employee).where(Employee.employee_id == pkg.salesperson_id)).first()
    inv_emp = session.exec(select(Employee).where(Employee.employee_id == pkg.invoicing_employee_id)).first()
    items = _line_items(session, pkg.package_id)
    return PackageResponse(
        package_id=pkg.package_id, sale_id=pkg.sale_id, invoice_id=pkg.invoice_id,
        customer_id=pkg.customer_id, customer_name=customer.name if customer else pkg.customer_id,
        salesperson_id=pkg.salesperson_id, salesperson_name=salesperson.name if salesperson else pkg.salesperson_id,
        invoicing_employee_id=pkg.invoicing_employee_id,
        invoicing_employee_name=inv_emp.name if inv_emp else pkg.invoicing_employee_id,
        status=pkg.status, priority=pkg.priority, fragile=pkg.fragile,
        contents_summary=pkg.contents_summary, current_location=pkg.current_location,
        destination=pkg.destination, truck_id=pkg.truck_id, delay_reason=pkg.delay_reason,
        delay_duration_hours=pkg.delay_duration_hours, expected_delivery=pkg.expected_delivery,
        created_at=pkg.created_at, updated_at=pkg.updated_at,
        line_items=[
            LineItemResponse(
                id=li.id, package_id=li.package_id, product_name=li.product_name,
                product_category=li.product_category, quantity=li.quantity,
                unit_description=li.unit_description, product_type=li.product_type,
                fragile=li.fragile,
            ) for li in items
        ],
        open_complaint_count=_open_complaint_count(session, pkg.package_id),
    )


def _add_history(
    session: Session, package_id: str, event_type: str, actor: Employee,
    source: str, prev: dict | None = None, new: dict | None = None,
    reason: str | None = None, correlation_id: str | None = None,
) -> PackageHistory:
    entry = PackageHistory(
        package_id=package_id, event_type=event_type,
        actor_id=actor.employee_id, actor_name=actor.name,
        timestamp=datetime.utcnow(), source=source,
        entity_type="package", entity_id=package_id,
        previous_value=json.dumps(prev) if prev is not None else None,
        new_value=json.dumps(new) if new is not None else None,
        reason=reason, correlation_id=correlation_id,
    )
    session.add(entry)
    return entry


class PackageService:
    @staticmethod
    async def create_package(
        session: Session, actor: Employee, sale_id: str, destination: str,
        priority: str, contents_summary: str, fragile: bool, source: str = "ui",
        correlation_id: str | None = None,
    ) -> PackageResponse:
        sale = session.exec(select(Sale).where(Sale.sale_id == sale_id)).first()
        if not sale:
            raise HTTPException(status_code=404, detail=f"Sale '{sale_id}' not found.")
        invoice = session.exec(select(Invoice).where(Invoice.sale_id == sale_id)).first()

        package_id = f"PKG-{datetime.utcnow().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
        pkg = Package(
            package_id=package_id, sale_id=sale_id,
            invoice_id=invoice.invoice_id if invoice else "",
            customer_id=sale.customer_id, salesperson_id=sale.salesperson_id,
            invoicing_employee_id=actor.employee_id if not invoice else invoice.created_by_id,
            status=PackageStatus.ORDER_CREATED,
            destination=destination, priority=priority,
            contents_summary=contents_summary, fragile=fragile,
        )
        session.add(pkg)
        session.flush()

        _add_history(session, package_id, PackageHistoryEventType.PACKAGE_CREATED, actor, source,
                     new={"status": PackageStatus.ORDER_CREATED}, correlation_id=correlation_id)
        AuditLogger.log(session, actor, source, "package", package_id, "create_package",
                        new_value={"sale_id": sale_id, "status": PackageStatus.ORDER_CREATED},
                        correlation_id=correlation_id)
        session.commit()
        session.refresh(pkg)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="package.created", topic="packages",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="package", entity_id=package_id,
            payload={"package_id": package_id, "sale_id": sale_id, "status": PackageStatus.ORDER_CREATED},
            summary=f"Package {package_id} created by {actor.name}",
            correlation_id=correlation_id,
        ))

        return _to_response(session, pkg)

    @staticmethod
    def get_by_id(session: Session, package_id: str) -> Package | None:
        return session.exec(select(Package).where(Package.package_id == package_id)).first()

    @staticmethod
    def get_all(
        session: Session,
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
    ) -> tuple[list[PackageListItem], int]:
        from sqlmodel import or_
        query = select(Package)

        if status:
            query = query.where(Package.status == status)
        if priority:
            query = query.where(Package.priority == priority)
        if customer_id:
            query = query.where(Package.customer_id == customer_id)
        if salesperson_id:
            query = query.where(Package.salesperson_id == salesperson_id)
        if invoice_creator_id:
            query = query.where(Package.invoicing_employee_id == invoice_creator_id)
        if truck_id:
            query = query.where(Package.truck_id == truck_id)
        if has_delay is True:
            query = query.where(Package.delay_reason.isnot(None))
        elif has_delay is False:
            query = query.where(Package.delay_reason.is_(None))
        if exception_state == "damaged":
            query = query.where(Package.status == "damaged")
        elif exception_state == "cancelled":
            query = query.where(Package.status == "cancelled")
        elif exception_state == "returned":
            query = query.where(Package.status == "returned")
        elif exception_state == "any":
            query = query.where(Package.status.in_(["damaged", "cancelled", "returned"]))
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Package.package_id.ilike(search_term),
                    Package.contents_summary.ilike(search_term),
                )
            )

        count_query = select(func.count(Package.id))
        if status:
            count_query = count_query.where(Package.status == status)
        if priority:
            count_query = count_query.where(Package.priority == priority)
        if customer_id:
            count_query = count_query.where(Package.customer_id == customer_id)
        if salesperson_id:
            count_query = count_query.where(Package.salesperson_id == salesperson_id)
        if invoice_creator_id:
            count_query = count_query.where(Package.invoicing_employee_id == invoice_creator_id)
        if truck_id:
            count_query = count_query.where(Package.truck_id == truck_id)
        if has_delay is True:
            count_query = count_query.where(Package.delay_reason.isnot(None))
        elif has_delay is False:
            count_query = count_query.where(Package.delay_reason.is_(None))
        if exception_state == "any":
            count_query = count_query.where(Package.status.in_(["damaged", "cancelled", "returned"]))
        elif exception_state in ("damaged", "cancelled", "returned"):
            count_query = count_query.where(Package.status == exception_state)
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Package.package_id.ilike(search_term),
                    Package.contents_summary.ilike(search_term),
                )
            )

        total = session.exec(count_query).one()

        if sort_by == "expected_delivery":
            order = Package.expected_delivery.asc()
        elif sort_by == "priority":
            order = Package.priority.asc()
        else:
            order = Package.updated_at.desc()

        packages = session.exec(query.order_by(order).offset(offset).limit(limit)).all()
        return [_to_list_item(session, p) for p in packages], total

    @staticmethod
    def get_history(session: Session, package_id: str) -> PackageHistoryListResponse:
        entries = session.exec(
            select(PackageHistory)
            .where(PackageHistory.package_id == package_id)
            .order_by(PackageHistory.timestamp.desc())
        ).all()
        return PackageHistoryListResponse(
            package_id=package_id,
            history=[
                PackageHistoryResponse(
                    id=e.id, package_id=e.package_id, event_type=e.event_type,
                    actor_id=e.actor_id, actor_name=e.actor_name, timestamp=e.timestamp,
                    source=e.source, entity_type=e.entity_type, entity_id=e.entity_id,
                    previous_value=e.previous_value, new_value=e.new_value,
                    reason=e.reason, correlation_id=e.correlation_id,
                ) for e in entries
            ],
        )

    @staticmethod
    async def advance_status(
        session: Session, actor: Employee, package_id: str, target_status: str,
        reason: str | None, source: str, correlation_id: str | None = None,
    ) -> PackageResponse:
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")

        if pkg.status == PackageStatus.ORDER_CREATED:
            items = _line_items(session, package_id)
            if len(items) == 0:
                raise MissingLineItemsError()

        if target_status == PackageStatus.CANCELLED:
            required_op = "cancel_package"
        elif target_status == PackageStatus.DAMAGED:
            required_op = "record_damage"
        else:
            required_op = "advance_lifecycle"

        if not has_permission(actor.persona, required_op):
            raise HTTPException(
                status_code=403,
                detail=f"Persona '{actor.persona}' ({actor.name}) does not have permission for '{required_op}'.",
            )

        prev_status = pkg.status
        LifecycleValidator.validate(prev_status, target_status)

        pkg.status = target_status
        pkg.updated_at = datetime.utcnow()

        event_type_map = {
            PackageStatus.DELIVERED: PackageHistoryEventType.DELIVERED,
            PackageStatus.CANCELLED: PackageHistoryEventType.CANCELLED,
            PackageStatus.DAMAGED: PackageHistoryEventType.DAMAGED,
            PackageStatus.RETURNED: PackageHistoryEventType.RETURNED,
        }
        history_event_type = event_type_map.get(target_status, PackageHistoryEventType.STATUS_CHANGED)

        _add_history(session, package_id, history_event_type, actor, source,
                     prev={"status": prev_status}, new={"status": target_status},
                     reason=reason, correlation_id=correlation_id)
        AuditLogger.log(session, actor, source, "package", package_id, "status_changed",
                        previous_value={"status": prev_status}, new_value={"status": target_status},
                        reason=reason, correlation_id=correlation_id)
        session.commit()
        session.refresh(pkg)

        # Map terminal statuses to specific event types; all others use package.status.updated
        domain_event_map = {
            PackageStatus.DELIVERED: "package.delivered",
            PackageStatus.CANCELLED: "package.cancelled",
            PackageStatus.DAMAGED: "package.damaged",
            PackageStatus.RETURNED: "package.returned",
        }
        event_type_str = domain_event_map.get(target_status, "package.status.updated")
        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type=event_type_str, topic="package-status",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="package", entity_id=package_id,
            payload={"package_id": package_id, "previous_status": prev_status,
                     "new_status": target_status, "reason": reason},
            summary=f"Package {package_id} moved from {prev_status} to {target_status} by {actor.name}",
            correlation_id=correlation_id,
        ))

        return _to_response(session, pkg)

    @staticmethod
    async def record_delay(
        session: Session, actor: Employee, package_id: str,
        delay_reason: str, delay_duration_hours: float, source: str = "ui",
    ) -> PackageResponse:
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
        if pkg.status in TERMINAL_STATUSES:
            raise HTTPException(status_code=409, detail="Cannot record delay on a terminal package.")

        prev = {"delay_reason": pkg.delay_reason, "delay_duration_hours": pkg.delay_duration_hours}
        pkg.delay_reason = delay_reason
        pkg.delay_duration_hours = delay_duration_hours
        pkg.updated_at = datetime.utcnow()

        _add_history(session, package_id, PackageHistoryEventType.DELAY_RECORDED, actor, source,
                     prev=prev, new={"delay_reason": delay_reason, "delay_duration_hours": delay_duration_hours})
        AuditLogger.log(session, actor, source, "package", package_id, "record_delay",
                        previous_value=prev,
                        new_value={"delay_reason": delay_reason, "delay_duration_hours": delay_duration_hours})
        session.commit()
        session.refresh(pkg)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="package.delay.recorded", topic="package-status",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="package", entity_id=package_id,
            payload={"package_id": package_id, "current_status": pkg.status,
                     "delay_reason": delay_reason, "delay_duration_hours": delay_duration_hours},
            summary=f"Delay recorded on {package_id}: {delay_reason}",
        ))

        return _to_response(session, pkg)

    @staticmethod
    async def approve_return(
        session: Session, actor: Employee, package_id: str,
        reason: str, source: str = "ui",
    ) -> PackageResponse:
        """Used directly by manager approve_return action."""
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
        if pkg.status not in (PackageStatus.IN_TRANSIT, PackageStatus.DELIVERED):
            raise HTTPException(
                status_code=409,
                detail=f"Approve return requires 'in_transit' or 'delivered' status. Current: '{pkg.status}'.",
            )

        return await PackageService.advance_status(
            session, actor, package_id, PackageStatus.RETURNED, reason, source
        )

    @staticmethod
    async def update_fields(
        session: Session, actor: Employee, package_id: str,
        update_data: PackageUpdate,
    ) -> PackageResponse:
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
        if pkg.status in TERMINAL_STATUSES:
            raise HTTPException(status_code=409, detail="Cannot edit a terminal package.")

        prev = {"priority": pkg.priority, "destination": pkg.destination, "contents_summary": pkg.contents_summary}
        if update_data.current_location is not None:
            pkg.current_location = update_data.current_location
        if update_data.destination is not None:
            pkg.destination = update_data.destination
        if update_data.truck_id is not None:
            pkg.truck_id = update_data.truck_id
        if update_data.expected_delivery is not None:
            pkg.expected_delivery = update_data.expected_delivery
        if update_data.priority is not None:
            pkg.priority = update_data.priority
        if update_data.contents_summary is not None:
            pkg.contents_summary = update_data.contents_summary
        if update_data.fragile is not None:
            pkg.fragile = update_data.fragile
        pkg.updated_at = datetime.utcnow()

        new = {"priority": pkg.priority, "destination": pkg.destination}
        _add_history(session, package_id, PackageHistoryEventType.LOCATION_UPDATED, actor,
                     update_data.source, prev=prev, new=new)
        AuditLogger.log(session, actor, update_data.source, "package", package_id, "update_fields",
                        previous_value=prev, new_value=new)
        session.commit()
        session.refresh(pkg)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="package.updated", topic="packages",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=update_data.source, entity_type="package", entity_id=package_id,
            payload={"package_id": package_id, "previous": prev, "new": new},
            summary=f"Package {package_id} fields updated by {actor.name}",
        ))

        return _to_response(session, pkg)

    @staticmethod
    async def delete_package(
        session: Session, actor: Employee, package_id: str, source: str = "ui",
    ) -> None:
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")
        if pkg.status != PackageStatus.ORDER_CREATED:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a package that has progressed past order_created.",
            )
        AuditLogger.log(session, actor, source, "package", package_id, "delete_package",
                        previous_value={"status": pkg.status})
        session.delete(pkg)
        session.commit()

    @staticmethod
    async def add_line_item(
        session: Session, actor: Employee, package_id: str,
        data: LineItemCreate, source: str = "ui",
    ) -> LineItemResponse:
        pkg = session.exec(select(Package).where(Package.package_id == package_id)).first()
        if not pkg:
            raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found.")

        item = PackageLineItem(
            package_id=package_id, product_name=data.product_name,
            product_category=data.product_category, quantity=data.quantity,
            unit_description=data.unit_description, product_type=data.product_type,
            fragile=data.fragile,
        )
        session.add(item)
        _add_history(session, package_id, PackageHistoryEventType.LINE_ITEM_ADDED, actor, source,
                     new={"product_name": data.product_name, "quantity": data.quantity})
        AuditLogger.log(session, actor, source, "package", package_id, "add_line_item",
                        new_value={"product_name": data.product_name})
        session.commit()
        session.refresh(item)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="package.line_item_added", topic="packages",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="package", entity_id=package_id,
            payload={"package_id": package_id, "product_name": data.product_name},
            summary=f"Line item '{data.product_name}' added to {package_id}",
        ))

        return LineItemResponse(
            id=item.id, package_id=item.package_id, product_name=item.product_name,
            product_category=item.product_category, quantity=item.quantity,
            unit_description=item.unit_description, product_type=item.product_type,
            fragile=item.fragile,
        )

    @staticmethod
    async def update_line_item(
        session: Session, actor: Employee, package_id: str, item_id: int,
        data: LineItemUpdate, source: str = "ui",
    ) -> LineItemResponse:
        item = session.exec(
            select(PackageLineItem)
            .where(PackageLineItem.id == item_id)
            .where(PackageLineItem.package_id == package_id)
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="Line item not found.")

        prev = {"product_name": item.product_name, "quantity": item.quantity}
        if data.product_name is not None:
            item.product_name = data.product_name
        if data.product_category is not None:
            item.product_category = data.product_category
        if data.quantity is not None:
            item.quantity = data.quantity
        if data.unit_description is not None:
            item.unit_description = data.unit_description
        if data.product_type is not None:
            item.product_type = data.product_type
        if data.fragile is not None:
            item.fragile = data.fragile

        _add_history(session, package_id, PackageHistoryEventType.LINE_ITEM_CHANGED, actor, source,
                     prev=prev, new={"product_name": item.product_name, "quantity": item.quantity})
        AuditLogger.log(session, actor, source, "package", package_id, "update_line_item",
                        previous_value=prev, new_value={"product_name": item.product_name})
        session.commit()
        session.refresh(item)

        return LineItemResponse(
            id=item.id, package_id=item.package_id, product_name=item.product_name,
            product_category=item.product_category, quantity=item.quantity,
            unit_description=item.unit_description, product_type=item.product_type,
            fragile=item.fragile,
        )

    @staticmethod
    async def remove_line_item(
        session: Session, actor: Employee, package_id: str, item_id: int, source: str = "ui",
    ) -> None:
        item = session.exec(
            select(PackageLineItem)
            .where(PackageLineItem.id == item_id)
            .where(PackageLineItem.package_id == package_id)
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="Line item not found.")

        existing = _line_items(session, package_id)
        if len(existing) <= 1:
            raise HTTPException(
                status_code=409,
                detail="Cannot remove the last line item from a package.",
            )

        AuditLogger.log(session, actor, source, "package", package_id, "remove_line_item",
                        previous_value={"product_name": item.product_name})
        session.delete(item)
        session.commit()

    @staticmethod
    def get_at_risk(session: Session) -> list[PackageListItem]:
        from datetime import timedelta
        now = datetime.utcnow()
        packages = session.exec(select(Package)).all()
        result = []
        for pkg in packages:
            if pkg.status in TERMINAL_STATUSES:
                continue
            is_delayed = pkg.delay_reason is not None
            is_approaching = pkg.expected_delivery and pkg.expected_delivery < now + timedelta(hours=2)
            has_complaint = _open_complaint_count(session, pkg.package_id) > 0
            if is_delayed or is_approaching or has_complaint:
                result.append(_to_list_item(session, pkg))
        return result

    @staticmethod
    def get_delayed(session: Session) -> list[PackageListItem]:
        packages = session.exec(
            select(Package).where(Package.delay_reason.isnot(None))
        ).all()
        return [_to_list_item(session, p) for p in packages if p.status not in TERMINAL_STATUSES]
