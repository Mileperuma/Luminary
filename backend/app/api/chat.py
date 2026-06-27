"""Chat endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.models.chat import ChatSession, ChatSessionType
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    StartChatRequest,
    StartChatResponse,
)
from app.services.chatbot import send_message, start_session

router = APIRouter()


_OPENING_MESSAGES = {
    ChatSessionType.ONBOARDING: (
        "Hi — I'm Luminary. I'll ask a few short questions to learn what you like in "
        "books, articles, and movies. There are no wrong answers and we'll be done in "
        "a couple of minutes. To start: what's the last book, film, or article you "
        "really enjoyed?"
    ),
    ChatSessionType.GENERAL: (
        "Hey, how can I help? You can ask for picks, tweak a preference, or just chat "
        "about something you read or watched."
    ),
}


@router.post("/start", response_model=StartChatResponse, status_code=status.HTTP_201_CREATED)
def start(
    payload: StartChatRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> StartChatResponse:
    chat_session = start_session(session, user=current_user, session_type=payload.session_type)
    return StartChatResponse(
        session_id=chat_session.id,
        opening_message=_OPENING_MESSAGES[payload.session_type],
    )


@router.post("/message", response_model=ChatMessageResponse)
def message(
    payload: ChatMessageRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> ChatMessageResponse:
    chat_session = session.get(ChatSession, payload.session_id)
    if chat_session is None or chat_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="chat session not found")

    reply = send_message(
        session,
        user=current_user,
        chat_session=chat_session,
        content=payload.content,
    )
    return ChatMessageResponse(
        session_id=reply.session_id,
        assistant_message=reply.assistant_message,
        finished=reply.finished,
        captured_preferences=reply.captured_preferences,
    )
