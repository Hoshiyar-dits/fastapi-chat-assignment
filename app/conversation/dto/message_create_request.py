from pydantic import BaseModel

from app.conversation.dto.fields import MessageContent


class MessageCreateRequest(BaseModel):
    content: MessageContent
