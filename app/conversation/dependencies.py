from typing import Annotated

from fastapi import Depends

from app.conversation.repository import ConversationRepository
from app.conversation.service import ConversationService
from app.database.session import DbSession


def get_conversation_service(db: DbSession) -> ConversationService:
    return ConversationService(
        conversation_repository=ConversationRepository(db),
    )


ConversationServiceDep = Annotated[
    ConversationService,
    Depends(get_conversation_service),
]
