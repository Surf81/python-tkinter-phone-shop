# Настройки проекта
from main.browser import Browser
from main.settings import DATABASE
from phoneshop.auth.rules import AccessRules
from phoneshop.auth.user import User
from phoneshop.db.db import DB
from phoneshop.db.loadbase import load_phone_base



database = DB(DATABASE['SQLITE'])
user = User(database)
rules = AccessRules(user)

# Первичное наполнение базы данных
# # load_phone_base()


if __name__ == "__main__":
    browser = Browser(database, user, rules)
