from app.conversation.model import Conversation, Message, MessageRole
from app.conversation.repository import ConversationRepository
from app.core.exceptions import NotFoundError


class StudioService:
    """Admin / sub-admin access to every user's conversations."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
    ):
        self.conversation_repository = conversation_repository

    async def list_conversations(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
    ) -> list[Conversation]:

        return await self.conversation_repository.list_conversations(
            limit=limit,
            offset=offset,
            user_id=user_id,
            with_user=True,
        )

    async def get_conversation(
        self,
        conversation_id: int,
    ) -> Conversation:

        conversation = await self.conversation_repository.get(
            conversation_id=conversation_id,
            with_messages=True,
            with_user=True,
        )

        if conversation is None:
            raise NotFoundError("Conversation not found")

        return conversation

    async def reply(
        self,
        conversation_id: int,
        staff_user_id: int,
        content: str,
    ) -> Message:

        conversation = await self.conversation_repository.get(
            conversation_id=conversation_id,
        )

        if conversation is None:
            raise NotFoundError("Conversation not found")

        message = await self.conversation_repository.add_message(
            conversation=conversation,
            sender_id=staff_user_id,
            role=MessageRole.STUDIO,
            content=content,
        )

        await self.conversation_repository.commit()

        return message
