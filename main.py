# Настройки проекта
from core.browser import Browser
from core.settings import DATABASE
from core.db.database import SQLiteDatabase


if __name__ == "__main__":
    database = SQLiteDatabase(DATABASE['SQLITE'])

    browser = Browser(database)
    browser.run()
