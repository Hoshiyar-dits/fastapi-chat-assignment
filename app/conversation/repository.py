from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.conversation.model import Conversation, Message, MessageRole
from app.database.repository import BaseRepository


class ConversationRepository(BaseRepository):

    async def create(
        self,
        user_id: int,
        title: str,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)

        await self.db.flush()

        return conversation

    async def list_conversations(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
        with_user: bool = False,
    ) -> list[Conversation]:
        """List conversations; user_id=None lists all users' (studio)."""

        query = (
            select(Conversation)
            .where(Conversation.deleted_at.is_(None))
            .order_by(
                Conversation.updated_at.desc(),
                Conversation.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        if user_id is not None:
            query = query.where(Conversation.user_id == user_id)

        if with_user:
            query = query.options(selectinload(Conversation.user))

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get(
        self,
        conversation_id: int,
        user_id: int | None = None,
        with_messages: bool = False,
        with_user: bool = False,
    ) -> Conversation | None:
        """Get one conversation; user_id restricts it to that owner."""

        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None),
        )

        if user_id is not None:
            query = query.where(Conversation.user_id == user_id)

        if with_messages:
            query = query.options(selectinload(Conversation.messages))

        if with_user:
            query = query.options(selectinload(Conversation.user))

        if with_messages or with_user:
            # populate_existing reloads server-generated values
            # (timestamps) on objects already in the session.
            query = query.execution_options(populate_existing=True)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation: Conversation,
        sender_id: int,
        role: MessageRole,
        content: str,
    ) -> Message:

        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            role=role,
            content=content,
        )

        self.db.add(message)

        # Bump the conversation so the most recently active one lists first.
        conversation.updated_at = func.now()

        await self.db.flush()
        await self.db.refresh(message)

        return message
