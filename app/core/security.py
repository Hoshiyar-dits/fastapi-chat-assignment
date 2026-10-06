import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings


# bcrypt only uses the first 72 bytes of a password; longer input is
# rejected at validation time instead of being silently truncated.
BCRYPT_MAX_PASSWORD_BYTES = 72

ACCESS_TOKEN_TYPE = "access"


def _hash_password_sync(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def _verify_password_sync(
    plain_password: str,
    password_hash: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        # Malformed hash stored in the database.
        return False


# Compared against when a login email does not exist, so the response
# time does not reveal which emails are registered.
_DUMMY_PASSWORD_HASH = _hash_password_sync(uuid4().hex)


# bcrypt is deliberately slow (~100ms+) and CPU bound; running it in a
# worker thread keeps the event loop free for other requests.
async def hash_password(password: str) -> str:
    return await asyncio.to_thread(
        _hash_password_sync,
        password,
    )


async def verify_password(
    plain_password: str,
    password_hash: str | None,
) -> bool:
    """Verify a password; pass None when the user does not exist."""

    is_valid = await asyncio.to_thread(
        _verify_password_sync,
        plain_password,
        password_hash or _DUMMY_PASSWORD_HASH,
    )

    return is_valid and password_hash is not None


def create_access_token(user_id: int) -> tuple[str, int]:
    expires_in = settings.jwt_access_token_expire_minutes * 60

    expire = datetime.now(UTC) + timedelta(
        seconds=expires_in
    )

    payload = {
        "sub": str(user_id),
        "jti": uuid4().hex,
        "exp": expire,
        "type": ACCESS_TOKEN_TYPE,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_in


def decode_access_token(token: str) -> int | None:
    """Return the user id from a valid access token, or None."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require_exp": True,
                "require_sub": True,
            },
        )
    except JWTError:
        return None

    if payload.get("type") != ACCESS_TOKEN_TYPE:
        return None

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject.isdigit():
        return None

    return int(subject)
