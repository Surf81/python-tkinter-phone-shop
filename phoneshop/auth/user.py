import tkinter as tk

class User(object):
    default_user = {
        "login": None,
        "firsname": "unknown",
        "secondname": "",
        "patronymic": "",
        "role": "unknown",
        "role_descriptor": "Не зарегистрирован",
    }

    def __init__(self, db_manager):
        self.user = dict(self.default_user)
        self.db_manager = db_manager

    def logon(self, login, password):
        roles = self.db_manager.check_user(login, password)
        if not roles:
            self.user = dict(self.default_user)
            return False
        return roles

    def new_user(self, userdata):
        roles = self.db_manager.new_user(userdata)
        if not roles:
            self.user = dict(self.default_user)
            return False
        return roles

    def is_free_login(self, login):
        return self.db_manager.is_free_login(login)

    def set_role(self, role=None):
        if role:
            self.user = {
                "login": role["login"],
                "firsname": role.get("firstname", ""),
                "secondname": role.get("secondname", ""),
                "patronymic": role.get("patronymic", ""),
                "role": role["role"],
                "role_descriptor": role["description"],
            }
        else:
            self.user = dict(self.default_user)

    @property
    def role(self):
        return self.user.get("role")
