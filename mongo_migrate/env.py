from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str | None = Field(default=None, alias="MONGO_HOST")
    port: int | None = Field(default=None, alias="MONGO_PORT")
    username: str | None = Field(default=None, alias="MONGO_INITDB_ROOT_USERNAME")
    password: str | None = Field(default=None, alias="MONGO_INITDB_ROOT_PASSWORD")