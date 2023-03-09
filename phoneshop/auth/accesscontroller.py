class AccessController(object):
    rules = {
        "adminmenu": {"admin": True},
        "adminpage": {"admin": True},
        "logon": {"unknown": True},
        "changeuser": {
            "admin": True,
            "user": True,
        },
    }

    def __init__(self, user):
        self.user = user

    def is_allow(self, rule: str) -> bool:
        """Возвращает значение правила для текущей учетной записи"""
        return self.rules.get(rule, dict()).get(self.user.role, False)
