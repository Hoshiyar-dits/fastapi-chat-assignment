from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError
from app.database.repository import BaseRepository
from app.user.model import User, UserRole


class UserRepository(BaseRepository):

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.username == username,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> User:

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )

        self.db.add(user)

        try:
            await self.db.flush()
        except IntegrityError as exc:
            # Unique constraint hit by a concurrent signup that passed
            # the service's existence checks at the same time.
            await self.db.rollback()
            raise ConflictError(
                "User with this email or username already exists"
            ) from exc

        return user
