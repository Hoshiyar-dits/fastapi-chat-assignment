from app.conversation.dto import ConversationResponse
from app.user.dto import UserResponse


class StudioConversationResponse(ConversationResponse):
    user: UserResponse
