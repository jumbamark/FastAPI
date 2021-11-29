from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str  # for json web tokens
    algorithm: str  # for signing our token
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
print(settings.database_name)
