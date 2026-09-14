from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatResponse,
)
from app.services.chat_service import (
    create_chat_session,
    get_chat_history,
    send_chat_message,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = create_chat_session(
        db=db,
        current_user=current_user,
    )

    return {
        "session_id": session.id,
    }


@router.post(
    "",
    response_model=ChatResponse,
)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = send_chat_message(
        db=db,
        current_user=current_user,
        question=request.question,
        session_id=request.session_id,
    )

    return ChatResponse(
        answer=result.answer,
        sources=result.sources,
        session_id=result.session_id,
        safety_flag=result.safety_flag,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=ChatHistoryResponse,
)
def get_session_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = get_chat_history(
        db=db,
        current_user=current_user,
        session_id=session_id,
    )

    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
    )