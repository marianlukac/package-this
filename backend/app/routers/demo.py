from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.persona.middleware import require_manager
from app.services.demo_service import DemoService

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/reset", response_model=dict)
async def reset_demo(
    actor=Depends(require_manager),
    session: Session = Depends(get_session),
):
    DemoService.reset(session)
    return {"status": "ok", "message": "Demo data reset to baseline."}


@router.post("/scenarios/{scenario_name}", response_model=dict)
async def run_scenario(
    scenario_name: str,
    actor=Depends(require_manager),
    session: Session = Depends(get_session),
):
    await DemoService.run_scenario(session, actor, scenario_name, source="demo")
    return {"status": "ok", "scenario": scenario_name}
