from pydantic import BaseModel

from app.authentication.dto.token_response import TokenResponse
from app.user.dto import UserResponse


class LoginResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
