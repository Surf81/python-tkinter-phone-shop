from typing import *

class Router(object):
    def __init__(self, master):
        self.master = master
        self.routers = dict()
        self.history = None

    def __call__(self, label) -> Callable:
        router = self.routers.get(label, None)
        if not router:
            return
        if router.get("history"):
            self.history = router.get("command")
        return router.get("command")


    def register_rout(self, label, command, history=False):
        router = self.routers.setdefault(label, dict())
        router["command"] = command
        router["history"] = history

    def refresh(self):
        if self.history:
            self.history()
