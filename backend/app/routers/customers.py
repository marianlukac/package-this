from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.complaint import ComplaintResponse
from app.schemas.customer import CustomerResponse
from app.services.complaint_service import ComplaintService
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers(session: Session = Depends(get_session)):
    return CustomerService.get_all(session)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, session: Session = Depends(get_session)):
    customer = CustomerService.get_by_id(session, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return CustomerResponse(
        id=customer.id, customer_id=customer.customer_id, name=customer.name,
        address=customer.address, city=customer.city, state=customer.state,
        lat=customer.lat, lng=customer.lng, is_unhappy=customer.is_unhappy,
        contact_name=customer.contact_name, contact_email=customer.contact_email,
    )


@router.get("/{customer_id}/complaints", response_model=list[ComplaintResponse])
def get_customer_complaints(customer_id: str, session: Session = Depends(get_session)):
    return ComplaintService.get_by_customer(session, customer_id)
