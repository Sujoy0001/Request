from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	neon_db: str = Field(default="", repr=False)

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)


@lru_cache
def get_settings() -> Settings:
	settings = Settings()
	if not settings.neon_db:
		raise ValueError("neon_db must be set in the environment or .env file")
	return settings
