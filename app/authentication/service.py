from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    PermissionDeniedError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.user.model import User
from app.user.repository import UserRepository


class AuthenticationService:

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def signup(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str,
    ) -> User:

        if await self.user_repository.get_by_email(email):
            raise ConflictError("User with this email already exists")

        if await self.user_repository.get_by_username(username):
            raise ConflictError("User with this username already exists")

        user = await self.user_repository.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_hash=await hash_password(password),
        )

        await self.user_repository.commit()

        return user

    async def login(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str, int]:
        """Return the user, an access token and its lifetime in seconds."""

        user = await self.user_repository.get_by_email(email)

        # Always run the password check, even for unknown emails, so the
        # response time does not reveal whether the email is registered.
        is_valid = await verify_password(
            password,
            user.password_hash if user else None,
        )

        if user is None or not is_valid:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise PermissionDeniedError("User account is inactive")

        access_token, expires_in = create_access_token(user.id)

        return user, access_token, expires_in
