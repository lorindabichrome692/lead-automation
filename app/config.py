from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    airtable_api_key: str
    airtable_base_id: str
    airtable_table_name: str = "Leads"
    resend_api_key: str
    resend_from_email: str  # Use "onboarding@resend.dev" for testing (no domain verification needed)
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
