from pydantic import BaseModel

from app.conversation.dto.fields import MessageContent


class StudioReplyRequest(BaseModel):
    content: MessageContent
