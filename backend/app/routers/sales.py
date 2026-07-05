from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.invoice import Invoice
from app.models.package import Package
from app.persona.middleware import require_permission
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=dict[str, Any])
def list_sales(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)):
    sales, total = SaleService.get_all(session, limit, offset)
    return {"items": sales, "total": total, "limit": limit, "offset": offset}


@router.get("/{sale_id}", response_model=dict[str, Any])
def get_sale(sale_id: str, session: Session = Depends(get_session)):
    sale = SaleService.get_by_id(session, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale '{sale_id}' not found.")
    # Attach invoice and packages inline
    invoice = session.exec(select(Invoice).where(Invoice.sale_id == sale_id)).first()
    packages = session.exec(select(Package).where(Package.sale_id == sale_id)).all()
    return {
        **sale.model_dump(),
        "invoice": {"invoice_id": invoice.invoice_id, "created_by_id": invoice.created_by_id} if invoice else None,
        "packages": [{"package_id": p.package_id, "status": p.status, "priority": p.priority} for p in packages],
    }


@router.post("", response_model=SaleResponse, status_code=201)
async def create_sale(
    body: SaleCreate,
    actor=Depends(require_permission("create_sale")),
    session: Session = Depends(get_session),
):
    return await SaleService.create_sale(session, actor, body.customer_id, body.notes)
