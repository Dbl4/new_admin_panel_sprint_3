import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from loader import SQLiteLoader
from saver import PostgresSaver
from settings import tables

load_dotenv()


@contextmanager
def conn_sqlite(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_loader = SQLiteLoader(connection)
    postgres_saver = PostgresSaver(pg_conn)

    for model, table in tables.items():
        data = sqlite_loader.get_data(table)
        postgres_saver.save_all_data(data, model, table)


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5432)
    }

    with conn_sqlite('db.sqlite') as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
