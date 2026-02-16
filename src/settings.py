from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    s3_endpoint: str
    s3_bucket: str

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

    redis_host: str
    redis_port: int

    celery_broker_url: str
    celery_result_backend: str

    postgres_database_uri: str
    async_postgres_database_uri: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
