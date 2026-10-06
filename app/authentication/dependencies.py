from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.authentication.service import AuthenticationService
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.database.session import DbSession
from app.user.model import STUDIO_ROLES, User
from app.user.repository import UserRepository


def get_authentication_service(db: DbSession) -> AuthenticationService:
    return AuthenticationService(
        user_repository=UserRepository(db),
    )


AuthService = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]


# auto_error=False so a missing header returns our 401, not FastAPI's 403.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: DbSession,
) -> User:

    if credentials is None:
        raise AuthenticationError("Not authenticated")

    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise AuthenticationError("Invalid or expired token")

    user = await UserRepository(db).get_by_id(user_id)

    if user is None:
        raise AuthenticationError("Invalid or expired token")

    if not user.is_active:
        raise PermissionDeniedError("User account is inactive")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_studio_user(current_user: CurrentUser) -> User:
    """Allow only admin and sub-admin users."""

    if current_user.role not in STUDIO_ROLES:
        raise PermissionDeniedError(
            "Studio access requires admin or sub-admin role"
        )

    return current_user


StudioUser = Annotated[User, Depends(get_studio_user)]
