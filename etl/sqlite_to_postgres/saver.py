from dataclasses import astuple
from logging import getLogger

import psycopg2

from settings import schema


def field_formater(raw_dict: dict) -> dict:
    """Функция, исправляющия поля created_at и updated_at"""

    if "created_at" and "updated_at" in raw_dict:
        raw_dict["created"] = raw_dict.pop("created_at")
        raw_dict["modified"] = raw_dict.pop("updated_at")
    elif "created_at" in raw_dict:
        raw_dict["created"] = raw_dict.pop("created_at")
    elif "updated_at" in raw_dict:
        raw_dict["modified"] = raw_dict.pop("updated_at")
    return raw_dict


class PostgresSaver:
    def __init__(self, pg_conn):
        self.connection = pg_conn
        self._logger = getLogger()

    def save_all_data(self, data, model, table):
        """Основной метод сохранения данных в Postgres"""

        _curs = self._get_cursor()
        for raw in data:
            raw_dict = field_formater(dict(raw))
            try:
                raw_values = self.__get_values(model, raw_dict)
                query = self._get_query(table, model)
                _curs.execute(query, raw_values)
                self.connection.commit()
            except psycopg2.IntegrityError as err:
                self._logger.error(err)

    def _get_cursor(self):
        return self.connection.cursor()

    def __get_values(self, model, raw_dict: dict) -> tuple:
        """Получение значений необходимых для вставки в Postgres"""

        ex_model = model(**raw_dict)
        return astuple(ex_model)

    def get_model_keys(self, model):
        model_keys = model.__dataclass_fields__.keys()
        return model_keys

    def get_fields(self, model):
        model_keys = self.get_model_keys(model)
        fields = ', '.join(field for field in model_keys)
        return fields

    def get_quantity_values(self, model):
        model_keys = self.get_model_keys(model)
        quantity = ['%s' for key in range(len(model_keys))]
        quantity_values = ', '.join(elem for elem in quantity)
        return quantity_values

    def _get_query(self, table, model):
        """Получение запроса для вставки в Postgres"""

        fields = self.get_fields(model)
        quantity_values = self.get_quantity_values(model)
        query = "INSERT INTO {schema}.{table} ({fields}) VALUES ({quantity_values}) " \
                "ON CONFLICT (id) DO NOTHING; ".format(fields=fields,
                                                       quantity_values=quantity_values,
                                                       schema=schema,
                                                       table=table)
        return query
