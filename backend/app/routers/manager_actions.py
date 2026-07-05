from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.persona.middleware import require_manager
from app.schemas.manager_action import ManagerActionRequest, ManagerActionResponse
from app.services.manager_actions_service import ManagerActionsService

router = APIRouter(prefix="/manager-actions", tags=["ManagerActions"])


@router.post("", response_model=ManagerActionResponse)
async def perform_manager_action(
    body: ManagerActionRequest,
    actor=Depends(require_manager),
    session: Session = Depends(get_session),
):
    return await ManagerActionsService.perform_action(session, actor, body)
