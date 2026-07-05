from sqlmodel import Session, select

from app.models.customer import Customer
from app.schemas.customer import CustomerResponse


def _to_response(c: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=c.id, customer_id=c.customer_id, name=c.name, address=c.address,
        city=c.city, state=c.state, lat=c.lat, lng=c.lng,
        is_unhappy=c.is_unhappy, contact_name=c.contact_name, contact_email=c.contact_email,
    )


class CustomerService:
    @staticmethod
    def get_all(session: Session) -> list[CustomerResponse]:
        customers = session.exec(select(Customer).order_by(Customer.name)).all()
        return [_to_response(c) for c in customers]

    @staticmethod
    def get_by_id(session: Session, customer_id: str) -> Customer | None:
        return session.exec(select(Customer).where(Customer.customer_id == customer_id)).first()
