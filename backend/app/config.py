from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://dispatch:dispatch@localhost:5432/dispatch"
    database_url_direct: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""  # Supabase Settings → API → JWT Secret (HS256)
    scraperapi_key: str = ""

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    embed_model: str = "text-embedding-3-small"
    gen_model: str = "gpt-4.1-nano"
    frontend_origin: str = "http://localhost:5173"

    classify_prompt: str = ""
    summarize_prompt: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    digest_from: str = "dispatch@example.com"

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    bluesky_identifier: str = ""
    bluesky_app_password: str = ""


settings = Settings()
