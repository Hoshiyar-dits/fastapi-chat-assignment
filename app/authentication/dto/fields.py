"""Reusable validated field types for authentication DTOs."""

from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, EmailStr, StringConstraints

from app.core.security import BCRYPT_MAX_PASSWORD_BYTES


def _check_password_bytes(password: str) -> str:
    if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password must be at most {BCRYPT_MAX_PASSWORD_BYTES} bytes"
        )

    return password


def _normalize_username(value: object) -> object:
    # Runs before the pattern check, which StringConstraints applies to
    # the raw input.
    return value.strip().lower() if isinstance(value, str) else value


# EmailStr lowercases only the domain; lowercase the whole address so
# "John@x.com" and "john@x.com" are the same account.
NormalizedEmail = Annotated[
    EmailStr,
    AfterValidator(str.lower),
]

PersonName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]

Username = Annotated[
    str,
    BeforeValidator(_normalize_username),
    StringConstraints(
        min_length=3,
        max_length=100,
        pattern=r"^[a-z0-9_.-]+$",
    ),
]

# Passwords are never stripped: whitespace is a legitimate character.
NewPassword = Annotated[
    str,
    StringConstraints(min_length=8, max_length=BCRYPT_MAX_PASSWORD_BYTES),
    AfterValidator(_check_password_bytes),
]
