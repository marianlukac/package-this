"""Dunder Mifflin Package Manager — FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import create_db_and_tables
from app.events.publisher import get_publisher, reset_publisher
from app.lifecycle.transitions import InvalidTransitionError, MissingLineItemsError
from app.persona.middleware import PersonaMiddleware
from app.realtime.broadcaster import get_broadcaster, reset_broadcaster
from app.realtime.websocket import ws_manager
from app.routers import (
    complaints,
    customers,
    demo,
    employees,
    events,
    invoices,
    manager_actions,
    packages,
    routes,
    sales,
    trucks,
)
from app.routers import (
    map as map_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    create_db_and_tables()
    get_publisher()
    get_broadcaster()

    # Seed baseline data if the database is empty
    try:
        from sqlmodel import Session, select
        from app.database import get_engine
        from app.models.employee import Employee
        from seed.seed_data import seed
        with Session(get_engine()) as session:
            if not session.exec(select(Employee)).first():
                seed(session)
    except Exception:
        pass

    # Start simulation engine if enabled
    if settings.app_env != "test":
        try:
            from app.simulation.engine import SimulationEngine
            engine = SimulationEngine()
            import asyncio
            task = asyncio.create_task(engine.run())
            app.state.simulation_task = task
        except Exception:
            pass

    yield

    if hasattr(app.state, "simulation_task"):
        app.state.simulation_task.cancel()

    reset_publisher()
    reset_broadcaster()


app = FastAPI(
    title="Dunder Mifflin Package Manager",
    description="Official trainer baseline for the Agentic AI workshop.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permissive for workshop use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persona middleware — resolves X-Persona-Id header on every request
app.add_middleware(PersonaMiddleware)


# --- Exception handlers ---

@app.exception_handler(InvalidTransitionError)
async def invalid_transition_handler(request, exc: InvalidTransitionError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(MissingLineItemsError)
async def missing_line_items_handler(request, exc: MissingLineItemsError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


# --- Routers ---

app.include_router(packages.router)
app.include_router(sales.router)
app.include_router(invoices.router)
app.include_router(customers.router)
app.include_router(employees.router)
app.include_router(trucks.router)
app.include_router(routes.router)
app.include_router(map_router.router)
app.include_router(events.router)
app.include_router(complaints.router)
app.include_router(manager_actions.router)
app.include_router(demo.router)


# --- WebSocket endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; all broadcasting is server-initiated
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# --- Operational summary ---

@app.get("/operational-summary", tags=["Packages"])
def operational_summary():
    """MCP-friendly snapshot of current operational state."""
    from sqlmodel import Session, func, select

    from app.database import get_engine
    from app.models.complaint import Complaint, ComplaintStatus
    from app.models.customer import Customer
    from app.models.package import TERMINAL_STATUSES, Package, PackageStatus
    from app.models.truck import Truck, TruckStatus

    engine = get_engine()
    with Session(engine) as session:
        total_packages = session.exec(select(func.count(Package.id))).one()
        active_packages = session.exec(
            select(func.count(Package.id)).where(Package.status.not_in(list(TERMINAL_STATUSES)))
        ).one()
        in_transit = session.exec(
            select(func.count(Package.id)).where(Package.status == PackageStatus.IN_TRANSIT)
        ).one()
        delayed = session.exec(
            select(func.count(Package.id)).where(Package.delay_reason.isnot(None))
        ).one()
        open_complaints = session.exec(
            select(func.count(Complaint.id)).where(Complaint.status == ComplaintStatus.OPEN)
        ).one()
        active_trucks = session.exec(
            select(func.count(Truck.id)).where(Truck.status == TruckStatus.IN_TRANSIT)
        ).one()
        backorder_count = session.exec(
            select(func.count(Package.id)).where(Package.status == PackageStatus.BACKORDER)
        ).one()
        order_created_count = session.exec(
            select(func.count(Package.id)).where(Package.status == PackageStatus.ORDER_CREATED)
        ).one()
        customer_unhappy_count = session.exec(
            select(func.count(Customer.id)).where(Customer.is_unhappy == True)  # noqa: E712
        ).one()

    return {
        "total_packages": total_packages,
        "active_packages": active_packages,
        "in_transit": in_transit,
        "delayed": delayed,
        "open_complaints": open_complaints,
        "active_trucks": active_trucks,
        "backorder_count": backorder_count,
        "order_created_count": order_created_count,
        "customer_unhappy_count": customer_unhappy_count,
    }


@app.get("/health", tags=["Demo"])
def health():
    return {"status": "ok", "service": "dm-package-manager"}
