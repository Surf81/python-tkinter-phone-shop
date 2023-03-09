import sqlite3
from os import path


class SQLiteDatabase:
    def __init__(self, database: str) -> None:
        self.database = database
        self._connection = None
        self.connected = False
        self.db_empty = False
        self.db_empty = False
        if not path.exists(self.database):
            self.db_empty = True

    @property
    def connection(self):
        if self.connected:
            return self._connection
        self._connection = sqlite3.connect(self.database)
        self._connection.row_factory = sqlite3.Row
        self.connected = True
        return self._connection

    def commit(self):
        self.connection.commit()

    def execute(self, sql, *args):
        return self.connection.execute(sql, args)

    def executemany(self, sql, *args):
        return self.connection.executemany(sql, args)

    def close(self):
        if self.connected:
            self.connection.close()
        self.connected = False
