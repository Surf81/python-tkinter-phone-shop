from functools import wraps
from typing import *

class Router(object):
    def __init__(self):
        self.routers = dict()
        self.history = None

    def __call__(self, label) -> Callable:
        if self.routers.get(label):
            return self.__call_function_control(label)

    def __call_function_control(self, label):
        @wraps(self.routers[label].get("command"))
        def wrapper(*args, **kwargs):
            router = self.routers[label]
            if router["history"]:
                self.history = label
            return router["command"](*args, **kwargs)

        return wrapper


    def register_rout(self, label, command, history=False):
        router = self.routers.setdefault(label, dict())
        router["command"] = command
        router["history"] = history


    def refresh_event(self, event):
        self.__call__("refresh")()
        if self.history:
            self.__call__(self.history)()
