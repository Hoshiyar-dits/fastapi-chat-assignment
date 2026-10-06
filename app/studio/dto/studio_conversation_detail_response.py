from app.conversation.dto import ConversationDetailResponse
from app.user.dto import UserResponse


class StudioConversationDetailResponse(ConversationDetailResponse):
    user: UserResponse
