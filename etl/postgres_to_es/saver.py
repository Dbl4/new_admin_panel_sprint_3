import json
import logging

from elasticsearch import helpers, Elasticsearch


class ElSearchSaver:
    def __init__(self, es_object: Elasticsearch) -> None:
        self.es_object = es_object

    def bulk_save(self, transform_data: list) -> None:
        """Загрузить пачкой документов в индекс"""
        helpers.bulk(self.es_object, transform_data)

    def create_index(self, name: str, settings: str) -> bool:
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
