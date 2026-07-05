"""Shared test fixtures for the DM Package Manager test suite."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.events.inmemory import InMemoryEventPublisher
from app.events.publisher import reset_publisher
from app.main import app
from app.models.customer import Customer
from app.models.employee import Employee, PersonaType
from app.models.invoice import Invoice
from app.models.package import Package, PackagePriority, PackageStatus
from app.models.package_line_item import PackageLineItem, ProductType
from app.models.sale import Sale


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="engine_override")
def engine_override_fixture(engine):
    """Make InMemoryEventPublisher._persist() use the test engine."""
    import app.database as _db
    original = getattr(_db, "_engine", None)
    _db._engine = engine
    yield engine
    _db._engine = original


@pytest.fixture(name="publisher")
def publisher_fixture(engine_override):
    pub = InMemoryEventPublisher()
    import app.events.publisher as _mod
    _mod._publisher_instance = pub
    yield pub
    reset_publisher()


@pytest.fixture(name="client")
def client_fixture(engine, publisher):
    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Pre-built domain objects ---

@pytest.fixture(name="michael")
def michael_fixture(session):
    emp = Employee(
        employee_id="michael-scott", name="Michael Scott",
        persona=PersonaType.MANAGER, title="Regional Manager",
        email="michael@dundermifflin.com",
    )
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture(name="jim")
def jim_fixture(session):
    emp = Employee(
        employee_id="jim-halpert", name="Jim Halpert",
        persona=PersonaType.SALES, title="Sales Representative",
        email="jim@dundermifflin.com",
    )
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture(name="darryl")
def darryl_fixture(session):
    emp = Employee(
        employee_id="darryl-philbin", name="Darryl Philbin",
        persona=PersonaType.WAREHOUSE, title="Warehouse Manager",
        email="darryl@dundermifflin.com",
    )
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture(name="customer")
def customer_fixture(session):
    c = Customer(
        customer_id="CUST-001", name="Vance Refrigeration",
        address="1 Bob Vance Way", city="Scranton", state="PA",
        lat=41.408, lng=-75.662,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@pytest.fixture(name="sale")
def sale_fixture(session, customer, jim):
    s = Sale(sale_id="SALE-001", customer_id=customer.customer_id, salesperson_id=jim.employee_id)
    session.add(s)
    i = Invoice(invoice_id="INV-001", sale_id=s.sale_id, created_by_id=jim.employee_id)
    session.add(i)
    session.commit()
    session.refresh(s)
    return s


@pytest.fixture(name="package")
def package_fixture(session, sale):
    pkg = Package(
        package_id="PKG-2026-AABBCCDD", sale_id=sale.sale_id, invoice_id="INV-001",
        customer_id=sale.customer_id, salesperson_id=sale.salesperson_id,
        invoicing_employee_id=sale.salesperson_id,
        status=PackageStatus.ORDER_CREATED,
        priority=PackagePriority.STANDARD, contents_summary="Reams of paper",
    )
    session.add(pkg)
    item = PackageLineItem(
        package_id=pkg.package_id, product_name="A4 White 80gsm",
        product_category="Paper", quantity=10, unit_description="ream",
        product_type=ProductType.PAPER_PRODUCT, fragile=False,
    )
    session.add(item)
    session.commit()
    session.refresh(pkg)
    return pkg
