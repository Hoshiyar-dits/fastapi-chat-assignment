from app.conversation.dto.conversation_response import ConversationResponse
from app.conversation.dto.message_response import MessageResponse


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]
