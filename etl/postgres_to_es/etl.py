import json
import logging
import time
from functools import wraps

from elasticsearch import helpers, Elasticsearch
from psycopg2.extensions import connection as _connection

from postgres_to_es.loader import PostgresLoader
from postgres_to_es.state import State


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            n = 1
            sleep_time = start_sleep_time * factor ** n
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    logging.critical(ex)
                    if sleep_time < border_sleep_time:
                        time.sleep(sleep_time)
                        n += 1
                        sleep_time = start_sleep_time * factor ** n
                    else:
                        time.sleep(border_sleep_time)

        return inner

    return func_wrapper


class ElSearchSaver:
    def __init__(self, es_object):
        self.es_object = es_object

    def bulk_save(self, transform_data: list) -> None:
        """Загрузить пачкой документов в индекс"""
        helpers.bulk(self.es_object, transform_data)

    def create_index(self, name: str, settings: dict) -> bool:
        """Создать индекс"""
        try:
            self.es_object.indices.create(index=name, body=settings)
            return True
        except Exception as ex:
            logging.critical(ex)

    def check_index(self, name: str) -> bool:
        """Проверить наличие индекса"""
        try:
            return True if self.es_object.indices.exists(name) else False
        except Exception as ex:
            logging.critical(ex)

    def save_document(self, index_name: str, data: dict) -> None:
        """Создать и сохранить документы по одному (медленно)"""
        for doc in data:
            doc = json.dumps({key: value for key, value in doc.items()})
            self.es_object.index(index=index_name, body=doc)


class ETLProcess:
    def __init__(self, state: State, es_object: Elasticsearch, pg_conn: _connection) -> None:
        self.state = state
        self.els_saver = ElSearchSaver(es_object)
        self.postgres_loader = PostgresLoader(pg_conn)

    @backoff()
    def extract(self) -> (dict, dict):
        """Взять состояние и учитывая состояние
        получить данные из PostgreSQL и новое состояние"""
        try:
            state = self.state.get_state('modified')
        except FileNotFoundError:
            logging.warning('State does not exist. It will be created')
            self.state.set_state('modified', '1101-08-10')
            state = self.state.get_state('modified')

        films_id, new_state = self.postgres_loader.get_films_id(state)

        if state == new_state:
            return 0, new_state

        data = self.postgres_loader.load_data(tuple(films_id))
        return data, new_state

    @backoff()
    def transform(self, data: dict, index_name: str, index_settings: dict) -> list:
        """Создать индекс и преобразовать данные в нужный формат для загрузки в ElasticSearch"""
        if not self.els_saver.check_index(index_name):
            self.els_saver.create_index(index_name, index_settings)
            logging.info('Index created')

        transform_data = [
            {
                "_index": index_name,
                "_id": doc["id"],
                "_source": json.dumps({key: value for key, value in doc.items()})
            }
            for doc in data
        ]

        return transform_data

    @backoff()
    def loader(self, transform_data: list, new_state: dict) -> None:
        """Загрузить данные в Elasticsearch и обновить состояние"""
        self.els_saver.bulk_save(transform_data)
        # сохранить новое состояние
        self.state.set_state('modified', new_state)
