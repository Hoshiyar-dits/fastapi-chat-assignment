from fastapi import APIRouter, status

from app.authentication.dependencies import AuthService
from app.authentication.dto import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    TokenResponse,
)
from app.user.dto import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    payload: SignupRequest,
    service: AuthService,
):
    return await service.signup(
        first_name=payload.first_name,
        last_name=payload.last_name,
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    payload: LoginRequest,
    service: AuthService,
):
    user, access_token, expires_in = await service.login(
        email=payload.email,
        password=payload.password,
    )

    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        ),
    )
