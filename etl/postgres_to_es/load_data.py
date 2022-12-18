"""Основной файл для загрузки данных из postgres в ElasticSearch"""
import logging
import time

import psycopg2

from loader import MoviesLoader, T
from settings import etl_settings, settings
from elasticsearch import Elasticsearch
from psycopg2.extras import DictCursor

from etl import ETLProcess
from state import State, JsonFileStorage


def load_from_postgres(postgres_loader: T, es_object: Elasticsearch, state: State) -> None:
    """Основной метод загрузки данных из Postgres в ElasticSearch"""
    etl = ETLProcess(state, es_object, postgres_loader)
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
    es_object = Elasticsearch(etl_settings.get_connection)
    # создадим экземпляр состояния
    state = State(JsonFileStorage(etl_settings.storage))
    while True:
        # подключаем постгрес  делаем загрузку в эластик
        with psycopg2.connect(**settings.__dict__, cursor_factory=DictCursor) as pg_conn:
            movies_loader = MoviesLoader(pg_conn)
            load_from_postgres(movies_loader, es_object, state)
        pg_conn.close()
        time.sleep(100)
