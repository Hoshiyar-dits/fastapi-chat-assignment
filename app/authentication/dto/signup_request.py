from pydantic import BaseModel

from app.authentication.dto.fields import (
    NewPassword,
    NormalizedEmail,
    PersonName,
    Username,
)


class SignupRequest(BaseModel):
    first_name: PersonName
    last_name: PersonName
    username: Username
    email: NormalizedEmail
    password: NewPassword
