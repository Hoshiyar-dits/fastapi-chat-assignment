"""
Seed the studio staff accounts (admin and sub-admin).

Run from the project root:

    python -m app.database.seeder

Idempotent: existing accounts are left as they are, except that their
role is corrected if it was changed. All changes are committed in one
transaction, so a failure leaves the database untouched.
"""

import asyncio
import logging
import sys
from dataclasses import dataclass

from pydantic import SecretStr
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings
from app.core.exceptions import ConflictError
from app.core.security import BCRYPT_MAX_PASSWORD_BYTES, hash_password
from app.database.session import SessionLocal, close_database
from app.user.model import UserRole
from app.user.repository import UserRepository


logger = logging.getLogger("seeder")


class SeederError(Exception):
    """Invalid seeder configuration or data conflict."""


@dataclass(frozen=True, slots=True)
class StaffAccount:
    first_name: str
    last_name: str
    username: str
    email: str
    password: SecretStr | None
    role: UserRole
    password_env_var: str


STAFF_ACCOUNTS = (
    StaffAccount(
        first_name="Studio",
        last_name="Admin",
        username=settings.admin_username.lower(),
        email=settings.admin_email.lower(),
        password=settings.admin_password,
        role=UserRole.ADMIN,
        password_env_var="ADMIN_PASSWORD",
    ),
    StaffAccount(
        first_name="Studio",
        last_name="Sub Admin",
        username=settings.sub_admin_username.lower(),
        email=settings.sub_admin_email.lower(),
        password=settings.sub_admin_password,
        role=UserRole.SUB_ADMIN,
        password_env_var="SUB_ADMIN_PASSWORD",
    ),
)


def validate_password(account: StaffAccount) -> str:
    """Fail before touching the database if a password is unusable."""

    if account.password is None or not account.password.get_secret_value():
        raise SeederError(
            f"{account.password_env_var} is not set. "
            f"Add it to .env before running the seeder."
        )

    password = account.password.get_secret_value()

    if len(password) < 8:
        raise SeederError(
            f"{account.password_env_var} must be at least 8 characters."
        )

    if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
        raise SeederError(
            f"{account.password_env_var} must be at most "
            f"{BCRYPT_MAX_PASSWORD_BYTES} bytes."
        )

    return password


async def seed_staff_users() -> None:
    async with SessionLocal() as session:
        repository = UserRepository(session)

        for account in STAFF_ACCOUNTS:
            user = await repository.get_by_email(account.email)

            if user is not None:
                if user.role != account.role:
                    user.role = account.role
                    logger.info(
                        "Updated role of %s to %s",
                        account.email,
                        account.role,
                    )
                else:
                    logger.info("Skipped %s: already exists", account.email)

                continue

            password = validate_password(account)

            if await repository.get_by_username(account.username):
                raise SeederError(
                    f"Username '{account.username}' is already taken "
                    f"by another account."
                )

            await repository.create(
                first_name=account.first_name,
                last_name=account.last_name,
                username=account.username,
                email=account.email,
                password_hash=await hash_password(password),
                role=account.role,
            )

            logger.info("Created %s: %s", account.role, account.email)

        await repository.commit()


async def main() -> int:
    try:
        await seed_staff_users()
    except (SeederError, ConflictError) as exc:
        logger.error("Seeding failed: %s", exc)
        return 1
    except SQLAlchemyError:
        logger.exception("Seeding failed: database error")
        return 1
    finally:
        await close_database()

    logger.info("Seeding completed")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    sys.exit(asyncio.run(main()))
