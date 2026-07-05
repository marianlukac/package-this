from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.persona.middleware import require_permission
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(
    status: str | None = None,
    sale_id: str | None = None,
    package_id: str | None = None,
    session: Session = Depends(get_session),
):
    return ComplaintService.get_all(session, status=status, sale_id=sale_id, package_id=package_id)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str, session: Session = Depends(get_session)):
    result = ComplaintService.get_by_id(session, complaint_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found.")
    return result


@router.post("", response_model=ComplaintResponse, status_code=201)
async def create_complaint(
    body: ComplaintCreate,
    actor=Depends(require_permission("create_complaint")),
    session: Session = Depends(get_session),
):
    return await ComplaintService.create_complaint(
        session, actor, body.sale_id, body.package_ids, body.description
    )


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: str,
    body: ComplaintUpdate,
    actor=Depends(require_permission("update_complaint")),
    session: Session = Depends(get_session),
):
    return await ComplaintService.update_complaint(session, actor, complaint_id, body.description)


@router.post("/{complaint_id}/close", response_model=ComplaintResponse)
async def close_complaint(
    complaint_id: str,
    actor=Depends(require_permission("close_complaint")),
    session: Session = Depends(get_session),
):
    return await ComplaintService.close_complaint(session, actor, complaint_id)
