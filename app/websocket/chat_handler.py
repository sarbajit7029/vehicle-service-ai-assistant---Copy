from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.models.chat_session import ChatSession
from app.db.session import SessionLocal
from app.services.chat_service import send_chat_message
from app.websocket.manager import manager


router = APIRouter(tags=["WebSocket Chat"])


def get_user_from_token(
    db: Session,
    token: str,
) -> User | None:
    """
    Validate the JWT and return the corresponding user.

    This reuses the project's existing JWT decoding function.
    """

    try:
        payload = decode_access_token(token)
    except Exception:
        return None

    if not payload:
        return None

    subject = payload.get("sub")

    if subject is None:
        return None

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        return None

    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
        )
    )

    return user


def verify_session_owner(
    db: Session,
    session_id: int,
    user_id: int,
) -> bool:
    """
    Make sure the WebSocket user owns the requested chat session.
    """

    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
    )

    return session is not None


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: int,
) -> None:
    """
    WebSocket endpoint for real-time vehicle-service chat.

    Authentication:
        /ws/chat/{session_id}?token=<JWT>

    The actual chat business logic is handled by chat_service.py.
    """

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token is required.",
        )
        return

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. AUTHENTICATION
        # ---------------------------------------------------------

        current_user = get_user_from_token(
            db=db,
            token=token,
        )

        if current_user is None:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid or expired authentication token.",
            )
            return

        # ---------------------------------------------------------
        # 2. SESSION OWNERSHIP
        # ---------------------------------------------------------

        if not verify_session_owner(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        ):
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Chat session does not belong to this user.",
            )
            return

        # ---------------------------------------------------------
        # 3. CONNECT
        # ---------------------------------------------------------

        await manager.connect(
            websocket=websocket,
            session_id=session_id,
        )

        await manager.send_json(
            session_id,
            {
                "type": "connected",
                "session_id": session_id,
                "message": "WebSocket chat connected.",
            },
        )

        # ---------------------------------------------------------
        # 4. RECEIVE MESSAGES
        # ---------------------------------------------------------

        while True:
            data = await websocket.receive_json()

            question = data.get("question")

            if not isinstance(question, str) or not question.strip():
                await manager.send_json(
                    session_id,
                    {
                        "type": "error",
                        "message": "Question cannot be empty.",
                    },
                )
                continue

            question = question.strip()

            # -----------------------------------------------------
            # 5. REUSE CHAT SERVICE
            # -----------------------------------------------------

            try:
                result = send_chat_message(
                    db=db,
                    current_user=current_user,
                    question=question,
                    session_id=session_id,
                )

                # -------------------------------------------------
                # 6. SEND AI RESPONSE
                # -------------------------------------------------

                await manager.send_json(
                    session_id,
                    {
                        "type": "message",
                        "session_id": result.session_id,
                        "question": question,
                        "answer": result.answer,
                        "sources": result.sources,
                        "safety_flag": result.safety_flag,
                    },
                )

            except Exception:
                db.rollback()

                await manager.send_json(
                    session_id,
                    {
                        "type": "error",
                        "message": (
                            "An error occurred while processing "
                            "your message."
                        ),
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)

    except Exception:
        manager.disconnect(session_id)

        try:
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Internal WebSocket error.",
            )
        except Exception:
            pass

    finally:
        manager.disconnect(session_id)
        db.close()