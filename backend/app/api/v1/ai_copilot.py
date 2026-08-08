"""
AI Fleet Copilot API Router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai_copilot import AICopilotQueryRequest, AICopilotQueryResponse
from app.services.ai_copilot_service import AICopilotService

router = APIRouter(prefix="/copilot", tags=["AI Fleet Copilot"])


@router.post("/chat", response_model=AICopilotQueryResponse)
def chat_with_copilot(
    request: AICopilotQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conversational AI Copilot natural language fleet query endpoint."""
    service = AICopilotService(db)
    return service.process_query(request)
