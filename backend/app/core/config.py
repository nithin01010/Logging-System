from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Observability Platform"
    MONGO_URI: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
