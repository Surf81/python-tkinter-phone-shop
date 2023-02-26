from typing import *

class Router(object):
    def __init__(self, master):
        self.master = master
        self.routers = dict()

    def __call__(self, label) -> Callable:
        return self.routers.get(label)

    def register_rout(self, label, command):
        self.routers[label] = command