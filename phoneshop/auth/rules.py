class AccessRules(object):
    rules = {
        "adminmenu": {
            "admin": True
        },
        "logon": {
            "unknown": True
        },
        "changeuser": {
            "admin": True,
            "user": True,
        },
    }

    def __init__(self, user):
        self.user = user

    def is_allow(self, rule):
        return self.rules.get(rule, dict()).get(self.user.role, False)

