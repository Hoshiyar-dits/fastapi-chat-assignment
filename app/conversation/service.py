from app.conversation.model import Conversation, Message, MessageRole
from app.conversation.repository import ConversationRepository
from app.core.exceptions import NotFoundError


class ConversationService:

    def __init__(
        self,
        conversation_repository: ConversationRepository,
    ):
        self.conversation_repository = conversation_repository

    async def create_conversation(
        self,
        user_id: int,
        title: str,
        first_message: str | None = None,
    ) -> Conversation:

        conversation = await self.conversation_repository.create(
            user_id=user_id,
            title=title,
        )

        if first_message:
            await self.conversation_repository.add_message(
                conversation=conversation,
                sender_id=user_id,
                role=MessageRole.USER,
                content=first_message,
            )

        await self.conversation_repository.commit()

        return await self.get_conversation(
            conversation_id=conversation.id,
            user_id=user_id,
        )

    async def list_conversations(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[Conversation]:

        return await self.conversation_repository.list_conversations(
            limit=limit,
            offset=offset,
            user_id=user_id,
        )

    async def get_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Conversation:

        conversation = await self.conversation_repository.get(
            conversation_id=conversation_id,
            user_id=user_id,
            with_messages=True,
        )

        # 404 rather than 403 for other users' conversations, so their
        # existence is not revealed.
        if conversation is None:
            raise NotFoundError("Conversation not found")

        return conversation

    async def add_message(
        self,
        conversation_id: int,
        user_id: int,
        content: str,
    ) -> Message:

        conversation = await self.conversation_repository.get(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            raise NotFoundError("Conversation not found")

        message = await self.conversation_repository.add_message(
            conversation=conversation,
            sender_id=user_id,
            role=MessageRole.USER,
            content=content,
        )

        await self.conversation_repository.commit()

        return message
