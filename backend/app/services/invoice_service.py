from sqlmodel import Session, select

from app.models.employee import Employee
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse


def _to_response(session: Session, inv: Invoice) -> InvoiceResponse:
    creator = session.exec(select(Employee).where(Employee.employee_id == inv.created_by_id)).first()
    return InvoiceResponse(
        id=inv.id, invoice_id=inv.invoice_id, sale_id=inv.sale_id,
        created_by_id=inv.created_by_id,
        created_by_name=creator.name if creator else inv.created_by_id,
        created_at=inv.created_at, notes=inv.notes,
    )


class InvoiceService:
    @staticmethod
    def get_by_id(session: Session, invoice_id: str) -> InvoiceResponse | None:
        inv = session.exec(select(Invoice).where(Invoice.invoice_id == invoice_id)).first()
        if not inv:
            return None
        return _to_response(session, inv)

    @staticmethod
    def get_all(session: Session) -> list[InvoiceResponse]:
        invoices = session.exec(select(Invoice).order_by(Invoice.created_at.desc())).all()
        return [_to_response(session, inv) for inv in invoices]
