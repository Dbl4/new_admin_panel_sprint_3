"""Основной файл для загрузки данных из postgres в ElasticSearch"""

import logging
import os
import time

import psycopg2
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from postgres_to_es.etl import ETLProcess
from postgres_to_es.settings import index_name, index_settings
from postgres_to_es.state import State, JsonFileStorage

load_dotenv()


def load_from_postgres(pg_conn: _connection, es_object: Elasticsearch, state: State) -> None:
    """Основной метод загрузки данных из Postgres в ElasticSearch"""
    etl = ETLProcess(state, es_object, pg_conn)
    while True:
        data, new_state = etl.extract()
        logging.info('Data taken from Postgres')

        if not data:
            logging.info('Download completed successfully')
            return

        transform_data = etl.transform(data, index_name, index_settings)

        etl.loader(transform_data, new_state)
        logging.info('Data saved in ElasticSearch')
        time.sleep(10)


if __name__ == '__main__':
    es_object = Elasticsearch([{"host": os.environ.get('EL_HOST', '127.0.0.1'),
                                "port": os.environ.get('El_PORT', 9200)}])
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5432)
    }
    # создадим экземпляр состояния
    state = State(JsonFileStorage('state.txt'))
    # подключаем постгрес  делаем загрузку в эластик
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_postgres(pg_conn, es_object, state)
