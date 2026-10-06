from fastapi import APIRouter

from app.authentication.dependencies import CurrentUser
from app.user.dto import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(current_user: CurrentUser):
    return current_user
