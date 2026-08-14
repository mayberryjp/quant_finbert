from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QUANT_FINBERT_", extra="ignore")

    api_listen_address: str = Field("0.0.0.0", validation_alias="API_LISTEN_ADDRESS")
    api_port: int = Field(8023, validation_alias="API_PORT")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    model_name: str = Field("ProsusAI/finbert", validation_alias="MODEL_NAME")
    database_url: str = Field(
        "postgresql+psycopg://quant:quant@q",
        validation_alias="DATABASE_URL",
    )


settings = Settings()  # type: ignore[call-arg]
