from fastapi import APIRouter, status

from app.authentication.dependencies import CurrentUser
from app.conversation.dependencies import ConversationServiceDep
from app.conversation.dto import (
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.core.params import ConversationId, PaginationParams


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreateRequest,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return await service.create_conversation(
        user_id=current_user.id,
        title=payload.title,
        first_message=payload.message,
    )


@router.get(
    "",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    pagination: PaginationParams,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return await service.list_conversations(
        user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation(
    conversation_id: ConversationId,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: ConversationId,
    payload: MessageCreateRequest,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return await service.add_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=payload.content,
    )
