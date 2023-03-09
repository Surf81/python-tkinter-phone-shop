import sqlite3
from os import path
from typing import Any


class SQLiteDatabase:
    """Подключение к базе данных SQLite
        Принимаемое значение: database: str - путь к файлу sqlite
    """
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
        """Возвращает текущее подключение к базе данных
        Returns:
            <class 'sqlite3.Connection'>: текущее подключение к БД
        """
        if self.connected:
            return self._connection
        self._connection = sqlite3.connect(self.database)
        self._connection.row_factory = sqlite3.Row
        self.connected = True

        return self._connection

    def commit(self) -> None:
        """Выполняет commit к базе данных
        """
        self.connection.commit()

    def execute(self, sql: str, *args) -> Any:
        """выполняет запрос к базе данных
        Args:
            sql (str): текст запроса SQL
            *args: перечень значений, передаваемых вместе с запросом (не обязательно)
        Returns:
            <class 'sqlite3.Cursor'>: объект курсора содержащий результат запроса
        """
        return self.connection.execute(sql, args)

    def executemany(self, sql, *args) -> Any:
        """выполняет множественный запрос к базе данных
        Args:
            sql (str): текст запроса SQL
            *args: перечень кортежей значений, передаваемых вместе с запросом
        Returns:
            <class 'sqlite3.Cursor'>: объект курсора содержащий результат запроса
        """
        return self.connection.executemany(sql, args)

    def close(self) -> None:
        """Закрывает соединение с базой данных
        """
        if self.connected:
            self.connection.close()
        self.connected = False
