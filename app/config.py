from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    aws_master_username: str
    aws_master_password: str
    aws_database_name: str
    aws_database_endpoint: str
    aws_database_port: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    bucket_name: str
    bucket_name_for_logo: str
    sns_topic_arn: str

    class Config:
        env_file = ".env"


settings = Settings()
