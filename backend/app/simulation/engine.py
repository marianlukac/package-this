"""SimulationEngine — background task driving truck movement ticks."""
import asyncio

from sqlmodel import Session, select

from app.config import get_settings
from app.database import get_engine
from app.models.truck import Truck, TruckStatus
from app.simulation.tick import process_truck_tick

ACTIVE_STATUSES = (TruckStatus.ON_ROUTE, TruckStatus.REROUTED, TruckStatus.RETURNING)


class SimulationEngine:
    def __init__(self) -> None:
        self._tick = 0

    async def run(self) -> None:
        settings = get_settings()
        interval = settings.simulation_tick_interval_seconds
        location_every_n = settings.simulation_location_event_every_n_ticks

        while True:
            try:
                await self._tick_all(location_every_n)
            except Exception as exc:
                print(f"[SIMULATION] tick error: {exc}")
            self._tick += 1
            await asyncio.sleep(interval)

    async def _tick_all(self, location_every_n: int) -> None:
        engine = get_engine()
        with Session(engine) as session:
            trucks = session.exec(
                select(Truck).where(Truck.status.in_(list(ACTIVE_STATUSES)))
            ).all()
            for truck in trucks:
                await process_truck_tick(session, truck, self._tick, location_every_n)
