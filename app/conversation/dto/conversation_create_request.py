from pydantic import BaseModel, Field

from app.conversation.dto.fields import ConversationTitle, MessageContent


class ConversationCreateRequest(BaseModel):
    title: ConversationTitle
    message: MessageContent | None = Field(
        default=None,
        description="Optional first message of the conversation",
    )
