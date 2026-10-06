from datetime import datetime

from pydantic import BaseModel

from app.conversation.model import MessageRole


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int | None
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
