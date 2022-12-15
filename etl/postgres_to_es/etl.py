import json
import logging
import time
from functools import wraps

from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection

from loader import PostgresLoader
from saver import ElSearchSaver
from settings import INDEX_NAME, CREATE_INDEX, INDEX_SETTINGS
from state import State


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
                    if n >= 6:
                        break
                    if sleep_time < border_sleep_time:
                        time.sleep(sleep_time)
                        n += 1
                        sleep_time = start_sleep_time * factor ** n
                    else:
                        time.sleep(border_sleep_time)

        return inner

    return func_wrapper


class ETLProcess:
    def __init__(self, state: State, es_object: Elasticsearch, pg_conn: _connection) -> None:
        self.state = state
        self.els_saver = ElSearchSaver(es_object)
        self.postgres_loader = PostgresLoader(pg_conn)

    @backoff()
    def extract(self) -> (dict, dict):
        """Взять состояние и учитывая состояние
        получить данные из PostgreSQL и новое состояние."""
        try:
            state = self.state.get_state('modified')
        except FileNotFoundError:
            logging.warning('State does not exist. It will be created')
            self.state.set_state('modified', '1101-08-10')
            state = self.state.get_state('modified')

        films_id, new_state = self.postgres_loader.get_films_id(state)

        if state == new_state:
            return dict(), new_state

        data = self.postgres_loader.load_data(films_id)

        return data, new_state

    @backoff()
    def transform(self, data: dict) -> list:
        """Создать индекс и преобразовать данные в нужный формат для загрузки в ElasticSearch"""
        transform_data = [
            {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": json.dumps({key: value for key, value in doc.items()})
            }
            for doc in data
        ]

        return transform_data

    @backoff()
    def load(self, transform_data: list, new_state: dict) -> None:
        """Создать индекс, загрузить данные в Elasticsearch и обновить состояние"""

        # проверяем наличие индекса, и если необходимо создаем
        if not self.els_saver.check_index(INDEX_NAME):
            if CREATE_INDEX:
                self.els_saver.create_index(INDEX_NAME, INDEX_SETTINGS)
                logging.info(f'Index {INDEX_NAME} created')
            else:
                logging.warning('Index will not created. Сheck your index settings')
                return

        self.els_saver.bulk_save(transform_data)
        # сохранить новое состояние
        self.state.set_state('modified', new_state)
