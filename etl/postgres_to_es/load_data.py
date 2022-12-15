"""Основной файл для загрузки данных из postgres в ElasticSearch"""

import logging
import time

import psycopg2

from settings import ELASTICSEARCH, STORAGE, DATABASE
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from etl import ETLProcess
from state import State, JsonFileStorage


def load_from_postgres(pg_conn: _connection, es_object: Elasticsearch, state: State) -> None:
    """Основной метод загрузки данных из Postgres в ElasticSearch"""
    etl = ETLProcess(state, es_object, pg_conn)
    while True:
        data, new_state = etl.extract()
        logging.info('Data taken from Postgres')

        if len(data) == 0:
            logging.info('Download completed successfully')
            return

        transform_data = etl.transform(data)

        etl.load(transform_data, new_state)
        logging.info('Data saved in ElasticSearch')


if __name__ == '__main__':
    es_object = Elasticsearch(ELASTICSEARCH)
    # создадим экземпляр состояния
    state = State(JsonFileStorage(STORAGE))
    while True:
        # подключаем постгрес  делаем загрузку в эластик
        with psycopg2.connect(**DATABASE, cursor_factory=DictCursor) as pg_conn:
            load_from_postgres(pg_conn, es_object, state)
        pg_conn.close()
        time.sleep(100)
