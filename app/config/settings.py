from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Chat Assignment"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    database_url: str
    database_echo: bool = False
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    # Recycle before MySQL's wait_timeout drops idle connections.
    database_pool_recycle_seconds: int = Field(default=1800, gt=0)

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, gt=0)

    # Used only by the seeder (python -m app.database.seeder)
    admin_email: str = "admin@example.com"
    admin_username: str = "admin"
    admin_password: SecretStr | None = None

    sub_admin_email: str = "subadmin@example.com"
    sub_admin_username: str = "subadmin"
    sub_admin_password: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
