from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.authentication.dependencies import StudioUser, get_studio_user
from app.conversation.dto import MessageResponse
from app.core.params import ConversationId, PaginationParams
from app.studio.dependencies import StudioServiceDep
from app.studio.dto import (
    StudioConversationDetailResponse,
    StudioConversationResponse,
    StudioReplyRequest,
)


# Every route here requires an admin or sub-admin token.
router = APIRouter(
    prefix="/studio",
    tags=["Studio"],
    dependencies=[Depends(get_studio_user)],
)


@router.get(
    "/conversations",
    response_model=list[StudioConversationResponse],
)
async def list_conversations(
    pagination: PaginationParams,
    service: StudioServiceDep,
    user_id: Annotated[
        int | None,
        Query(gt=0, description="Only show conversations of this user"),
    ] = None,
):
    return await service.list_conversations(
        limit=pagination.limit,
        offset=pagination.offset,
        user_id=user_id,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=StudioConversationDetailResponse,
)
async def get_conversation(
    conversation_id: ConversationId,
    service: StudioServiceDep,
):
    return await service.get_conversation(
        conversation_id=conversation_id,
    )


@router.post(
    "/conversations/{conversation_id}/reply",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def reply_to_conversation(
    conversation_id: ConversationId,
    payload: StudioReplyRequest,
    staff_user: StudioUser,
    service: StudioServiceDep,
):
    return await service.reply(
        conversation_id=conversation_id,
        staff_user_id=staff_user.id,
        content=payload.content,
    )
