from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.chat_message import ChatMessage
from app.db.models.chat_session import ChatSession
from app.db.models.user import User
from app.schemas.chat import ChatHistoryMessage
from app.services.rag_service import rag_answer


@dataclass(frozen=True)
class ChatServiceResult:
    answer: str
    sources: list[dict]
    session_id: int
    safety_flag: bool


def _get_owned_session(
    db: Session,
    session_id: int,
    user_id: int,
) -> ChatSession:
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    return session


def create_chat_session(
    db: Session,
    current_user: User,
) -> ChatSession:
    session = ChatSession(
        user_id=current_user.id,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_chat_history(
    db: Session,
    current_user: User,
    session_id: int,
) -> list[ChatHistoryMessage]:
    session = _get_owned_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
    ).all()

    return [
        ChatHistoryMessage(
            id=message.id,
            question=message.question,
            answer=message.answer,
            sources=message.sources or [],
            created_at=message.created_at,
        )
        for message in messages
    ]


def send_chat_message(
    db: Session,
    current_user: User,
    question: str,
    session_id: int | None = None,
) -> ChatServiceResult:
    question = question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    # ---------------------------------------------------------
    # 1. Get existing session or create a new one
    # ---------------------------------------------------------
    if session_id is None:
        session = create_chat_session(
            db=db,
            current_user=current_user,
        )
    else:
        session = _get_owned_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )

    # ---------------------------------------------------------
    # 2. Save the user's question
    # ---------------------------------------------------------
    chat_message = ChatMessage(
        session_id=session.id,
        question=question,
        answer="",
        sources=[],
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    try:
        # -----------------------------------------------------
        # 3. Existing RAG pipeline
        #
        # IMPORTANT:
        # Do not duplicate:
        # - safety guard
        # - database fact handling
        # - document retrieval
        # - LLM selection
        # - retrieval-only fallback
        #
        # These already belong to rag_service.py.
        # -----------------------------------------------------
        result = rag_answer(
    db=db,
    question=question,
)

        # -----------------------------------------------------
        # 4. Save answer and sources
        # -----------------------------------------------------
        chat_message.answer = result.answer
        chat_message.sources = result.sources

        db.commit()
        db.refresh(chat_message)

        return ChatServiceResult(
            answer=result.answer,
            sources=result.sources,
            session_id=session.id,
            safety_flag=result.safety_triggered,
        )

    except Exception:
        # -----------------------------------------------------
        # Keep the database consistent if RAG fails.
        # -----------------------------------------------------
        db.rollback()

        raise