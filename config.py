from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from pydantic import (
    PostgresDsn,
    MySQLDsn,
    field_validator,
    ValidationError
)
from pydantic_core.core_schema import FieldValidationInfo
from typing import (
    Any,
    Optional
)
from pathlib import Path
import logging
import os


logger = logging.getLogger(__name__)

parent_dir = Path(__file__).parents[1]
env_file = os.path.join('.env')


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    mysql_db: str
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket_name: str
    region_name: str
    model_config = SettingsConfigDict(env_file=env_file)

    postgres_url: Optional[PostgresDsn] = None
    mysql_url: Optional[MySQLDsn] = None

    @field_validator("postgres_url", mode='before')
    @classmethod
    def assemble_pgsql_connection(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        postgres_dsn = PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("postgres_user"),
            password=info.data.get("postgres_password"),
            host=info.data.get("postgres_host"),
            port=info.data.get("postgres_port"),
            path=info.data.get('postgres_db'),
        )
        return str(postgres_dsn)

    @field_validator("mysql_url", mode='before')
    @classmethod
    def assemble_mysql_connection(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        mysql_dsn = MySQLDsn.build(
            scheme="mysql+mysqlconnector",
            username=info.data.get("mysql_user"),
            password=info.data.get("mysql_password"),
            host=info.data.get("mysql_host"),
            port=info.data.get("mysql_port"),
            path=info.data.get('mysql_db'),
        )
        return str(mysql_dsn)


try:
    settings = Settings()
except Exception as e:
    logger.exception(f'Validation failed for system config. Details : {e}')
    exit(1)

