from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.invoice import InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=list[InvoiceResponse])
def list_invoices(session: Session = Depends(get_session)):
    return InvoiceService.get_all(session)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str, session: Session = Depends(get_session)):
    invoice = InvoiceService.get_by_id(session, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")
    return invoice
