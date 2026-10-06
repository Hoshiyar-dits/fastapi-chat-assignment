from typing import Annotated

from fastapi import Depends

from app.conversation.repository import ConversationRepository
from app.database.session import DbSession
from app.studio.service import StudioService


def get_studio_service(db: DbSession) -> StudioService:
    return StudioService(
        conversation_repository=ConversationRepository(db),
    )


StudioServiceDep = Annotated[StudioService, Depends(get_studio_service)]
