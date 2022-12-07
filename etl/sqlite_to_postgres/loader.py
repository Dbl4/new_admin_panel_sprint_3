import sqlite3
from logging import getLogger


class SQLiteLoader:
    def __init__(self, connection):
        self.connection = connection
        self._logger = getLogger()
        self.batch = 100

    def get_data(self, table):
        try:
            _curs = self._get_cursor()
            _curs.execute("SELECT * FROM {table};".format(table=table))
            while True:
                data = _curs.fetchmany(size=self.batch)
                if not data:
                    return
                yield from data
        except sqlite3.DatabaseError as err:
            self._logger.error(err)

    def _get_cursor(self):
        return self.connection.cursor()
