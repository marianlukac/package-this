import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app.audit.logger import AuditLogger
from app.events.envelope import make_envelope
from app.events.publisher import get_publisher
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.package import Package
from app.models.sale import Sale
from app.schemas.sale import SaleResponse


def _to_response(session: Session, sale: Sale) -> SaleResponse:
    customer = session.exec(select(Customer).where(Customer.customer_id == sale.customer_id)).first()
    salesperson = session.exec(select(Employee).where(Employee.employee_id == sale.salesperson_id)).first()
    invoice = session.exec(select(Invoice).where(Invoice.sale_id == sale.sale_id)).first()
    pkg_count = session.exec(select(func.count(Package.id)).where(Package.sale_id == sale.sale_id)).one()
    return SaleResponse(
        id=sale.id, sale_id=sale.sale_id,
        customer_id=sale.customer_id,
        customer_name=customer.name if customer else sale.customer_id,
        salesperson_id=sale.salesperson_id,
        salesperson_name=salesperson.name if salesperson else sale.salesperson_id,
        invoice_id=invoice.invoice_id if invoice else "",
        notes=sale.notes,
        package_count=pkg_count,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
    )


class SaleService:
    @staticmethod
    async def create_sale(
        session: Session,
        actor: Employee,
        customer_id: str,
        notes: str,
        source: str = "ui",
    ) -> SaleResponse:
        customer = session.exec(select(Customer).where(Customer.customer_id == customer_id)).first()
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")

        sale_id = f"SALE-{datetime.utcnow().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
        sale = Sale(sale_id=sale_id, customer_id=customer_id, salesperson_id=actor.employee_id, notes=notes)
        session.add(sale)
        session.flush()

        invoice_id = f"INV-{datetime.utcnow().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
        invoice = Invoice(invoice_id=invoice_id, sale_id=sale_id, created_by_id=actor.employee_id)
        session.add(invoice)

        AuditLogger.log(session, actor, source, "sale", sale_id, "create_sale",
                        new_value={"customer_id": customer_id})
        session.commit()
        session.refresh(sale)

        publisher = get_publisher()
        await publisher.publish(make_envelope(
            event_type="sale.created", topic="packages",
            actor_id=actor.employee_id, actor_name=actor.name, persona=actor.persona,
            source=source, entity_type="sale", entity_id=sale_id,
            payload={"sale_id": sale_id, "customer_id": customer_id},
            summary=f"Sale {sale_id} created by {actor.name} for {customer.name}",
        ))

        return _to_response(session, sale)

    @staticmethod
    def get_by_id(session: Session, sale_id: str) -> SaleResponse | None:
        sale = session.exec(select(Sale).where(Sale.sale_id == sale_id)).first()
        if not sale:
            return None
        return _to_response(session, sale)

    @staticmethod
    def get_all(session: Session, limit: int = 50, offset: int = 0) -> tuple[list[SaleResponse], int]:
        sales = session.exec(select(Sale).order_by(Sale.created_at.desc()).offset(offset).limit(limit)).all()
        total = session.exec(select(func.count(Sale.id))).one()
        return [_to_response(session, s) for s in sales], total
