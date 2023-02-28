

class User(object):
    default_user = {
        "login": None,
        "firsname": "unknown",
        "secondname": "",
        "patronymic": "",
        "role": "unknown",
        "role_descriptor": "Не зарегистрирован",
    }


    def __init__(self, database):
        self.user = dict(self.default_user)
        self.db = database


    def logon(self, login, password):
        roles = self.db.get_user(login, password)
        if not roles:
            self.user = dict(self.default_user)
            return False
        
        return roles

    def registation(self, userdata):
        roles = self.db.new_user(userdata)
        if not roles:
            self.user = dict(self.default_user)
            return False
        
        return roles
