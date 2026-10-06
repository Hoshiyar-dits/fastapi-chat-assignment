from pydantic import BaseModel, Field

from app.authentication.dto.fields import NormalizedEmail
from app.core.security import BCRYPT_MAX_PASSWORD_BYTES


class LoginRequest(BaseModel):
    email: NormalizedEmail
    # No minimum beyond non-empty: login must not leak or depend on the
    # signup password policy, which may change over time.
    password: str = Field(
        min_length=1,
        max_length=BCRYPT_MAX_PASSWORD_BYTES,
    )
