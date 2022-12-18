import os
from pathlib import Path
import logging
from typing import List

from pydantic import BaseSettings, Field


BASE_DIR = Path(__file__).resolve().parent.parent

# конфиг для логгирования
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR, 'postgres_to_es/py_log.log'),
                    filemode="w", format="%(asctime)s %(levelname)s %(message)s")


class DatabaseSettings(BaseSettings):
    dbname: str = Field(env="DB_NAME")
    user: str = Field(env="DB_USER")
    password: str = Field(env="DB_PASSWORD")
    host: str = Field(env="DB_HOST")
    port: int = Field(5432, env="DB_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ElasticSearchSettings(BaseSettings):
    host: str = Field('127.0.0.1', env="EL_HOST")
    port: int = Field(9200, env="El_PORT")
    storage: str = Field("state.txt", env="EL_STORAGE")
    index_name: str = Field("movies", env="INDEX_NAME")
    create_index: bool = Field(True, env="CREATE_INDEX")
    index_settings: str = Field(env="INDEX_SETTINGS")

    @property
    def get_connection(self) -> List[dict]:
        return [{"host": self.host, "port": self.port}]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = DatabaseSettings()
etl_settings = ElasticSearchSettings()

