# Настройки проекта
from core.browser import Browser
from core.settings import DATABASE
from phoneshop.auth.access import Access
from phoneshop.auth.user import User
from phoneshop.db.db import DB
from phoneshop.db.loadbase import load_phone_base



if __name__ == "__main__":
    database = DB(DATABASE['SQLITE'])
    user = User(database)
    access = Access(user)

    # user.set_role({
    #     "login": "unknown admin",
    #     "role": "admin",
    #     "description": "Хитрый админ",
    # })

    # Первичное наполнение базы данных
    # # load_phone_base()

    browser = Browser(database, user, access)
